# gateway/templatetags/theme_filters.py
from django import template

register = template.Library()

@register.filter
def filter_by_bucket(themes, bucket_code):
    """Filter themes by bucket"""
    if not themes:
        return []
    return [theme for theme in themes if theme.bucket == bucket_code]