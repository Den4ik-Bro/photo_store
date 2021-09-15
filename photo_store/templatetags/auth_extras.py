from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    if Group.objects.filter(name=group_name).exists():
        return True
    return False


@register.filter()
def check_permission(user, permission):
    if user.user_permissions.filter(codename=permission).exists():
        return True
    return False