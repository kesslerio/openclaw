import AppKit
import AVFoundation
import Dispatch
import OSLog
import Speech

/// Observes left Option and starts a dictation capture while it is held.
final class VoiceDictationHotkey: @unchecked Sendable {
    static let shared = VoiceDictationHotkey()

    private var globalMonitor: Any?
    private var localMonitor: Any?
    private var optionDown = false // left option only
    private var active = false

    private let beginAction: @Sendable () async -> Void
    private let endAction: @Sendable () async -> Void

    init(
        beginAction: @escaping @Sendable () async -> Void = { await VoiceDictation.shared.begin() },
        endAction: @escaping @Sendable () async -> Void = { await VoiceDictation.shared.end() })
    {
        self.beginAction = beginAction
        self.endAction = endAction
    }

    func setEnabled(_ enabled: Bool) {
        if ProcessInfo.processInfo.isRunningTests { return }
        self.withMainThread { [weak self] in
            guard let self else { return }
            if enabled {
                self.startMonitoring()
            } else {
                self.stopMonitoring()
            }
        }
    }

    private func startMonitoring() {
        guard self.globalMonitor == nil, self.localMonitor == nil else { return }
        self.globalMonitor = NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged) { [weak self] event in
            let keyCode = event.keyCode
            let flags = event.modifierFlags
            self?.handleFlagsChanged(keyCode: keyCode, modifierFlags: flags)
        }
        self.localMonitor = NSEvent.addLocalMonitorForEvents(matching: .flagsChanged) { [weak self] event in
            let keyCode = event.keyCode
            let flags = event.modifierFlags
            self?.handleFlagsChanged(keyCode: keyCode, modifierFlags: flags)
            return event
        }
    }

    private func stopMonitoring() {
        if let globalMonitor {
            NSEvent.removeMonitor(globalMonitor)
            self.globalMonitor = nil
        }
        if let localMonitor {
            NSEvent.removeMonitor(localMonitor)
            self.localMonitor = nil
        }
        self.optionDown = false
        self.active = false
    }

    private func handleFlagsChanged(keyCode: UInt16, modifierFlags: NSEvent.ModifierFlags) {
        self.withMainThread { [weak self] in
            self?.updateModifierState(keyCode: keyCode, modifierFlags: modifierFlags)
        }
    }

    private func withMainThread(_ block: @escaping @Sendable () -> Void) {
        DispatchQueue.main.async(execute: block)
    }

    private func updateModifierState(keyCode: UInt16, modifierFlags: NSEvent.ModifierFlags) {
        // Left Option (keyCode 58) acts as a hold-to-dictate modifier.
        if keyCode == 58 {
            self.optionDown = modifierFlags.contains(.option)
        }

        let chordActive = self.optionDown
        if chordActive, !self.active {
            self.active = true
            Task {
                Logger(subsystem: "ai.openclaw", category: "voice.dictation")
                    .info("dictation hotkey down")
                await self.beginAction()
            }
        } else if !chordActive, self.active {
            self.active = false
            Task {
                Logger(subsystem: "ai.openclaw", category: "voice.dictation")
                    .info("dictation hotkey up")
                await self.endAction()
            }
        }
    }

    func _testUpdateModifierState(keyCode: UInt16, modifierFlags: NSEvent.ModifierFlags) {
        self.updateModifierState(keyCode: keyCode, modifierFlags: modifierFlags)
    }
}

