import re


def camel_to_snake(name):
    # convert camelFormat to snake_format
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def is_collection(collection):
    return hasattr(collection, '__iter__') and hasattr(collection, '__getitem__')
