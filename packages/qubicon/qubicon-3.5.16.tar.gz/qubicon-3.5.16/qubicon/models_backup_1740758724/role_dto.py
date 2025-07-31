from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.role_dto_name import RoleDtoName
from qubicon.api.types import UNSET, Unset

T = TypeVar("T", bound="RoleDto")


@_attrs_define
class RoleDto:
    """
    Attributes:
        id (Union[Unset, int]):
        name (Union[Unset, RoleDtoName]):
    """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, RoleDtoName] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name: Union[Unset, str] = UNSET
        if not isinstance(self.name, Unset):
            name = self.name.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _name = d.pop("name", UNSET)
        name: Union[Unset, RoleDtoName]
        if isinstance(_name, Unset):
            name = UNSET
        else:
            name = RoleDtoName(_name)

        role_dto = cls(
            id=id,
            name=name,
        )

        role_dto.additional_properties = d
        return role_dto

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
