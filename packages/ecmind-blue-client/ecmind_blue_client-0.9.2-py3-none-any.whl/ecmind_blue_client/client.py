"""
Abstract base class for TCPClient and TCPPoolClient
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterator, List, Literal, Optional, Union
from string import ascii_letters, digits

from XmlElement import XmlElement

from ecmind_blue_client import BlueException
from ecmind_blue_client.const import (
    FieldSchema,
    ImportActions,
    Jobs,
    MainTypeId,
    StoreInCacheByIdConversion,
    SystemFields,
)
from ecmind_blue_client.dms_result import DmsResult
from ecmind_blue_client.job import Job
from ecmind_blue_client.options import Options
from ecmind_blue_client.param import Param, ParamTypes
from ecmind_blue_client.query_condition_group import QueryConditionGroup
from ecmind_blue_client.query_result_field import QueryResultField
from ecmind_blue_client.request_file import RequestFile
from ecmind_blue_client.result import Result
from ecmind_blue_client.result_file import ResultFile

logger = logging.getLogger(__name__)

__all__ = ["Client"]


class Client(ABC):
    """Abstract base class for all client implementations."""

    @abstractmethod
    def execute(self, job: Job) -> Result:
        """Send a job to the blue server, execute it and return the response.

        Args:
            job (Job): A previously created Job() object.

        Returns:
            Result: The result of the job execution.
        """
        raise NotImplementedError

    def get_object_type_by_id(self, object_id: int) -> int:
        """Helper function: Execute the dms.GetObjectTypeByID job for a given object id and return the objects type id.

        Args:
            object_id (int): A folder, register or document id.

        Returns:
            int: The object type id for the given object id.
        """
        job = Job(Jobs.DMS_GETOBJECTTYPEBYID, Flags=0, ObjectID=object_id)
        return self.execute(job).values["ObjectType"]

    def store_in_cache(self, object_id: int, object_type_id: Optional[int] = None, checkout: Optional[bool] = False) -> List[ResultFile]:
        """Helper function: Execute the std.StoreInCache job for a given object to retrieve its files.

        Args:
            object_id (int): A document id.
            object_type_id (int, optional): The documents type id. When not provided, it is retrieve via get_object_type_by_id() first.
            checkout (bool, optional): When True, change the documents state to checked out on the server.


        Returns:
            List[ResultFile]: A list of ResultFile objects.

        ### Warning

        Known bug: Throws an enaio error on archived documents.
        """
        if object_type_id is None:
            object_type_id = self.get_object_type_by_id(object_id)

        job = Job(
            Jobs.STD_STOREINCACHE,
            Flags=1,
            dwObjectID=object_id,
            dwObjectType=object_type_id,
            DocState=(0 if checkout else 1),
            FileCount=0,
        )
        result = self.execute(job)
        if result.return_code != 0:
            raise RuntimeError(f"Received return code {result.return_code}: {result.error_message}")

        return result.files

    def store_in_cache_by_id(
        self,
        object_id: int,
        convert: StoreInCacheByIdConversion = StoreInCacheByIdConversion.NONE,
    ) -> List[ResultFile]:
        """Helper function: Execute the std.StoreInCacheById job for a given object to retrieve/convert its files.

        Args:
             object_id (int): A document id.
             convert (StoreInCacheByIdConversion, optional): (Optional) Convert
            - main type 1, 2, 3 or 4 to PDF with StoreInCacheByIdConversion.PDF
            - main type 2 or 3 with StoreInCacheByIdConversion.MULTIPAGE_TIFF

        Returns:
            List[ResultFile]: A list of ResultFile objects.
        """

        job = Job(
            Jobs.STD_STOREINCACHEBYID,
            Flags=1,
            dwObjectID=object_id,
            Convert=convert.value,
        )

        result = self.execute(job)
        if result.return_code != 0:
            raise RuntimeError(f"Received return code {result.return_code}: {result.error_message}")

        return result.files

    def xml_import(
        self,
        object_name: str,
        search_fields: Dict[str, str],
        import_fields: Dict[str, str],
        table_fields: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        folder_id: Optional[int] = None,
        register_id: Optional[int] = None,
        object_id: Optional[int] = None,
        options: Union[Options, str] = "",
        action0: ImportActions = ImportActions.INSERT,
        action1: ImportActions = ImportActions.UPDATE,
        actionM: ImportActions = ImportActions.ERROR,  # pylint: disable=invalid-name
        files: Optional[List[Union[RequestFile, str]]] = None,
        main_type: Union[MainTypeId, int, None] = None,
        variant_parent_id: Optional[int] = None,
        context_user: Optional[str] = None,
    ) -> DmsResult:
        """Helper function: Execute the dms.XMLImport job.

        Args:
            object_name (str): The internal name of the object type to import.
            search_fields (Dict[str, str]): Dict of internal field names and values.
                If one or more objects match all `search_fields`, the `action1` or `actionM` will be used, `action0` otherwise.
            import_fields (Dict[str, str]): Dict of internal field names and (new) values.
            table_fields (Dict[str, List[Dict[str, str]]], optional):
                Dict of internal table field names and list of new rows as dicts of internal column name and values.
            folder_id (int, optional): Folder id to import registers or documents into.
            register_id (int, optional): Register id to import sub-registers or documents into.
            object_id (int, optional): Objekt id to force an update of this element.
            options (str, optional): Semicolon separated string of import options.
            action0 (ImportActions, optional): `ImportActions` Enum element defining how to handle
                imports when the search_fields do not match any pre-existing objects.
            action1 (ImportActions, optional): `ImportActions` Enum element defining how to handle
                imports when the search_fields do match exactly one pre-existing object.
            actionM (ImportActions, optional): `ImportActions` Enum element defining how to handle
                imports when the search_fields do match more then one pre-existing object.
            files (List[str], optional): List of strings containing file path to import into a document object or RequestFile objects.
            main_type (int, optional): Set the main type id for document imports or leave empty for default value.
                Valid ids are `DOC_GRAYSCALE`/`1`, `DOC_BW`/`2`, DOC_COLOR`3`, `DOC_WINDOWS`/`4`,
                `DOC_MULTIMEDIA`/`5`, `DOC_MAIL`/`6`, `DOC_XML`/`7`, `DOC_CONTAINER`/`8`.
            variant_parent_id (int, optional): Set the parent id for document variant imports.
            search_fields (List[str], optional): must be empty when `variant_parent_id` is set.
            context_user (str, optional): string to change the job context to another user name.

        Returns:
            DmsResult: The result of the import operation.
        """

        object_element = XmlElement(
            "Object",
            s=[
                XmlElement("Search", s=[search_fields_element := XmlElement("Fields")]),
                import_fields_element := XmlElement("Fields"),
            ],
        )

        if main_type and isinstance(main_type, MainTypeId):
            object_element.set("maintype", str(main_type.value))
        elif main_type:
            object_element.set("maintype", str(main_type))

        if variant_parent_id:
            if len(search_fields) > 0:
                raise ValueError("search_fields must be empty when variant_parent_id is set.")
            search_fields = {SystemFields.OBJECT_ID.name: "-1"}
            object_element.set("variantparent_id", str(variant_parent_id))

        xml = XmlElement(
            "DMSData",
            s=[
                XmlElement(
                    "Archive",
                    s=[
                        XmlElement(
                            "ObjectType",
                            {"internal_name": object_name},
                            [object_element],
                        )
                    ],
                )
            ],
        )

        system_field_names = [item[0] for item in SystemFields.__members__.items()]

        if folder_id:
            object_element.set("folder_id", str(folder_id))

        if register_id:
            object_element.set("register_id", str(register_id))

        if object_id:
            object_element.set("object_id", str(object_id))

        for field_internal_name, field_value in search_fields.items():
            field = XmlElement("Field", a={"internal_name": field_internal_name}, t=field_value)
            if field_internal_name in system_field_names:
                field.set("system", "1")
            search_fields_element.append(field)

        for field_internal_name, field_value in import_fields.items():
            field = XmlElement("Field", a={"internal_name": field_internal_name}, t=field_value)
            if field_internal_name in system_field_names:
                field.set("system", "1")
            import_fields_element.append(field)

        if table_fields is not None and len(table_fields):
            object_element.append(table_fields_element := XmlElement("TableFields"))
            for table_field_internal_name, table_field_rows in table_fields.items():
                table_field = XmlElement("TableField", {"internal_name": table_field_internal_name})
                table_fields_element.append(table_field)
                for table_field_row in table_field_rows:
                    table_field.append(
                        XmlElement(
                            "Row",
                            s=[
                                XmlElement(
                                    "Field",
                                    {"internal_name": table_row_field_internal_name},
                                    t=table_row_field_value,
                                )
                                for table_row_field_internal_name, table_row_field_value in table_field_row.items()
                            ],
                        )
                    )

        job = Job(
            Jobs.DMS_XMLIMPORT,
            context_user=context_user,
            Flags=0,
            Options=str(options),
            Action0=action0.value,
            Action1=action1.value,
            ActionM=actionM.value,
            files=files,
            Encoding="UTF-8",
            XML=xml,
        )

        result: Result = self.execute(job)
        return DmsResult(**result.__dict__)

    def get_object_details(
        self,
        object_name: str,
        object_id: int,
        system_fields: Optional[List[SystemFields]] = None,
    ) -> dict:
        """
        This method returns the metadata of the object with the given ID and internal name.
        Implementation of the blue API job `dms.getObjectDetails`.
        Due to some bugs in the original method, the `dms.getResultList` method is used here.

        Args:
            object_name (str): The internal name of the object.
            object_id (int): The ID of the object.
            system_fields (List[SystemFields], optional): List of system fields to be included in the result.

        Returns:
            dict: A dictionary containing the metadata files.

        """

        query_fields = []
        for system_field in system_fields or []:
            query_field = XmlElement("Field", {"internal_name": system_field.name, "system": "1"})
            query_fields.append(query_field)

        query_xml = XmlElement(
            "DMSQuery",
            {},
            [
                XmlElement(
                    "Archive",
                    {},
                    [
                        XmlElement(
                            "ObjectType",
                            {"internal_name": object_name},
                            [
                                XmlElement("Fields", {"field_schema": FieldSchema.ALL.value}, query_fields),
                                XmlElement(
                                    "Conditions",
                                    {},
                                    [
                                        XmlElement(
                                            "ConditionObject",
                                            {"internal_name": object_name},
                                            [
                                                XmlElement(
                                                    "FieldCondition",
                                                    {
                                                        "internal_name": SystemFields.OBJECT_ID.name,
                                                        "operator": "=",
                                                        "system": "1",
                                                    },
                                                    [XmlElement("Value", t=str(object_id))],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        )

        job = Job(
            Jobs.DMS_GETRESULTLIST,
            Flags=0,
            Encoding="UTF-8",
            RequestType="HOL",
            XML=query_xml,
        )
        result = self.execute(job)
        if result.return_code != 0:
            raise RuntimeError(f"Received return code {result.return_code}: {result.error_message}")

        if result.values["Count"] == 0:
            return {}

        result_xml = XmlElement.from_string(result.values["XML"])
        obj_xml = result_xml["Archive"][0]["ObjectType"][0]["ObjectList"][0]["Object"][0]

        result = {}
        for field in obj_xml["Fields"][0]["Field"]:
            result[field.attributes["internal_name"]] = field.text

        table_fields = obj_xml.find("TableFields")
        if table_fields:
            for table_field in table_fields["TableField"]:
                table_field_result = []
                cols = [col.attributes["internal_name"] for col in table_field["Columns"][0]["Column"]]
                for row in table_field.findall("Row"):
                    row_result = {}
                    for i, col in enumerate(cols):
                        row_result[col] = row.subelements[i].text
                    table_field_result.append(row_result)

                result[table_field.attributes["internal_name"]] = table_field_result

        return result

    def execute_sql(self, sql_command: str, *params: int | str | float) -> Union[List[Dict[str, str]], None]:
        """Helper function: Execute a sql command via ADO.

        Args:
            sql_command (str): The sql command.

        Returns:
            list[dict[str, str]] | None:
                - For SELECT statements: `List[Dict]` -- The list of records with each row as dictionary of column name and string-value
                - For other statements: `None`
        """

        sql_command = parse_sqlstring(sql_command, *params)

        job = Job(Jobs.ADO_EXECUTESQL, Flags=0, Command=sql_command.strip())
        result = self.execute(job)
        if result.return_code != 0:
            raise BlueException(
                result.return_code,
                f"Job {Jobs.ADO_EXECUTESQL} failed with error code {result.return_code} and message {result.error_message}",
            )

        if result.files and len(result.files) > 0:
            file_bytes = result.files[0].bytes()
            if file_bytes is not None:
                xml_result = XmlElement.from_string(file_bytes.decode("UTF-8"))
                data = [row.attributes for row in xml_result["{urn:schemas-microsoft-com:rowset}data"][0]["{#RowsetSchema}row"]]
                return data
            else:
                return None
        else:
            return None

    def lol_query(
        self,
        object_name: str,
        conditions: Optional[Union[QueryConditionGroup, List[QueryConditionGroup]]] = None,
        result_fields: Union[
            str,
            SystemFields,
            QueryResultField,
            List[Union[str, SystemFields, QueryResultField]],
            None,
        ] = None,
        offset: int = 0,
        page_size: int = 1000,
        max_hits: Optional[int] = None,
        include_file_info: bool = False,
        follow_doc_links: bool = False,
        include_status: bool = False,
        garbage_mode: bool = False,
        context_user: Optional[str] = None,
        field_schema: Optional[Union[FieldSchema, Literal["DEF", "ALL"]]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Helper function: Page through dms.GetResultList in LOL format, yielding dicts of result fields for each hit.

        Args:
            object_name (str): The internal name of the object type to import.
            result_fields (Union[str, SystemFields, QueryResultField, List[Union[str, SystemFields, QueryResultField]], None], optional):
                List of internal field names, SystemField instances or QueryField instances (for sorting).
            offset (int, optional): defining the query offset, default = 0.
            page_size (int, optional):  defining the query page size, default = 1000.
            max_hits (int, optional): None limiting the querys maximum yield, default = None.
            include_file_info (boolean, optional):
                indicating, if file size, file extension and mime type should be added to document results, default = False.
            follow_doc_links (boolean, optional):
                bool indicating, the include_file_info returns the data of referenced files ("green arrows"), default = False.
            include_status (boolean, optional): indicating, if status field should be added to the result, default = False.
            garbage_mode (boolean, optional):
                indicating, if the query searches the recycle bin instead of non-deleted objects, default = False.
            context_user (str, optional): To change the job context to another user name.
            field_schema (Union[FieldSchema, Literal["DEF", "ALL"]], optional):
                Defines if the api will return all fields or only the the fields defined in `result_fields`.
                By default, only the defined fields will be return if `result_fields` is not empty resp. only the defined fields if
                `result_fields` is not empty. https://ecm.community/t/lol-query-systemfields-auch-mit-schema-all/375

        Returns:
            Iterator[Dict[str, Any]]: An iterator of dictionaries representing the query results fields. The key is the field internal name
        """

        if conditions:
            if not isinstance(conditions, list):
                conditions = [conditions]

            grouped_conditions: Dict[str, List[QueryConditionGroup]] = {}
            for condition in conditions:
                if not condition.internal_name in grouped_conditions:
                    grouped_conditions[condition.internal_name] = []
                grouped_conditions[condition.internal_name].append(condition)

            conditions_element = XmlElement("Conditions", {}, [])

            for internal_name, conditions_my_name in grouped_conditions.items():
                conditions_element.append(
                    XmlElement(
                        "ConditionObject",
                        {"internal_name": internal_name},
                        [x.to_xml_element() for x in conditions_my_name],
                    )
                )
        else:
            conditions_element = XmlElement("Conditions")

        if field_schema and isinstance(field_schema, str):
            field_schema = FieldSchema(field_schema)

        if result_fields is not None and (not isinstance(result_fields, list) or len(result_fields) > 0):
            fields_element = XmlElement("Fields", {"field_schema": FieldSchema.DEF.value if field_schema is None else field_schema.value})
            for result_field in result_fields if isinstance(result_fields, list) else [result_fields]:
                if isinstance(result_field, QueryResultField):
                    fields_element.append(result_field.to_xml_element())
                else:
                    fields_element.append(QueryResultField(result_field).to_xml_element())

        else:
            fields_element = XmlElement("Fields", {"field_schema": FieldSchema.ALL.value if field_schema is None else field_schema.value})

        query_xml = XmlElement(
            "DMSQuery",
            {},
            [
                XmlElement(
                    "Archive",
                    {},
                    [
                        XmlElement(
                            "ObjectType",
                            {"internal_name": object_name},
                            [fields_element, conditions_element],
                        )
                    ],
                )
            ],
        )

        job = Job(
            jobname=Jobs.DMS_GETRESULTLIST,
            context_user=context_user,
            Flags=0,
            Encoding="UTF-8",
            RequestType="LOL",
            XML=query_xml,
            MaxHits=max_hits,
            PageSize=page_size,
            Offset=offset,
            DateFormat="%Y-%m-%d",  # %z,
            FileInfo=1 if include_file_info else 0,
            FollowDocLink=1 if follow_doc_links else 0,
            Status=1 if include_status else 0,
            GarbageMode=1 if garbage_mode else 0,
        )

        current_offset = offset
        combined_count = 0
        columns = None
        tables = None
        while (not max_hits) or (combined_count <= max_hits):
            result = self.execute(job)
            if result.return_code != 0:
                raise RuntimeError(f"enaio error {result.return_code}: {result.error_message}")

            total_hits = result.values["TotalHits"]
            count = result.values["Count"]
            combined_count += count
            if total_hits == 0:
                logging.debug("Query returned no result objects. Finished.")
                return

            max_hits = total_hits if max_hits is None or max_hits > total_hits else max_hits

            archive = XmlElement.from_string(result.values["XML"])["Archive"][0]
            objecttype = archive["ObjectType"][0]
            rowset = objecttype["Rowset"][0]

            if not columns and not tables:
                columns = {column.attributes["internal_name"]: column.attributes["datatype"] for column in rowset["Columns"][0]["Column"]}
                tables = {
                    table.attributes["internal_name"]: {
                        column.attributes["internal_name"]: column.attributes["datatype"] for column in table["Columns"][0]["Column"]
                    }
                    for table in rowset["Columns"][0]["TableField"]
                }

            for row in rowset["Rows"][0]["Row"]:
                yield_result = {}
                # Add common fields form Archive and ObjectType tag
                yield_result["OBJECT_ID"] = int(row.attributes["id"])
                yield_result["OBJECT_FOLDER_TYPE_ID"] = int(archive.attributes["id"])
                yield_result["OBJECT_TYPE_ID"] = int(objecttype.attributes["id"])
                yield_result["OBJECT_MAINTYPE"] = int(objecttype.attributes["maintype"])
                yield_result["OBJECT_COTYPE"] = int(objecttype.attributes["cotype"])
                yield_result["OBJECT_INTERNAL_NAME"] = objecttype.attributes["internal_name"]
                yield_result["OBJECT_TYPE"] = objecttype.attributes["type"]
                yield_result["OBJECT_TABLE"] = objecttype.attributes["table"]

                if columns:
                    for name, value in zip(columns, row["Value"]):
                        datatype = columns[name]
                        if datatype == "TEXT":
                            # Value attribute of system fields or text value
                            yield_result[name] = value.attributes["value"] if "value" in value.attributes else value.text
                        elif datatype == "INTEGER":
                            # Text value of status fields or integer value of text value or None
                            yield_result[name] = value.text if "value" in value.attributes else int(value.text) if value.text else None
                        elif datatype == "DECIMAL":
                            yield_result[name] = float(value.text) if value.text else None
                        elif datatype == "DATE":
                            yield_result[name] = datetime.strptime(value.text, "%Y-%m-%d").date() if value.text else None
                        elif datatype == "DATETIME":
                            yield_result[name] = datetime.strptime(value.text, "%Y-%m-%d %H:%M:%S") if value.text else None
                        else:
                            yield_result[name] = value.text

                if tables:
                    for table_name, table_columns in tables.items():
                        table_result = []
                        for table_field in row["TableField"]:
                            if table_field.attributes["internal_name"] == table_name:
                                for table_row in table_field.findall("Row"):
                                    table_row_result = {}
                                    for name, value in zip(table_columns, table_row["Value"]):
                                        datatype = table_columns[name]
                                        if datatype == "TEXT":
                                            table_row_result[name] = (
                                                value.attributes["value"] if "value" in value.attributes else value.text
                                            )
                                        elif datatype == "INTEGER":
                                            table_row_result[name] = (
                                                value.text if "value" in value.attributes else int(value.text) if value.text else None
                                            )
                                        elif datatype == "DECIMAL":
                                            table_row_result[name] = float(value.text) if value.text else None
                                        elif datatype == "DATE":
                                            # it looks like enaio always delivers the DE format here
                                            table_row_result[name] = (
                                                datetime.strptime(value.text, "%d.%m.%Y").date() if value.text else None
                                            )
                                        else:
                                            table_row_result[name] = value.text
                                    table_result.append(table_row_result)
                                yield_result[table_name] = table_result

                yield yield_result

            if max_hits and (max_hits - combined_count <= 0):
                logging.debug("Max hits reached. Finished")
                return
            current_offset += count
            job.update(Param("Offset", ParamTypes.INTEGER, current_offset))
            logging.debug("Paging to next result frame with offset %s after %s combined hits.", current_offset, combined_count)


