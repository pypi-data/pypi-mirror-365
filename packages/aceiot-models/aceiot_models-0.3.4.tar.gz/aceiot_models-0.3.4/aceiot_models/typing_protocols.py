"""Protocol types for dynamic models to improve type checking."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HasID(Protocol):
    """Protocol for models that have an ID attribute."""

    id: int


@runtime_checkable
class HasName(Protocol):
    """Protocol for models that have a name attribute."""

    name: str


@runtime_checkable
class HasNiceName(Protocol):
    """Protocol for models that have a nice_name attribute."""

    nice_name: str | None


@runtime_checkable
class HasIDAndName(HasID, HasName, Protocol):
    """Protocol for models that have both ID and name attributes."""


@runtime_checkable
class EntityProtocol(HasID, HasName, Protocol):
    """Protocol for entity models with common attributes."""

    nice_name: str | None

    def get_display_name(self) -> str:
        """Get display name for the entity."""
        ...


@runtime_checkable
class BulkOperationProtocol(Protocol):
    """Protocol for models that support bulk operations."""

    @classmethod
    def validate_bulk(cls, items: list[dict[str, Any]]) -> list[Any]:
        """Validate multiple items at once."""
        ...


@runtime_checkable
class ReferenceModelProtocol(HasID, HasName, Protocol):
    """Protocol for reference models used in relationships."""


@runtime_checkable
class CRUDModelProtocol(Protocol):
    """Protocol for models created by ModelFactory with CRUD operations."""

    # Common fields that all CRUD models should have
    id: int | None
    name: str | None

    def to_reference(self) -> ReferenceModelProtocol:
        """Convert to reference model."""
        ...
