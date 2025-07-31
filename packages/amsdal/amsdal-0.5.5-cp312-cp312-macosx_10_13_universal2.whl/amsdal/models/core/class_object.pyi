from amsdal.models.core.class_property import *
from amsdal.models.core.storage_metadata import *
from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class ClassObject(Model):
    __module_type__: ClassVar[ModuleType]
    title: str
    type: str
    module_type: str
    properties: dict[str, ClassProperty | None] | None
    required: list[str] | None
    custom_code: str | None
    storage_metadata: StorageMetadata | None
    @classmethod
    def _non_empty_keys_properties(cls, value: Any) -> Any: ...
    @property
    def display_name(self) -> str:
        """
        Returns the display name of the object.

        Returns:
            str: The display name, which is the title of the object.
        """