def parse_sqlstring(sql_command: str, *params: int | str | float) -> str:
    """
    Fill the placeholders in a prepared SQL string with given parameters

    For each placeholder there must be a matching parameter,
    with matching types. Allowed placeholders:

    - %d for decimal numbers, param must be a number (will be casted to int)
    - %f for floating point numbers, param must be a convertible to float
    - %s for any string. The param will be converted to str. It is
    recommended to not enclose %s parameters in quotation marks.
    - %w for a single word string with no whitespace allowed.
    - %u for an unquoted string (used if table- or field names are to be
    inserted from a variable). Only letters, digits, and _#$@ are allowed,
    no whitespace is allowed.

    A % character can be escaped by using a double %% char, e.g.
    sql_str="This is 30%% faster".
    If exactly one str, int or float value is to be inserted, a
    single value instead of an Iterable is accepted too.
    """

    tokens = sql_command.split("%")

    final_str = tokens[0]

    params_list = list(params)

    index_in_params = 0
    last_was_empty: bool = False

    for token in tokens[1:]:
        if last_was_empty:
            final_str += "%" + token
            last_was_empty = False
            continue
        if token == "":
            last_was_empty = True
        elif token.startswith("d"):
            try:
                number = int(params_list[index_in_params])
                index_in_params += 1
            except ValueError:
                raise ValueError(
                    r"Error during parsing of SQL string. Placeholder %d should have "
                    f"a matching int parameter, but {params_list[index_in_params]} "
                    "is not convertible to int"
                )
            final_str += f"{number}{token[1:]}"
        elif token.startswith("f"):
            try:
                number = float(params_list[index_in_params])
                index_in_params += 1
            except ValueError:
                raise ValueError(
                    r"Error during parsing of SQL string. Placeholder %f should have "
                    f"a matching parameter, but {params_list[index_in_params]} is not "
                    "convertible to float"
                )
            final_str += f"{number}{token[1:]}"
        elif token.startswith("w"):
            word = str(params_list[index_in_params])
            index_in_params += 1

            # check if this "word" is actually more than one word
            # check for comment markers as well since that's a
            # known way to inject
            forbidden_chars = [" ", "\t", "\n", "\r", "/*", "*/"]
            if any([forbidden_char in word for forbidden_char in forbidden_chars]):
                raise ValueError(
                    r"Error during parsing of SQL string. Placeholder %w can "
                    f"only be a single word. The value '{word}' is "
                    "not allowed."
                )

            # in SQL, quotation marks are escaped by doubling them
            word = word.replace("'", "''")
            word = word.replace('"', '""')

            # %s and %w markers don't need to be enclosed in quotation marks.
            # If the current doesn't end with a quotation marker, enclose
            # the inserted value in single quotes.
            if final_str.endswith("'") or final_str.endswith('"'):
                final_str += f"{word}{token[1:]}"
            else:
                final_str += f"'{word}'{token[1:]}"

        elif token.startswith("s"):
            value = str(params_list[index_in_params])
            index_in_params += 1

            # escape quotation marks
            value = value.replace("'", "''")
            value = value.replace('"', '""')

            # enclose in single-quotes if necessary
            if final_str.endswith("'") or final_str.endswith('"'):
                final_str += f"{value}{token[1:]}"
            else:
                final_str += f"'{value}'{token[1:]}"

        elif token.startswith("u"):
            value = str(params_list[index_in_params])
            index_in_params += 1

            # Here only characters valid in table- and field-names are allowed.
            # These are: Letters, digits, _, @, $, #.
            allowed_chars = list(ascii_letters)
            allowed_chars += list(digits)
            allowed_chars += ["_", "@", "$", "#"]

            for char in value:
                if not char in allowed_chars:
                    raise ValueError(r"In the placeholder %u in an SQL-string, only letters, digits, '_', '@', '$' and '#' are allowed.")
            final_str += value + token[1:]

        else:
            raise ValueError(
                r"Unrecognized placeholder in SQL-String. A '%' character must be part of a "
                r"placeholder for a value to be inserted. Allowed placeholders are: "
                r"%d for decimal numbers, %f for float, %s for strings, %w for words "
                r"(= strings without whitespace), %u for unquoted strings (used for table- "
                r"or fieldnames, only a-z, A-Z, 0-9, _, @, $ and # allowed, no whitespace allowed), "
                r" and %% for the '%' character."
            )

    if index_in_params != len(params_list):
        raise ValueError(
            f"Incorrect number of arguments in SQL-String. There were {index_in_params} "
            f"placeholders, but {len(params_list)} values given."
        )

    return final_str
