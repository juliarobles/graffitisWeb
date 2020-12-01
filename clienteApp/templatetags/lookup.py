from django import template

register = template.Library()

#https://stackoverflow.com/questions/8948430/get-list-item-dynamically-in-django-templates
@register.filter(name="lookup")
def _lookup(d, key):
    return d[key]