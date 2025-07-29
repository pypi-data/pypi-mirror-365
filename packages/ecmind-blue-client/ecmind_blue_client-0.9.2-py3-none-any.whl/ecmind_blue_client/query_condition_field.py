"""
QueryConditionField object
"""

from datetime import date, datetime
from typing import List, Optional, Union

from XmlElement import XmlElement

from ecmind_blue_client.const import QueryOperators, SpecialValues, SystemFields


class QueryConditionField:
    """Create a new QueryConditionField() object.

    Args:
        field (Union[str, SystemFields]): A internal name as string or a instance of SystemFields.
            Internal names beeing automatically checked against known system field names.
        values (str | int | float | date | datetime | None | SpecialValues |
            list[str | int | float | date | datetime | None | SpecialValues], optional):
            A list of literal values, None (interpretet as `<NULL />` value) or a SpecialValues instance for `<SpecialValues>`
        operator (QueryOperators, optional):
            QueryOperators instance, default = EQUAL. -- (Optional) QueryOperators instance, default = EQUAL.
        table (Optional[str], optional):
            Table internal name. If this is set, the a `<TableCondition>` is created using the field parameter as `<TableColumn>`,
            default = None.
    """

    def __init__(
        self,
        field: Union[str, SystemFields],
        values: (
            str | int | float | date | datetime | None | SpecialValues | list[str | int | float | date | datetime | None | SpecialValues]
        ),
        operator: QueryOperators = QueryOperators.EQUAL,
        table: Optional[str] = None,
    ):
        if not table and isinstance(field, SystemFields):
            self.internal_name = field.name
            self.system = True
        elif not table and field in [system_field.name for system_field in SystemFields]:
            self.internal_name = field
            self.system = True
        else:
            self.internal_name = field
            self.system = False

        self.query_operator = operator
        self.table_name = table
        self.values = values

    def __repr__(self) -> str:
        return (f"{self.table_name}:" if self.table_name else "") + f"{self.internal_name} {self.query_operator.value} {self.values}"

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""

        def values_to_xml_elements(self) -> List[XmlElement]:
            if self.values is None:
                return [XmlElement("NULL")]
            result = []
            for value in self.values if isinstance(self.values, list) else [self.values]:
                if value is None:
                    result.append(XmlElement("NULL"))
                elif isinstance(value, SpecialValues):
                    result.append(XmlElement("SpecialValue", t=value.value))
                elif isinstance(value, datetime):
                    result.append(XmlElement("Value", t=datetime.strftime(value, "%d.%m.%Y %H:%M:%S")))
                elif isinstance(value, date):
                    v_datetime = datetime.combine(value, datetime.min.time())
                    result.append(XmlElement("Value", t=datetime.strftime(v_datetime, "%d.%m.%Y")))
                else:
                    result.append(XmlElement("Value", t=str(value)))

            if len(result) == 0:
                return [XmlElement("NULL")]

            return result

        if self.table_name:
            xml = XmlElement(
                "TableCondition",
                {"internal_name": self.table_name},
                [
                    XmlElement(
                        "TableColumn",
                        {
                            "internal_name": self.internal_name,
                            "operator": self.query_operator.value,
                        },
                        values_to_xml_elements(self),
                    )
                ],
            )
        else:
            xml = XmlElement(
                "FieldCondition",
                {
                    "internal_name": self.internal_name,
                    "operator": self.query_operator.value,
                },
                values_to_xml_elements(self),
            )
            if self.system:
                xml.attributes["system"] = "1"

        return xml
