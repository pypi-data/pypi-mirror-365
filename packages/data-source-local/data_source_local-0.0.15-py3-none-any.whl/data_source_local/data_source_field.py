from database_mysql_local.generic_mapping import GenericMapping

class DataSourceField(GenericMapping):
    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(
            default_schema_name="data_source_field",
            default_table_name="data_source_field_table",
            default_view_table_name="data_source_field_view",
            is_test_data = is_test_data)