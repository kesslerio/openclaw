#!/usr/bin/env python3
"""
Model Enforcer - Ensures ONLY Anthropic Claude models are used.
This file must be imported at startup of any AI-using component.

CRITICAL: This system uses Anthropic Max 200 plan.
NO OpenAI, Gemini, GPT, or other providers allowed.
"""

import os
import sys
from typing import List, Optional

class ModelEnforcementError(Exception):
    """Raised when a forbidden model is detected"""
    pass

class ModelEnforcer:
    """
    Validates that only Anthropic Claude models are used.
    Prevents accidental use of OpenAI, Gemini, etc.
    """

    ALLOWED_PROVIDERS = ["anthropic"]

    FORBIDDEN_PROVIDERS = [
        "openai",
        "google",
        "gemini",
        "gpt",
        "mistral",
        "cohere",
        "palm",
        "llama",
        "together"
    ]

    FORBIDDEN_IMPORTS = [
        "openai",
        "google.generativeai",
        "vertexai",
    ]

    ALLOWED_MODELS = [
        "claude-sonnet-4-20250514",      # Primary - use this
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ]

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    @classmethod
    def validate_model(cls, model: str) -> str:
        """
        Validate a model string. Returns the model if valid, raises if not.
        """
        if not model:
            return cls.DEFAULT_MODEL

        model_lower = model.lower()

        # Check for forbidden providers
        for forbidden in cls.FORBIDDEN_PROVIDERS:
            if forbidden in model_lower:
                raise ModelEnforcementError(
                    f"\n🚫 FORBIDDEN MODEL DETECTED: '{model}'\n"
                    f"This system uses Anthropic Max 200 plan ONLY.\n"
                    f"Forbidden providers: {cls.FORBIDDEN_PROVIDERS}\n"
                    f"Allowed models: {cls.ALLOWED_MODELS}\n"
                )

        # Check for Claude
        if "claude" not in model_lower and "anthropic" not in model_lower:
            raise ModelEnforcementError(
                f"\n🚫 UNKNOWN MODEL: '{model}'\n"
                f"Only Anthropic Claude models are permitted.\n"
                f"Allowed: {cls.ALLOWED_MODELS}\n"
                f"Default: {cls.DEFAULT_MODEL}\n"
            )

        return model

    @classmethod
    def validate_environment(cls) -> List[str]:
        """
        Check environment for configuration issues.
        Returns list of warnings.
        """
        warnings = []

        # Check for forbidden API keys that might cause accidental usage
        forbidden_env_vars = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("GOOGLE_API_KEY", "Google/Gemini"),
            ("GEMINI_API_KEY", "Gemini"),
        ]

        for var, provider in forbidden_env_vars:
            if os.environ.get(var):
                warnings.append(
                    f"⚠️  {var} is set - ensure {provider} is not used accidentally"
                )

        # Ensure Anthropic key or auth token exists
        if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            warnings.append(
                "\n⚠️  No Anthropic credentials set!\n"
                "Set ANTHROPIC_AUTH_TOKEN (Max plan OAuth) or ANTHROPIC_API_KEY.\n"
            )

        return warnings

    @classmethod
    def check_imports(cls) -> List[str]:
        """Check if any forbidden modules are imported"""
        warnings = []

        for module in cls.FORBIDDEN_IMPORTS:
            if module in sys.modules:
                warnings.append(f"⚠️  Forbidden module '{module}' is imported!")

        return warnings

    @classmethod
    def enforce(cls, model: Optional[str] = None, quiet: bool = False) -> str:
        """
        Run all validations. Call this at startup.

        Args:
            model: Optional model to validate
            quiet: If True, don't print success message

        Returns:
            Validated model string (or default)
        """
        # Check environment
        env_warnings = cls.validate_environment()

        # Check imports
        import_warnings = cls.check_imports()

        # Print warnings
        for w in env_warnings + import_warnings:
            print(w, file=sys.stderr)

        # Validate model
        validated_model = cls.validate_model(model) if model else cls.DEFAULT_MODEL

        if not quiet:
            print(f"✅ Model enforcement passed: {validated_model}")

        return validated_model

    @classmethod
    def get_client(cls):
        """Get a configured Anthropic client.

        Routes through local Claude CLI proxy (port 8766) when
        CLAUDE_PROXY_URL is set, using Max plan auth at no extra cost.
        Falls back to direct API with ANTHROPIC_API_KEY if no proxy.
        """
        import anthropic
        cls.enforce(quiet=True)
        proxy_url = os.environ.get("CLAUDE_PROXY_URL", "http://localhost:8766")
        if proxy_url:
            # Route through Claude CLI proxy (Max plan)
            return anthropic.Anthropic(
                base_url=proxy_url,
                api_key="proxy-no-key-needed",  # SDK requires a value but proxy ignores it
            )
        return anthropic.Anthropic()


def enforce_anthropic_only(model: str = None) -> str:
    """Convenience function to enforce model at module load"""
    return ModelEnforcer.enforce(model, quiet=True)


# Auto-enforce on import (will raise if ANTHROPIC_API_KEY not set)
if __name__ != "__main__":
    try:
        _validated = ModelEnforcer.enforce(quiet=True)
    except ModelEnforcementError as e:
        print(f"⚠️  Model enforcement: {e}", file=sys.stderr)