/// Short-lived speech recognizer that records while the hotkey is held and types the result.
actor VoiceDictation {
    static let shared = VoiceDictation()

    private let logger = Logger(subsystem: "ai.openclaw", category: "voice.dictation")

    private var recognizer: SFSpeechRecognizer?
    private var audioEngine: AVAudioEngine?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var tapInstalled = false

    private var sessionID = UUID()

    private var committed: String = ""
    private var volatile: String = ""
    private var activeConfig: Config?
    private var isCapturing = false
    private var finalized = false
    private var timeoutTask: Task<Void, Never>?
    private var overlayToken: UUID?

    private struct Config {
        let micID: String?
        let localeID: String?
    }

    func begin() async {
        guard voiceWakeSupported else { return }
        guard !self.isCapturing else { return }

        let sessionID = UUID()
        self.sessionID = sessionID

        let granted = await PermissionManager.ensureVoiceWakePermissions(interactive: true)
        guard granted else { return }

        let config = await MainActor.run { self.makeConfig() }
        self.activeConfig = config
        self.isCapturing = true
        self.finalized = false
        self.timeoutTask?.cancel(); self.timeoutTask = nil

        self.logger.info("dictation begin")
        await VoiceWakeRuntime.shared.pauseForPushToTalk()
        self.overlayToken = await MainActor.run {
            VoiceSessionCoordinator.shared.startSession(
                source: .dictation,
                text: "",
                forwardEnabled: false)
        }

        do {
            try await self.startRecognition(localeID: config.localeID, sessionID: sessionID)
        } catch {
            await MainActor.run {
                VoiceWakeOverlayController.shared.dismiss()
            }
            self.isCapturing = false
            await VoiceWakeRuntime.shared.applyPushToTalkCooldown()
            await VoiceWakeRuntime.shared.refresh(state: AppStateStore.shared)
        }
    }

    func end() async {
        guard self.isCapturing else { return }
        self.isCapturing = false
        let sessionID = self.sessionID

        if self.tapInstalled {
            self.audioEngine?.inputNode.removeTap(onBus: 0)
            self.tapInstalled = false
        }
        self.recognitionRequest?.endAudio()

        if self.committed.isEmpty, self.volatile.isEmpty {
            await self.finalize(transcriptOverride: "", reason: "emptyOnRelease", sessionID: sessionID)
            return
        }

        self.timeoutTask?.cancel()
        self.timeoutTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            await self?.finalize(transcriptOverride: nil, reason: "timeout", sessionID: sessionID)
        }
    }

    // MARK: - Private

    private func startRecognition(localeID: String?, sessionID: UUID) async throws {
        let locale = localeID.flatMap { Locale(identifier: $0) } ?? Locale(identifier: Locale.current.identifier)
        self.recognizer = SFSpeechRecognizer(locale: locale)
        guard let recognizer, recognizer.isAvailable else {
            throw NSError(
                domain: "VoiceDictation",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Recognizer unavailable"])
        }

        self.recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        self.recognitionRequest?.shouldReportPartialResults = true
        guard let request = self.recognitionRequest else { return }

        if self.audioEngine == nil {
            self.audioEngine = AVAudioEngine()
        }
        guard let audioEngine = self.audioEngine else { return }

        let input = audioEngine.inputNode
        let format = input.outputFormat(forBus: 0)
        if self.tapInstalled {
            input.removeTap(onBus: 0)
            self.tapInstalled = false
        }
        input.installTap(onBus: 0, bufferSize: 2048, format: format) { [weak request] buffer, _ in
            request?.append(buffer)
        }
        self.tapInstalled = true

        audioEngine.prepare()
        try audioEngine.start()

        self.recognitionTask = recognizer.recognitionTask(with: request) { [weak self] result, error in
            guard let self else { return }
            if let error {
                self.logger.debug("dictation error: \(error.localizedDescription, privacy: .public)")
            }
            let transcript = result?.bestTranscription.formattedString
            let isFinal = result?.isFinal ?? false
            Task.detached { [weak self, transcript, isFinal, sessionID] in
                guard let self else { return }
                await self.handle(transcript: transcript, isFinal: isFinal, sessionID: sessionID)
            }
        }
    }

    private func handle(transcript: String?, isFinal: Bool, sessionID: UUID) async {
        guard sessionID == self.sessionID else {
            self.logger.debug("dictation drop transcript for stale session")
            return
        }
        guard let transcript else { return }
        if isFinal {
            self.committed = transcript
            self.volatile = ""
        } else {
            self.volatile = Self.delta(after: self.committed, current: transcript)
        }

        let snapshot = Self.join(self.committed, self.volatile)
        let attributed = Self.makeAttributed(committed: self.committed, volatile: self.volatile, isFinal: isFinal)
        if let token = self.overlayToken {
            await MainActor.run {
                VoiceSessionCoordinator.shared.updatePartial(
                    token: token,
                    text: snapshot,
                    attributed: attributed)
            }
        }
    }

    private func finalize(transcriptOverride: String?, reason: String, sessionID: UUID?) async {
        if self.finalized { return }
        if let sessionID, sessionID != self.sessionID {
            self.logger.debug("dictation drop finalize for stale session")
            return
        }
        self.finalized = true
        self.isCapturing = false
        self.timeoutTask?.cancel(); self.timeoutTask = nil

        let finalText: String = {
            if let override = transcriptOverride?.trimmingCharacters(in: .whitespacesAndNewlines) {
                return override
            }
            return (self.committed + self.volatile).trimmingCharacters(in: .whitespacesAndNewlines)
        }()

        let token = self.overlayToken
        let logger = self.logger
        await MainActor.run {
            logger.info("dictation finalize reason=\(reason, privacy: .public) len=\(finalText.count, privacy: .public)")
            if finalText.isEmpty {
                if let token {
                    VoiceSessionCoordinator.shared.dismiss(token: token, reason: .explicit, outcome: .empty)
                }
            } else {
                TextInjector.type(finalText)
                if let token {
                    VoiceSessionCoordinator.shared.dismiss(token: token, reason: .explicit, outcome: .sent)
                }
            }
        }

        self.recognitionTask?.cancel()
        self.recognitionRequest = nil
        self.recognitionTask = nil
        if self.tapInstalled {
            self.audioEngine?.inputNode.removeTap(onBus: 0)
            self.tapInstalled = false
        }
        if self.audioEngine?.isRunning == true {
            self.audioEngine?.stop()
            self.audioEngine?.reset()
        }
        self.audioEngine = nil

        self.committed = ""
        self.volatile = ""
        self.activeConfig = nil
        self.overlayToken = nil

        await VoiceWakeRuntime.shared.applyPushToTalkCooldown()
        _ = await MainActor.run { Task { await VoiceWakeRuntime.shared.refresh(state: AppStateStore.shared) } }
    }

    @MainActor
    private func makeConfig() -> Config {
        let state = AppStateStore.shared
        return Config(
            micID: state.voiceWakeMicID.isEmpty ? nil : state.voiceWakeMicID,
            localeID: state.voiceWakeLocaleID)
    }

    private static func join(_ prefix: String, _ suffix: String) -> String {
        if prefix.isEmpty { return suffix }
        if suffix.isEmpty { return prefix }
        return "\(prefix) \(suffix)"
    }

    private static func delta(after committed: String, current: String) -> String {
        if current.hasPrefix(committed) {
            let start = current.index(current.startIndex, offsetBy: committed.count)
            return String(current[start...])
        }
        return current
    }

    private static func makeAttributed(committed: String, volatile: String, isFinal: Bool) -> NSAttributedString {
        let full = NSMutableAttributedString()
        let committedAttr: [NSAttributedString.Key: Any] = [
            .foregroundColor: NSColor.labelColor,
            .font: NSFont.systemFont(ofSize: 13, weight: .regular),
        ]
        full.append(NSAttributedString(string: committed, attributes: committedAttr))
        let volatileColor: NSColor = isFinal ? .labelColor : NSColor.tertiaryLabelColor
        let volatileAttr: [NSAttributedString.Key: Any] = [
            .foregroundColor: volatileColor,
            .font: NSFont.systemFont(ofSize: 13, weight: .regular),
        ]
        full.append(NSAttributedString(string: volatile, attributes: volatileAttr))
        return full
    }
}

