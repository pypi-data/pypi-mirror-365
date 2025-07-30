class ShpritsException(Exception):
    """Base exception for the Shprits framework."""

    pass


class DependencyNotFoundError(ShpritsException):
    """Raised when a dependency cannot be found."""

    def __init__(self, dependency_type: type) -> None:
        self.dependency_type: type = dependency_type
        super().__init__(f"Dependency of type '{dependency_type.__name__}' not found.")


class InvalidProviderError(ShpritsException):
    """Raised when a provider is defined incorrectly."""

    pass


__all__ = ["ShpritsException", "DependencyNotFoundError", "InvalidProviderError"]
