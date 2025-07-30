import javacoder.utils.converter as cv


def convert_class_fields_to_db_ddl_builder(table_name: str,*default_ddl_columns:tuple):
    ddl_template = "create table {} (\nddl_column_template\n);".format(table_name)

    def converter(class_fields: list):
        ddl_columns=['\t'.join(c) for c in default_ddl_columns]
        ddl_column_template = '''{}\tvarchar(128)\tdefault null'''
        for i in class_fields:
            ddl_columns.append(cv.camel_to_snake(ddl_column_template.format(i)))
        return ddl_template.replace('ddl_column_template', ',\n'.join(ddl_columns))

    return converter