@MainActor
enum TextInjector {
    private static let logger = Logger(subsystem: "ai.openclaw", category: "voice.dictation.inject")

    static func type(_ text: String) {
        let pasteboard = NSPasteboard.general
        let changeCount = pasteboard.changeCount

        // Save current clipboard contents
        let savedItems = pasteboard.pasteboardItems?.map { item -> [NSPasteboard.PasteboardType: Data] in
            var dict = [NSPasteboard.PasteboardType: Data]()
            for type in item.types {
                if let data = item.data(forType: type) {
                    dict[type] = data
                }
            }
            return dict
        }

        // Place dictated text on the clipboard
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)

        // Simulate Cmd+V to paste
        let source = CGEventSource(stateID: .hidSystemState)
        let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 9, keyDown: true)
        keyDown?.flags = .maskCommand
        keyDown?.post(tap: .cghidEventTap)

        let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 9, keyDown: false)
        keyUp?.flags = .maskCommand
        keyUp?.post(tap: .cghidEventTap)

        logger.info("dictation injected len=\(text.count, privacy: .public)")

        // Restore original clipboard after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            guard pasteboard.changeCount == changeCount + 1 else { return }
            guard let savedItems, !savedItems.isEmpty else { return }
            pasteboard.clearContents()
            for itemDict in savedItems {
                let item = NSPasteboardItem()
                for (type, data) in itemDict {
                    item.setData(data, forType: type)
                }
                pasteboard.writeObjects([item])
            }
        }
    }
}
