from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_product_request_variants_item_config_attributes_item import (
        CreateProductRequestVariantsItemConfigAttributesItem,
    )
    from ..models.create_product_request_variants_item_custom_fields_item import (
        CreateProductRequestVariantsItemCustomFieldsItem,
    )


T = TypeVar("T", bound="CreateProductRequestVariantsItem")


@_attrs_define
class CreateProductRequestVariantsItem:
    """
    Attributes:
        sku (str):
        purchase_price (Union[None, Unset, float]):
        sales_price (Union[None, Unset, float]):
        config_attributes (Union[Unset, list['CreateProductRequestVariantsItemConfigAttributesItem']]):
        internal_barcode (Union[Unset, str]):
        registered_barcode (Union[Unset, str]):
        supplier_item_codes (Union[Unset, list[str]]):
        custom_fields (Union[Unset, list['CreateProductRequestVariantsItemCustomFieldsItem']]):
    """

    sku: str
    purchase_price: None | Unset | float = UNSET
    sales_price: None | Unset | float = UNSET
    config_attributes: (
        Unset | list["CreateProductRequestVariantsItemConfigAttributesItem"]
    ) = UNSET
    internal_barcode: Unset | str = UNSET
    registered_barcode: Unset | str = UNSET
    supplier_item_codes: Unset | list[str] = UNSET
    custom_fields: Unset | list["CreateProductRequestVariantsItemCustomFieldsItem"] = (
        UNSET
    )

    def to_dict(self) -> dict[str, Any]:
        sku = self.sku

        purchase_price: None | Unset | float
        if isinstance(self.purchase_price, Unset):
            purchase_price = UNSET
        else:
            purchase_price = self.purchase_price

        sales_price: None | Unset | float
        if isinstance(self.sales_price, Unset):
            sales_price = UNSET
        else:
            sales_price = self.sales_price

        config_attributes: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.config_attributes, Unset):
            config_attributes = []
            for config_attributes_item_data in self.config_attributes:
                config_attributes_item = config_attributes_item_data.to_dict()
                config_attributes.append(config_attributes_item)

        internal_barcode = self.internal_barcode

        registered_barcode = self.registered_barcode

        supplier_item_codes: Unset | list[str] = UNSET
        if not isinstance(self.supplier_item_codes, Unset):
            supplier_item_codes = self.supplier_item_codes

        custom_fields: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.custom_fields, Unset):
            custom_fields = []
            for custom_fields_item_data in self.custom_fields:
                custom_fields_item = custom_fields_item_data.to_dict()
                custom_fields.append(custom_fields_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "sku": sku,
            }
        )
        if purchase_price is not UNSET:
            field_dict["purchase_price"] = purchase_price
        if sales_price is not UNSET:
            field_dict["sales_price"] = sales_price
        if config_attributes is not UNSET:
            field_dict["config_attributes"] = config_attributes
        if internal_barcode is not UNSET:
            field_dict["internal_barcode"] = internal_barcode
        if registered_barcode is not UNSET:
            field_dict["registered_barcode"] = registered_barcode
        if supplier_item_codes is not UNSET:
            field_dict["supplier_item_codes"] = supplier_item_codes
        if custom_fields is not UNSET:
            field_dict["custom_fields"] = custom_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_product_request_variants_item_config_attributes_item import (
            CreateProductRequestVariantsItemConfigAttributesItem,
        )
        from ..models.create_product_request_variants_item_custom_fields_item import (
            CreateProductRequestVariantsItemCustomFieldsItem,
        )

        d = dict(src_dict)
        sku = d.pop("sku")

        def _parse_purchase_price(data: object) -> None | Unset | float:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | Unset | float, data)

        purchase_price = _parse_purchase_price(d.pop("purchase_price", UNSET))

        def _parse_sales_price(data: object) -> None | Unset | float:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | Unset | float, data)

        sales_price = _parse_sales_price(d.pop("sales_price", UNSET))

        config_attributes = []
        _config_attributes = d.pop("config_attributes", UNSET)
        for config_attributes_item_data in _config_attributes or []:
            config_attributes_item = (
                CreateProductRequestVariantsItemConfigAttributesItem.from_dict(
                    config_attributes_item_data
                )
            )

            config_attributes.append(config_attributes_item)

        internal_barcode = d.pop("internal_barcode", UNSET)

        registered_barcode = d.pop("registered_barcode", UNSET)

        supplier_item_codes = cast(list[str], d.pop("supplier_item_codes", UNSET))

        custom_fields = []
        _custom_fields = d.pop("custom_fields", UNSET)
        for custom_fields_item_data in _custom_fields or []:
            custom_fields_item = (
                CreateProductRequestVariantsItemCustomFieldsItem.from_dict(
                    custom_fields_item_data
                )
            )

            custom_fields.append(custom_fields_item)

        create_product_request_variants_item = cls(
            sku=sku,
            purchase_price=purchase_price,
            sales_price=sales_price,
            config_attributes=config_attributes,
            internal_barcode=internal_barcode,
            registered_barcode=registered_barcode,
            supplier_item_codes=supplier_item_codes,
            custom_fields=custom_fields,
        )

        return create_product_request_variants_item
