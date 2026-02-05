import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk";

const memoryCorePlugin = {
  id: "memory-core",
  name: "Memory (Core)",
  description: "File-backed memory search tools and CLI",
  kind: "memory",
  configSchema: emptyPluginConfigSchema(),
  register(api: OpenClawPluginApi) {
    api.registerTool(
      (ctx) => {
        const memorySearchTool = api.runtime.tools.createMemorySearchTool({
          config: ctx.config,
          agentSessionKey: ctx.sessionKey,
        });
        const memoryGetTool = api.runtime.tools.createMemoryGetTool({
          config: ctx.config,
          agentSessionKey: ctx.sessionKey,
        });
        const memoryGetChunksTool = api.runtime.tools.createMemoryGetChunksTool({
          config: ctx.config,
          agentSessionKey: ctx.sessionKey,
        });
        const memoryTimelineTool = api.runtime.tools.createMemoryTimelineTool({
          config: ctx.config,
          agentSessionKey: ctx.sessionKey,
        });
        if (!memorySearchTool || !memoryGetTool) {
          return null;
        }
        const tools = [memorySearchTool, memoryGetTool];
        if (memoryGetChunksTool) {
          tools.push(memoryGetChunksTool);
        }
        if (memoryTimelineTool) {
          tools.push(memoryTimelineTool);
        }
        return tools;
      },
      { names: ["memory_search", "memory_get", "memory_get_chunks", "memory_timeline"] },
    );

    api.registerCli(
      ({ program }) => {
        api.runtime.tools.registerMemoryCli(program);
      },
      { commands: ["memory"] },
    );
  },
};

export default memoryCorePlugin;
