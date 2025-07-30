import datetime
import os
import re

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from javacoder.core.operator import ClassOperator
from javacoder.utils.loader import get_git_config_property, load_content


class Plugin:
    def __init__(self, operator):
        self.operator = operator

    def invoke(self, **kwargs):
        invoke_method_name = 'invoke_' + kwargs['invoke_method']
        if hasattr(self, invoke_method_name):
            getattr(self, invoke_method_name)(**kwargs)


class ProjectPlugin(Plugin):
    def __init__(self, operator, project_path):
        super().__init__(operator)
        self.project_path = project_path
        self.packages = {}
        self.project_walker = ProjectWalker(project_path)
        self.project_walker.walk()
        self.new_project = len(self.project_walker.project_files) == 0
        self.project_pom = ET.ElementTree()
        self.project_pom_namespace = 'http://maven.apache.org/POM/4.0.0'
        if not self.new_project:
            source_path = os.path.join(project_path, 'src', 'main', 'java')
            for file, path in self.project_walker.peek():
                if file == 'pom.xml':
                    self.project_pom.parse(os.path.join(path, file))
                    self.project_pom_namespace = re.findall(r"^{(.+?)}.+$", self.project_pom.getroot().tag)[0]
                if file.endswith('.java'):
                    if file[:-5] not in self.packages:
                        self.packages[file[:-5]] = [path[len(source_path) + 1:].replace(os.sep, '.')]
                    else:
                        self.packages[file[:-5]].append(path[len(source_path) + 1:].replace(os.sep, '.'))

    def _create_project(self):
        if self.new_project:
            os.mkdir(os.path.join(self.project_path, 'src', 'main', 'java'))
            os.mkdir(os.path.join(self.project_path, 'src', 'main', 'resources'))
            with open(os.path.join(self.project_path, 'pom.xml'), 'w') as f:
                self.project_pom.write(f, encoding='utf-8')

    def get_project_dependencies(self):
        dependence_dict = {}
        if self.project_pom:
            dependencies = self.project_pom.getroot().find(self.get_project_pom_tag("dependencies"))
            properties = self.project_pom.getroot().find(self.get_project_pom_tag("properties"))
            properties_map = {}
            if properties and properties.iter():
                for i in properties.iter():
                    properties_map[i.tag[len(self.project_pom_namespace) + 2:]] = i.text
            if dependencies:
                for dependence in dependencies.findall(self.get_project_pom_tag("dependency")):
                    d = dependence.find(self.get_project_pom_tag("artifactId"))
                    if isinstance(d, ET.Element):
                        group_id = dependence.find(self.get_project_pom_tag("groupId")).text
                        version = '' if not isinstance(dependence.find(self.get_project_pom_tag("version")), ET.Element) \
                            else dependence.find(self.get_project_pom_tag("version")).text
                        dependence_dict[d.text] = {
                            'groupId': group_id,
                            'version': version if not re.match(r'\${.+?}', version) else
                            re.sub(r'\${.+?}', properties_map.get(re.findall(r'\${(.+?)}', version)[0]), version)
                        }
        return dependence_dict

    def get_project_pom_tag(self, tag_name):
        return '{' + self.project_pom_namespace + '}' + tag_name

    def fill_imports(self, class_name):
        if class_name:
            if class_name in self.packages:
                if len(self.packages[class_name]) == 1:
                    package_path = self.packages[class_name][0]
                else:
                    print("please select import class:")
                    for index, package in enumerate(self.packages[class_name]):
                        print(index, ": ", package)
                    select_one = int(input(">"))
                    package_path = self.packages[class_name][select_one]
                imported_class = self.operator.get_import()
                if package_path + '.' + class_name not in imported_class:
                    self.operator.add_import(package_path + '.' + class_name)

    def invoke_preview_class(self, **kwargs):
        self.check_class_package()
        referenced = self.get_operator_element_by_type('ReferenceType')
        for reference in referenced:
            self.fill_imports(reference.name)

    def invoke_save(self, **kwargs):
        self._create_project()
        self.check_class_package()
        referenced = self.get_operator_element_by_type('ReferenceType')
        for reference in referenced:
            self.fill_imports(reference.name)

    def get_operator_element_by_type(self, *element_type):
        elements = []
        result = set()
        elements.append(self.operator.class_tree)
        while len(elements) > 0:
            element = elements.pop()
            if type(element).__name__ in element_type:
                result.add(element)
            if element and hasattr(element, 'children'):
                for obj in element.children:
                    if obj and type(obj) != str:
                        if hasattr(obj, '__iter__') or hasattr(obj, '__getitem__'):
                            for o in obj:
                                elements.append(o)
                        else:
                            elements.append(obj)
        return result

    def check_class_package(self):
        if self.operator.class_tree.package:
            if not self.operator.file_path:
                self.operator.file_path = os.path.join(self.project_path, 'src', 'main', 'java',
                                                       str(self.operator.class_tree.package.name).replace('.', os.sep))
        else:
            if self.operator.file_path:
                self.operator.set_package_name_by_file_path(self.operator.file_path)


class AuthorPlugin(Plugin):
    def __init__(self, operator, username='', email='', **kwargs):
        super().__init__(operator)
        self.author_map = {
            "author": username if username != '' else get_git_config_property('user.name'),
            "email": email if email != '' else get_git_config_property('user.email')
        }
        for k, v in kwargs.items():
            self.author_map[k] = v

    def get_converted_author_info(self, key):
        return '@' + key + ' ' + self.author_map[key] + '\n'

    def invoke_preview_class(self, **kwargs):
        self.add_author_info()

    def invoke_save(self, **kwargs):
        self.add_author_info()

    def add_author_info(self):
        self.author_map['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.operator.class_cursor:
            author_info_document = ''
            if self.operator.class_cursor.documentation:
                for k in self.author_map.keys():
                    if '@' + k not in self.operator.class_cursor.documentation.documentation:
                        author_info_document = author_info_document + self.get_converted_author_info(k)
                document = author_info_document + self.operator.class_cursor.documentation.documentation
            else:
                document = '\n'.join([self.get_converted_author_info(k) for k in self.author_map.keys()])
            self.operator.set_document(document.strip('\n'))


class ProjectWalker:
    def __init__(self, project_path):
        self.project_path = project_path
        self.project_files = {}

    def walk(self):
        self.project_files.clear()
        if self.project_path and len(self.project_path) > 0:
            if os.path.exists(self.project_path) and os.path.isdir(self.project_path):
                for root, dirs, files in os.walk(self.project_path):
                    for file in files:
                        if file not in self.project_files:
                            self.project_files[file] = [root]
                        else:
                            self.project_files[file].append(root)

    def peek(self, fresh=True):
        if fresh:
            self.walk()
        for file, paths in self.project_files.items():
            for path in paths:
                yield file, path

    def peek_class_operator(self, fresh=True):
        if fresh:
            self.walk()
        for file, path in self.peek():
            op = convert_class_operator(file, path)
            if op:
                yield op

    def total_size(self, file_type=None):
        return sum([len(v) if file_type and k.endswith('.' + file_type) else 0 for k, v in self.project_files.items()])


def convert_class_operator(file, path):
    if file.endswith(".java"):
        try:
            return ClassOperator(class_path=os.path.join(path, file))
        except Exception as e:
            print("parse file - {} error info - {}".format(os.path.join(path, file), e))
    else:
        return None
