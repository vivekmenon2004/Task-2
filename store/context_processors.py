from .models import Category

def categories_processor(request):
    """
    Makes active categories available to all templates (e.g. for base navigation).
    """
    categories = Category.objects.filter(is_active=True).order_by('name')
    return {
        'nav_categories': categories
    }
