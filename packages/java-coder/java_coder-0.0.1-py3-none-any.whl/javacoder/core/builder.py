import javalang.parse
from javalang.parser import JavaSyntaxError
from javalang.tree import ReferenceType

from javacoder.core.operator import ClassOperator, InterfaceOperator, AbstractClassOperator
from javacoder.core.plugins import ProjectPlugin, AuthorPlugin


class ObjectBuilder:

    def __init__(self):
        self.operator = None

    def build(self):
        self.operator.format()
        return self.operator

    def document(self, document):
        self.operator.set_document(document)

    def annotation(self, annotation_name, **kwargs):
        self.operator.add_annotation(annotation_name, **kwargs)

    def imports(self, path, static=False, wildcard=False):
        self.operator.add_import(path, static=static, wildcard=wildcard)

    def project(self, project_path=None):
        if project_path:
            self.operator.add_plugin(ProjectPlugin(self.operator, project_path))

    def add_plugin(self, plugin):
        if plugin:
            self.operator.add_plugin(plugin)
            if hasattr(plugin, 'operator'):
                plugin.operator = self.operator

    def author(self, author='', email='', **kwargs):
        self.operator.add_plugin(AuthorPlugin(self.operator, author, email, **kwargs))

    def package(self, package_name):
        self.operator.set_package_name(package_name)


def parse_expression(expression):
    if type(expression) == str:
        try:
            return javalang.parse.parse_member_signature(expression)
        except JavaSyntaxError:
            pass
        try:
            return javalang.parse.parse_expression(expression)
        except JavaSyntaxError:
            pass
    return expression


class ClassBuilder(ObjectBuilder):
    def __init__(self, name):
        super().__init__()
        self.operator = ClassOperator(class_name=name)

    def field(self, field, value='', annotation='', **annotation_kwargs):
        self.operator.add_private_string(field, value)
        if len(annotation) > 0:
            self.operator.add_field_annotation(field, annotation, **annotation_kwargs)

    def extend(self, extend_class):
        self.operator.set_extend_class(extend_class)

    def add_fields_getter_and_setter(self):
        for field in self.operator.get_fields():
            self.operator.add_getter_and_setter(field.declarators[0].name)

    def implement(self, implement_class):
        self.operator.add_implement(implement_class)

    def constructor(self, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]

        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]

        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]
        self.operator.get_method_cursor().add_constructor(kwargs['modifiers'], kwargs['parameters'], kwargs['body'])

    def method(self, name, *body, **kwargs):
        if 'modifiers' not in kwargs.keys():
            kwargs['modifiers'] = ["public"]
        if 'return_type' not in kwargs.keys():
            kwargs['return_type'] = None
        elif type(kwargs['return_type']) == str:
            kwargs['return_type'] = ReferenceType(name=kwargs['return_type'])
        if 'parameters' not in kwargs.keys():
            kwargs['parameters'] = []
        else:
            kwargs['parameters'] = [parse_expression(e) for e in kwargs['parameters']]
        if not body or len(body) == 0:
            kwargs['body'] = []
        else:
            kwargs['body'] = [parse_expression(e) for e in body]

        self.operator.get_method_cursor().add_method(kwargs['modifiers'], kwargs['return_type'], name,
                                                     kwargs['parameters'], kwargs['body'])


class InterfaceBuilder(ObjectBuilder):
    def __init__(self, name):
        super(InterfaceBuilder, self).__init__()
        self.operator = InterfaceOperator(name=name)

    def method(self, name):
        self.operator.add_method(name)

    def extend(self, extend_interface, *template_class):
        self.operator.add_extend_interface(extend_interface, *template_class)


class EnumBuilder(ObjectBuilder):
    def __init__(self):
        super().__init__()


class AbstractClassBuilder(ClassBuilder):
    def __init__(self, name):
        super(ObjectBuilder, self).__init__()
        self.operator = AbstractClassOperator(class_name=name)
