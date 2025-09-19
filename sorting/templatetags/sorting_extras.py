from django import template
from collections import defaultdict

register = template.Library()


@register.simple_tag
def get_categories_for_bag_type(queryset):
    """
    Group bag subtypes by category, ensuring each category appears only once.
    Returns a list of dictionaries with 'category' and 'subtypes' keys.
    """
    # Group subtypes by category
    category_groups = defaultdict(list)
    
    for subtype in queryset:
        category_groups[subtype.category].append(subtype)
    
    # Convert to list of dictionaries and sort by category order
    result = []
    for category, subtypes in category_groups.items():
        # Sort subtypes alphabetically within each category
        sorted_subtypes = sorted(subtypes, key=lambda x: x.name)
        
        result.append({
            'category': category,
            'subtypes': sorted_subtypes
        })
    
    # Sort categories by their order (if they have one) or by name
    result.sort(key=lambda x: (
        x['category'].order if x['category'] and hasattr(x['category'], 'order') else 999,
        x['category'].name if x['category'] else 'zzz'
    ))
    
    return result