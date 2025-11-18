"""Password complexity validator for FitCoach.

This module provides comprehensive password validation to enforce strong password
policies and prevent common password-related security issues.

Security features:
- Minimum length requirement
- Character complexity requirements (uppercase, lowercase, digits, special chars)
- Common password detection
- Username/email similarity detection
- Comprehensive error messages
- Configurable requirements

References:
- OWASP Password Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- NIST Digital Identity Guidelines: https://pages.nist.gov/800-63-3/sp800-63b.html
"""

import logging
import re
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class PasswordValidationError(Exception):
    """Exception raised when password validation fails."""

    def __init__(self, message: str, errors: List[str]):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class PasswordValidator:
    """Validator for password complexity and security.

    Implements OWASP and NIST password guidelines to ensure strong passwords.

    Requirements:
    - Minimum length (default: 8)
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    - Not in common passwords list
    - Not similar to username/email

    Example:
        ```python
        validator = PasswordValidator()

        # Validate password
        is_valid, errors = validator.validate(
            password="MyP@ssw0rd123",
            username="john_doe",
            email="john@example.com"
        )

        if not is_valid:
            print(f"Password validation failed: {errors}")
        ```
    """

    # Common weak passwords (top 100 most common)
    # Source: https://github.com/danielmiessler/SecLists
    COMMON_PASSWORDS = {
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "password1", "123123", "1234567890", "000000", "qwerty", "abc123",
        "111111", "password123", "1q2w3e4r", "1234", "qwerty123", "million2",
        "1qaz2wsx", "123321", "654321", "666666", "987654321", "qwertyuiop",
        "123", "123123123", "password!", "welcome", "admin", "root", "master",
        "monkey", "dragon", "letmein", "login", "princess", "qazwsx",
        "solo", "passw0rd", "starwars", "welcome1", "hello", "freedom",
        "whatever", "trustno1", "jordan23", "harley", "robert", "matthew",
        "daniel", "andrew", "jordan", "hunter", "thomas", "michelle",
        "ashley", "jennifer", "joshua", "amanda", "justin", "jessica",
        "baseball", "football", "sunshine", "soccer", "superman", "batman",
        "michael", "shadow", "master", "jennifer", "111111", "2000", "jordan",
        "superman", "harley", "1234", "hunter", "fuckyou", "trustno1",
        "ranger", "buster", "thomas", "tigger", "robert", "soccer", "fuck",
        "batman", "test", "pass", "killer", "hockey", "george", "charlie",
        "andrew", "michelle", "love", "sunshine", "jessica", "asshole",
        "pepper", "daniel", "access", "123456789", "654321", "joshua",
    }

    # Minimum requirements
    DEFAULT_MIN_LENGTH = 8
    MIN_MIN_LENGTH = 6  # Absolute minimum
    MAX_LENGTH = 128

    # Special characters
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"

    def __init__(
        self,
        min_length: int = DEFAULT_MIN_LENGTH,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        check_common_passwords: bool = True,
        check_similarity: bool = True,
    ):
        """Initialize password validator.

        Args:
            min_length: Minimum password length (default: 8)
            require_uppercase: Require at least one uppercase letter (default: True)
            require_lowercase: Require at least one lowercase letter (default: True)
            require_digit: Require at least one digit (default: True)
            require_special: Require at least one special character (default: True)
            check_common_passwords: Check against common passwords (default: True)
            check_similarity: Check similarity to username/email (default: True)
        """
        self.min_length = max(min_length, self.MIN_MIN_LENGTH)
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.check_common_passwords = check_common_passwords
        self.check_similarity = check_similarity

    def _check_length(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check password length.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"

        if len(password) > self.MAX_LENGTH:
            return False, f"Password must be at most {self.MAX_LENGTH} characters long"

        return True, None

    def _check_uppercase(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check for uppercase letters.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.require_uppercase:
            return True, None

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        return True, None

    def _check_lowercase(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check for lowercase letters.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.require_lowercase:
            return True, None

        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        return True, None

    def _check_digit(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check for digits.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.require_digit:
            return True, None

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        return True, None

    def _check_special(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check for special characters.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.require_special:
            return True, None

        if not re.search(f"[{re.escape(self.SPECIAL_CHARS)}]", password):
            return False, f"Password must contain at least one special character ({self.SPECIAL_CHARS[:20]}...)"

        return True, None

    def _check_common_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """Check against common passwords list.

        Args:
            password: Password to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.check_common_passwords:
            return True, None

        # Check exact match (case-insensitive)
        if password.lower() in self.COMMON_PASSWORDS:
            logger.warning(f"Common password attempt detected")
            return False, "This password is too common. Please choose a more unique password"

        # Check for common patterns
        password_lower = password.lower()

        # Check if password is just a word followed by numbers
        if re.match(r"^[a-z]+\d+$", password_lower):
            word = re.match(r"^([a-z]+)\d+$", password_lower).group(1)
            if word in self.COMMON_PASSWORDS:
                return False, "This password pattern is too common. Please choose a more unique password"

        return True, None

    def _check_similarity(
        self,
        password: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Check if password is too similar to username or email.

        Args:
            password: Password to check
            username: Username to compare against
            email: Email to compare against

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.check_similarity:
            return True, None

        password_lower = password.lower()

        # Check username similarity
        if username:
            username_lower = username.lower()

            # Exact match
            if password_lower == username_lower:
                return False, "Password cannot be the same as username"

            # Password contains username
            if len(username_lower) >= 4 and username_lower in password_lower:
                return False, "Password cannot contain your username"

            # Username contains password (short passwords)
            if len(password_lower) >= 4 and password_lower in username_lower:
                return False, "Password is too similar to your username"

        # Check email similarity
        if email:
            email_lower = email.lower()
            email_local = email_lower.split("@")[0] if "@" in email_lower else email_lower

            # Exact match with email or local part
            if password_lower == email_lower or password_lower == email_local:
                return False, "Password cannot be the same as your email"

            # Password contains email local part
            if len(email_local) >= 4 and email_local in password_lower:
                return False, "Password cannot contain your email address"

        return True, None

    def validate(
        self,
        password: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate password against all requirements.

        Args:
            password: Password to validate
            username: Optional username for similarity check
            email: Optional email for similarity check

        Returns:
            Tuple of (is_valid, list_of_errors)
            - is_valid: True if password passes all checks
            - list_of_errors: List of error messages (empty if valid)

        Example:
            ```python
            validator = PasswordValidator()
            is_valid, errors = validator.validate(
                password="MyP@ssw0rd123",
                username="john_doe",
                email="john@example.com"
            )

            if not is_valid:
                for error in errors:
                    print(f"- {error}")
            ```
        """
        errors = []

        # Run all checks
        checks = [
            self._check_length(password),
            self._check_uppercase(password),
            self._check_lowercase(password),
            self._check_digit(password),
            self._check_special(password),
            self._check_common_password(password),
            self._check_similarity(password, username, email),
        ]

        for is_valid, error in checks:
            if not is_valid and error:
                errors.append(error)

        return len(errors) == 0, errors

    def validate_and_raise(
        self,
        password: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        """Validate password and raise exception if invalid.

        Args:
            password: Password to validate
            username: Optional username for similarity check
            email: Optional email for similarity check

        Raises:
            PasswordValidationError: If password is invalid
        """
        is_valid, errors = self.validate(password, username, email)

        if not is_valid:
            error_msg = "Password does not meet complexity requirements"
            logger.warning(
                f"Password validation failed for user {username or 'unknown'}. "
                f"Errors: {errors}"
            )
            raise PasswordValidationError(error_msg, errors)

    def get_requirements_text(self) -> str:
        """Get human-readable password requirements.

        Returns:
            String describing password requirements
        """
        requirements = [f"At least {self.min_length} characters long"]

        if self.require_uppercase:
            requirements.append("At least one uppercase letter")

        if self.require_lowercase:
            requirements.append("At least one lowercase letter")

        if self.require_digit:
            requirements.append("At least one digit")

        if self.require_special:
            requirements.append("At least one special character")

        if self.check_common_passwords:
            requirements.append("Must not be a common password")

        if self.check_similarity:
            requirements.append("Must not be similar to username or email")

        return "Password must meet the following requirements:\n- " + "\n- ".join(requirements)


# Global singleton instance
_default_validator: Optional[PasswordValidator] = None


def get_password_validator() -> PasswordValidator:
    """Get the default global password validator.

    Returns:
        PasswordValidator instance
    """
    global _default_validator
    if _default_validator is None:
        _default_validator = PasswordValidator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
            require_special=True,
            check_common_passwords=True,
            check_similarity=True,
        )
    return _default_validator


def validate_password(
    password: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
) -> Tuple[bool, List[str]]:
    """Validate password using the global validator.

    Convenience function for simple use cases.

    Args:
        password: Password to validate
        username: Optional username
        email: Optional email

    Returns:
        Tuple of (is_valid, errors)
    """
    validator = get_password_validator()
    return validator.validate(password, username, email)
