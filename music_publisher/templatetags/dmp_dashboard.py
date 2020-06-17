"""Filters used in DMP dashboard.

"""

from django import template
from collections import OrderedDict

register = template.Library()


def yield_sections(model_dict, sections):
    for name, object_names in sections.items():
        models = []
        for object_name in object_names:
            if object_name in model_dict:
                models.append(model_dict[object_name])
                del model_dict[object_name]
        if models:
            yield {
                'name': name,
                'models': models}


@register.filter(name='dmp_model_groups')
def dmp_model_groups(model_list):
    """Return groups of models."""
    model_dict = OrderedDict([(el['object_name'], el) for el in model_list])
    sections = {
        'Musical Works': [
            'Work', 'Publisher', 'Writer', 'CWRExport', 'ACKImport',
            'DataImport', 'RoyaltyCalculation'],
        'Recordings': ['Recording', 'Artist', 'Label'],
        'Releases': [
            'CommercialRelease', 'LibraryRelease', 'Library']
    }
    # Works
    yield from yield_sections(model_dict, sections)
