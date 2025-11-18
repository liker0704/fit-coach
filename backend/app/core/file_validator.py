"""File upload security validator for FitCoach.

This module provides comprehensive security validation for uploaded files to prevent:
1. Malicious file uploads (executable files, scripts)
2. Path traversal attacks
3. File type spoofing (magic bytes validation)
4. Oversized uploads (DoS prevention)
5. Malware uploads (optional ClamAV integration)

Security features:
- Magic bytes validation (not just MIME type)
- Filename sanitization and path traversal protection
- File size limits
- Extension whitelist
- Optional virus scanning
- Comprehensive logging

References:
- OWASP File Upload Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
"""

import imghdr
import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)


class FileValidationError(Exception):
    """Exception raised when file validation fails."""

    def __init__(self, message: str, field: str = "file"):
        self.message = message
        self.field = field
        super().__init__(self.message)


class FileValidator:
    """Validator for uploaded files with security checks.

    This class implements multiple layers of file upload security:
    1. Extension whitelist validation
    2. Magic bytes validation (actual file type)
    3. Filename sanitization
    4. Path traversal prevention
    5. Size limit enforcement
    6. Optional virus scanning

    Example:
        ```python
        validator = FileValidator(
            allowed_extensions={".jpg", ".png", ".jpeg"},
            max_size_mb=10,
            check_magic_bytes=True
        )

        # Validate uploaded file
        is_valid, error = await validator.validate(uploaded_file)
        if not is_valid:
            raise HTTPException(400, detail=error)

        # Sanitize filename
        safe_name = validator.sanitize_filename(uploaded_file.filename)
        ```
    """

    # Image magic bytes (file signatures)
    # Format: {extension: [possible_magic_bytes]}
    IMAGE_MAGIC_BYTES = {
        "jpg": [
            b"\xff\xd8\xff\xe0",  # JPEG (JFIF)
            b"\xff\xd8\xff\xe1",  # JPEG (Exif)
            b"\xff\xd8\xff\xe2",  # JPEG (Canon)
            b"\xff\xd8\xff\xe3",  # JPEG (Samsung)
            b"\xff\xd8\xff\xe8",  # JPEG (SPIFF)
        ],
        "jpeg": [
            b"\xff\xd8\xff\xe0",
            b"\xff\xd8\xff\xe1",
            b"\xff\xd8\xff\xe2",
            b"\xff\xd8\xff\xe3",
            b"\xff\xd8\xff\xe8",
        ],
        "png": [b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"],  # PNG
        "gif": [b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61"],  # GIF87a, GIF89a
        "bmp": [b"\x42\x4d"],  # BMP
        "webp": [b"\x52\x49\x46\x46"],  # WEBP (RIFF)
    }

    # Default allowed extensions for images
    DEFAULT_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Maximum file sizes (in MB)
    DEFAULT_MAX_SIZE_MB = 10
    ABSOLUTE_MAX_SIZE_MB = 50

    def __init__(
        self,
        allowed_extensions: Optional[set] = None,
        max_size_mb: int = DEFAULT_MAX_SIZE_MB,
        check_magic_bytes: bool = True,
        scan_viruses: bool = False,
    ):
        """Initialize file validator.

        Args:
            allowed_extensions: Set of allowed file extensions (e.g., {'.jpg', '.png'})
            max_size_mb: Maximum file size in MB (default: 10)
            check_magic_bytes: Whether to validate actual file type (default: True)
            scan_viruses: Whether to scan for viruses with ClamAV (default: False)
        """
        self.allowed_extensions = allowed_extensions or self.DEFAULT_IMAGE_EXTENSIONS
        self.max_size_mb = min(max_size_mb, self.ABSOLUTE_MAX_SIZE_MB)
        self.max_size_bytes = self.max_size_mb * 1024 * 1024
        self.check_magic_bytes = check_magic_bytes
        self.scan_viruses = scan_viruses

        # Normalize extensions to lowercase with dot
        self.allowed_extensions = {
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in self.allowed_extensions
        }

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues.

        Removes:
        - Path traversal attempts (../, ..\, etc.)
        - Null bytes
        - Control characters
        - Special characters that could cause issues

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for storage

        Example:
            ```python
            # Malicious filename
            bad = "../../../etc/passwd"
            safe = validator.sanitize_filename(bad)  # "passwd"

            # Filename with null bytes
            bad = "file\x00.jpg.exe"
            safe = validator.sanitize_filename(bad)  # "file.jpg.exe"
            ```
        """
        if not filename:
            return "unnamed_file"

        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Get just the filename (remove any path components)
        filename = os.path.basename(filename)

        # Remove or replace dangerous characters
        # Keep only alphanumeric, dots, hyphens, underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Remove leading dots (hidden files) and hyphens
        filename = filename.lstrip('.-')

        # Prevent multiple consecutive dots (could be path traversal attempt)
        filename = re.sub(r'\.{2,}', '.', filename)

        # Ensure filename is not empty after sanitization
        if not filename or filename == '.':
            return "unnamed_file"

        # Limit length (filesystem limits, typically 255 bytes)
        max_length = 200  # Leave room for prefixes
        if len(filename) > max_length:
            # Preserve extension if possible
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext

        return filename

    def validate_extension(self, filename: str) -> Tuple[bool, Optional[str]]:
        """Validate file extension against whitelist.

        Args:
            filename: Filename to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is empty"

        # Get extension
        _, ext = os.path.splitext(filename.lower())

        if not ext:
            return False, "File has no extension"

        if ext not in self.allowed_extensions:
            allowed_str = ", ".join(sorted(self.allowed_extensions))
            return False, f"File type '{ext}' not allowed. Allowed types: {allowed_str}"

        return True, None

    async def validate_magic_bytes(
        self, file: UploadFile
    ) -> Tuple[bool, Optional[str]]:
        """Validate file type by checking magic bytes (file signature).

        This prevents file type spoofing where a user renames a malicious file
        (e.g., virus.exe -> virus.jpg).

        Args:
            file: Uploaded file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Read first 12 bytes (enough for most image formats)
            file.file.seek(0)
            header = await file.read(12)
            file.file.seek(0)  # Reset for later use

            if not header:
                return False, "File is empty"

            # Get expected extension
            _, ext = os.path.splitext(file.filename.lower())
            ext = ext.lstrip(".")

            # Check if extension is in our magic bytes dict
            if ext not in self.IMAGE_MAGIC_BYTES:
                # Extension not in our list, use imghdr as fallback
                file.file.seek(0)
                detected_type = imghdr.what(file.file)
                file.file.seek(0)

                if detected_type is None:
                    return False, f"File does not appear to be a valid image"

                if f".{detected_type}" not in self.allowed_extensions:
                    return False, f"File type mismatch. Expected {ext}, detected {detected_type}"

                return True, None

            # Check magic bytes
            expected_signatures = self.IMAGE_MAGIC_BYTES[ext]
            matches = any(
                header.startswith(signature)
                for signature in expected_signatures
            )

            if not matches:
                # Try to detect actual type
                file.file.seek(0)
                detected_type = imghdr.what(file.file)
                file.file.seek(0)

                if detected_type:
                    return False, (
                        f"File type mismatch. Filename suggests '{ext}' but file "
                        f"appears to be '{detected_type}'. Possible file spoofing attempt."
                    )
                else:
                    return False, (
                        f"File does not match expected format for '{ext}'. "
                        f"Possible file corruption or spoofing attempt."
                    )

            return True, None

        except Exception as e:
            logger.error(f"Error validating magic bytes: {e}")
            return False, f"Error validating file type: {str(e)}"

    def validate_size(self, file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate file size.

        Args:
            file_size: Size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size <= 0:
            return False, "File is empty"

        if file_size > self.max_size_bytes:
            return False, (
                f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds "
                f"maximum allowed size ({self.max_size_mb}MB)"
            )

        return True, None

    def validate_content_type(
        self, content_type: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """Validate MIME content type.

        Note: This is just a preliminary check. Content-Type headers can be
        spoofed, so we still rely on magic bytes validation.

        Args:
            content_type: MIME type from request

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content_type:
            return False, "Content-Type header missing"

        if not content_type.startswith("image/"):
            return False, f"Content-Type '{content_type}' is not an image type"

        return True, None

    async def scan_for_viruses(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Scan file for viruses using ClamAV.

        Requires ClamAV to be installed and clamd running.

        Args:
            file_path: Path to file to scan

        Returns:
            Tuple of (is_safe, error_message)
        """
        if not self.scan_viruses:
            return True, None

        try:
            import pyclamd

            # Connect to ClamAV daemon
            cd = pyclamd.ClamdUnixSocket()

            # Check if ClamAV is available
            if not cd.ping():
                logger.warning("ClamAV daemon not available, skipping virus scan")
                return True, None

            # Scan file
            scan_result = cd.scan_file(str(file_path))

            if scan_result is None:
                # File is clean
                return True, None
            else:
                # Virus detected
                virus_name = scan_result.get(str(file_path), ["Unknown"])[1]
                logger.warning(
                    f"Virus detected in uploaded file: {virus_name} at {file_path}"
                )
                return False, f"File rejected: malware detected ({virus_name})"

        except ImportError:
            logger.warning(
                "pyclamd not installed, skipping virus scan. "
                "Install with: pip install pyclamd"
            )
            return True, None

        except Exception as e:
            logger.error(f"Error during virus scan: {e}")
            # Fail open - don't block upload if scanner fails
            return True, None

    async def validate(
        self, file: UploadFile, check_content: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """Perform complete validation of uploaded file.

        This is the main method that runs all security checks.

        Args:
            file: Uploaded file
            check_content: Whether to check file content (magic bytes)

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            ```python
            validator = FileValidator()
            is_valid, error = await validator.validate(uploaded_file)

            if not is_valid:
                raise HTTPException(400, detail=error)
            ```
        """
        # 1. Validate filename
        if not file.filename:
            return False, "Filename is missing"

        # 2. Sanitize filename (for logging)
        safe_filename = self.sanitize_filename(file.filename)
        logger.info(f"Validating file upload: {safe_filename}")

        # 3. Validate extension
        is_valid, error = self.validate_extension(file.filename)
        if not is_valid:
            logger.warning(f"Extension validation failed: {error}")
            return False, error

        # 4. Validate content type
        is_valid, error = self.validate_content_type(file.content_type)
        if not is_valid:
            logger.warning(f"Content-Type validation failed: {error}")
            return False, error

        # 5. Get and validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        is_valid, error = self.validate_size(file_size)
        if not is_valid:
            logger.warning(f"Size validation failed: {error}")
            return False, error

        # 6. Validate magic bytes (actual file type)
        if check_content and self.check_magic_bytes:
            is_valid, error = await self.validate_magic_bytes(file)
            if not is_valid:
                logger.warning(f"Magic bytes validation failed: {error}")
                return False, error

        logger.info(f"File validation successful: {safe_filename}")
        return True, None

    async def validate_and_raise(
        self, file: UploadFile, check_content: bool = True
    ) -> str:
        """Validate file and raise HTTPException if invalid.

        Convenience method that validates and raises exception on failure.

        Args:
            file: Uploaded file
            check_content: Whether to check file content

        Returns:
            Sanitized filename

        Raises:
            HTTPException: 400 if validation fails
        """
        is_valid, error = await self.validate(file, check_content)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "File validation failed"
            )

        return self.sanitize_filename(file.filename)


# Global singleton for image uploads
_image_validator: Optional[FileValidator] = None


def get_image_validator() -> FileValidator:
    """Get the global image file validator.

    Returns:
        FileValidator instance configured for images
    """
    global _image_validator
    if _image_validator is None:
        _image_validator = FileValidator(
            allowed_extensions={".jpg", ".jpeg", ".png", ".webp"},
            max_size_mb=10,
            check_magic_bytes=True,
            scan_viruses=False,  # Enable if ClamAV is installed
        )
    return _image_validator


async def validate_image_upload(file: UploadFile) -> str:
    """Validate image upload with default settings.

    Convenience function for image validation.

    Args:
        file: Uploaded file

    Returns:
        Sanitized filename

    Raises:
        HTTPException: 400 if validation fails
    """
    validator = get_image_validator()
    return await validator.validate_and_raise(file)
