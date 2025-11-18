"""Prompt injection sanitizer for AI agents.

This module provides comprehensive protection against prompt injection attacks
by detecting and removing malicious patterns from user inputs before they reach
the LLM.

Security features:
- Detection of prompt injection patterns
- Removal of system prompt manipulation attempts
- Special token filtering
- Input length limiting
- Special character escaping
- Comprehensive logging of suspicious inputs

References:
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- Prompt Injection: https://simonwillison.net/2023/Apr/14/worst-that-can-happen/
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PromptInjectionDetected(Exception):
    """Exception raised when prompt injection is detected."""

    def __init__(self, message: str, pattern: str, matched_text: str):
        self.message = message
        self.pattern = pattern
        self.matched_text = matched_text
        super().__init__(self.message)


class PromptSanitizer:
    """Sanitizer for AI prompts to prevent prompt injection attacks.

    This class implements multiple layers of protection:
    1. Pattern-based detection of known injection techniques
    2. Special token filtering
    3. Length limiting
    4. Character escaping
    5. Logging and monitoring

    Example:
        ```python
        sanitizer = PromptSanitizer(max_length=2000, strict_mode=True)

        # Sanitize user input
        safe_input, warnings = sanitizer.sanitize("What's the weather?")

        # Check for threats
        is_safe, threats = sanitizer.is_safe("Ignore previous instructions")
        if not is_safe:
            print(f"Threats detected: {threats}")
        ```
    """

    # Dangerous patterns that indicate prompt injection attempts
    INJECTION_PATTERNS = [
        # Direct instruction manipulation
        r"ignore\s+(previous|above|all|prior)\s+(instructions?|prompts?|rules?|directives?)",
        r"disregard\s+(previous|above|all|prior)\s+(instructions?|prompts?|rules?)",
        r"forget\s+(previous|above|all|prior)\s+(instructions?|prompts?|rules?)",
        r"override\s+(previous|above|all|system)\s+(instructions?|prompts?|rules?)",

        # System prompt manipulation
        r"you\s+are\s+now\s+(a|an)\s+",
        r"new\s+instructions?:",
        r"system\s+prompt:",
        r"act\s+as\s+(if|though)\s+",
        r"pretend\s+(you|to)\s+",
        r"simulate\s+(being|a|an)\s+",
        r"roleplay\s+as\s+",

        # Instruction injection
        r"###\s*instructions?:",
        r"===\s*instructions?:",
        r"\[system\]",
        r"\[instructions?\]",
        r"\[new\s+role\]",

        # Escape attempts
        r"\\n\\nsystem:",
        r"<\|system\|>",
        r"<\|assistant\|>",
        r"<\|im_start\|>",
        r"<\|im_end\|>",

        # Data exfiltration attempts
        r"repeat\s+(your|the)\s+(instructions?|system\s+prompt)",
        r"(show|tell|reveal)\s+me\s+(your|the)\s+(instructions?|system\s+prompt)",
        r"what\s+(are|were)\s+your\s+(original\s+)?instructions?",

        # Jailbreak attempts
        r"DAN\s+mode",
        r"developer\s+mode",
        r"sudo\s+mode",
        r"god\s+mode",
        r"jailbreak",

        # Code execution attempts
        r"```python.*eval\(",
        r"```python.*exec\(",
        r"```python.*__import__",
        r"os\.system\(",
        r"subprocess\.",
    ]

    # Special tokens used by various LLMs that should be filtered
    SPECIAL_TOKENS = [
        "<|system|>",
        "<|user|>",
        "<|assistant|>",
        "<|im_start|>",
        "<|im_end|>",
        "<|endoftext|>",
        "[INST]",
        "[/INST]",
        "<<SYS>>",
        "<</SYS>>",
        "<s>",
        "</s>",
        "<|>",
        "###",  # When used as separator
    ]

    # Maximum allowed lengths
    DEFAULT_MAX_LENGTH = 2000
    ABSOLUTE_MAX_LENGTH = 5000

    def __init__(
        self,
        max_length: int = DEFAULT_MAX_LENGTH,
        strict_mode: bool = False,
        log_suspicious: bool = True,
    ):
        """Initialize prompt sanitizer.

        Args:
            max_length: Maximum allowed input length (default: 2000)
            strict_mode: If True, raise exception on detected threats (default: False)
            log_suspicious: If True, log suspicious patterns (default: True)
        """
        self.max_length = min(max_length, self.ABSOLUTE_MAX_LENGTH)
        self.strict_mode = strict_mode
        self.log_suspicious = log_suspicious

        # Compile regex patterns for performance
        self.compiled_patterns = [
            (pattern, re.compile(pattern, re.IGNORECASE | re.MULTILINE))
            for pattern in self.INJECTION_PATTERNS
        ]

    def is_safe(self, text: str) -> Tuple[bool, List[str]]:
        """Check if text contains prompt injection patterns.

        Args:
            text: Input text to check

        Returns:
            Tuple of (is_safe, list_of_threats)
            - is_safe: True if no threats detected
            - list_of_threats: List of detected threat descriptions
        """
        if not text:
            return True, []

        threats = []

        # Check for injection patterns
        for pattern_str, pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                threat_desc = f"Injection pattern detected: {pattern_str}"
                threats.append(threat_desc)

                if self.log_suspicious:
                    logger.warning(
                        f"Prompt injection detected - Pattern: {pattern_str}, "
                        f"Matches: {matches}"
                    )

        # Check for special tokens
        for token in self.SPECIAL_TOKENS:
            if token.lower() in text.lower():
                threat_desc = f"Special token detected: {token}"
                threats.append(threat_desc)

                if self.log_suspicious:
                    logger.warning(f"Special token detected: {token}")

        return len(threats) == 0, threats

    def remove_special_tokens(self, text: str) -> str:
        """Remove special LLM tokens from text.

        Args:
            text: Input text

        Returns:
            Text with special tokens removed
        """
        result = text
        for token in self.SPECIAL_TOKENS:
            # Case-insensitive replacement
            result = re.sub(
                re.escape(token),
                "",
                result,
                flags=re.IGNORECASE
            )
        return result

    def truncate(self, text: str) -> str:
        """Truncate text to maximum allowed length.

        Args:
            text: Input text

        Returns:
            Truncated text (if necessary)
        """
        if len(text) <= self.max_length:
            return text

        if self.log_suspicious:
            logger.warning(
                f"Input truncated from {len(text)} to {self.max_length} chars"
            )

        return text[:self.max_length]

    def escape_dangerous_chars(self, text: str) -> str:
        """Escape potentially dangerous characters.

        This is a light touch - we don't want to break normal text,
        just reduce the risk of injection.

        Args:
            text: Input text

        Returns:
            Text with escaped characters
        """
        # Remove null bytes and control characters (except common whitespace)
        result = "".join(
            char for char in text
            if char.isprintable() or char in ['\n', '\t', '\r', ' ']
        )

        # Normalize excessive whitespace (common in injection attempts)
        result = re.sub(r'\s{4,}', '   ', result)  # Max 3 consecutive spaces
        result = re.sub(r'\n{4,}', '\n\n\n', result)  # Max 3 newlines

        return result

    def sanitize(
        self,
        text: str,
        user_id: Optional[int] = None,
    ) -> Tuple[str, List[str]]:
        """Sanitize user input to prevent prompt injection.

        This is the main method that applies all sanitization steps:
        1. Check for threats
        2. Remove special tokens
        3. Escape dangerous characters
        4. Truncate to max length

        Args:
            text: User input to sanitize
            user_id: Optional user ID for logging

        Returns:
            Tuple of (sanitized_text, warnings)
            - sanitized_text: Cleaned and safe text
            - warnings: List of warnings about what was sanitized

        Raises:
            PromptInjectionDetected: If strict_mode=True and threats detected
        """
        if not text:
            return "", []

        warnings = []
        original_length = len(text)

        # Step 1: Check for injection patterns
        is_safe, threats = self.is_safe(text)

        if not is_safe:
            warnings.extend(threats)

            # Log security event
            logger.warning(
                f"Prompt injection attempt detected. "
                f"User: {user_id or 'unknown'}, "
                f"Threats: {threats}, "
                f"Original text: {text[:100]}..."
            )

            if self.strict_mode:
                raise PromptInjectionDetected(
                    "Prompt injection detected",
                    pattern=threats[0] if threats else "unknown",
                    matched_text=text[:100]
                )

        # Step 2: Remove special tokens
        text = self.remove_special_tokens(text)

        # Step 3: Escape dangerous characters
        text = self.escape_dangerous_chars(text)

        # Step 4: Truncate if needed
        if len(text) > self.max_length:
            text = self.truncate(text)
            warnings.append(
                f"Input truncated from {original_length} to {self.max_length} chars"
            )

        # Final safety check
        if len(warnings) > 0 and self.log_suspicious:
            logger.info(
                f"Input sanitized for user {user_id or 'unknown'}. "
                f"Warnings: {warnings}"
            )

        return text, warnings

    def sanitize_dict(
        self,
        data: Dict[str, any],
        fields: List[str],
        user_id: Optional[int] = None,
    ) -> Tuple[Dict[str, any], Dict[str, List[str]]]:
        """Sanitize multiple fields in a dictionary.

        Useful for sanitizing request data with multiple text fields.

        Args:
            data: Dictionary containing fields to sanitize
            fields: List of field names to sanitize
            user_id: Optional user ID for logging

        Returns:
            Tuple of (sanitized_data, warnings_dict)
            - sanitized_data: Dictionary with sanitized values
            - warnings_dict: Dictionary mapping field names to warnings

        Example:
            ```python
            data = {"message": "Hello", "question": "What's the weather?"}
            sanitized, warnings = sanitizer.sanitize_dict(
                data,
                fields=["message", "question"],
                user_id=123
            )
            ```
        """
        result = data.copy()
        all_warnings = {}

        for field in fields:
            if field in data and isinstance(data[field], str):
                sanitized, warnings = self.sanitize(data[field], user_id)
                result[field] = sanitized
                if warnings:
                    all_warnings[field] = warnings

        return result, all_warnings


# Global singleton instance (can be configured at startup)
_default_sanitizer: Optional[PromptSanitizer] = None


def get_sanitizer() -> PromptSanitizer:
    """Get the default global sanitizer instance.

    Returns:
        Global PromptSanitizer instance
    """
    global _default_sanitizer
    if _default_sanitizer is None:
        _default_sanitizer = PromptSanitizer(
            max_length=2000,
            strict_mode=False,
            log_suspicious=True,
        )
    return _default_sanitizer


def sanitize_prompt(text: str, user_id: Optional[int] = None) -> str:
    """Quick sanitization using the global sanitizer.

    Convenience function for simple use cases.

    Args:
        text: Text to sanitize
        user_id: Optional user ID for logging

    Returns:
        Sanitized text

    Example:
        ```python
        from app.agents.prompt_sanitizer import sanitize_prompt

        safe_input = sanitize_prompt(user_input, user_id=123)
        ```
    """
    sanitizer = get_sanitizer()
    sanitized, _ = sanitizer.sanitize(text, user_id)
    return sanitized
