class FilesystemError(Exception):
    """Base exception for filesystem operations."""
    pass

class PathNotFoundError(FilesystemError):
    """Raised when a path is not found."""
    pass

class FileNotFoundError(FilesystemError):
    """Raised when a file is not found."""
    pass

class FileAlreadyExistsError(FilesystemError):
    """Raised when trying to create a file that already exists."""
    pass

class VersionConflictError(FilesystemError):
    """Raised when there's a version conflict during update."""
    pass

class AuthenticationError(FilesystemError):
    """Raised when authentication fails."""
    pass