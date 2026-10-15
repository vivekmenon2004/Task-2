from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product
from banners.models import Banner

def home(request):
    """
    Homepage view with hero banner slider, categories showcase,
    featured products, and promotional banners.
    Excludes disabled products and disabled categories site-wide.
    """
    all_banners = list(Banner.objects.filter(is_active=True).order_by('order', '-created_at'))
    
    hero_banners = all_banners
    promo_banners = all_banners[3:] if len(all_banners) > 3 else []

    # Active categories only
    categories = Category.objects.filter(is_active=True).order_by('name')

    # Only active products in active categories
    featured_products = Product.objects.filter(
        is_active=True,
        category__is_active=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')[:8]
    
    has_content = bool(all_banners or featured_products.exists() or categories.exists())
    
    context = {
        'hero_banners': hero_banners,
        'promo_banners': promo_banners,
        'categories': categories,
        'featured_products': featured_products,
        'has_content': has_content,
    }
    return render(request, 'store/home.html', context)


def product_list(request, category_slug=None):
    """
    Product catalog list view supporting:
    - All active products in active categories
    - Category filtering via URL (/category/<slug>/) or query param (/products/?category=<slug>)
    - Search by product name (?q=...)
    - Pagination with query parameter preservation
    """
    categories = Category.objects.filter(is_active=True).order_by('name')
    category_slug_param = category_slug or request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()

    products_qs = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related('category').order_by('-created_at')

    selected_category = None
    if category_slug_param:
        selected_category = get_object_or_404(Category, slug=category_slug_param, is_active=True)
        products_qs = products_qs.filter(category=selected_category)

    if search_query:
        # Search by name (and optionally key specs for better UX)
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) | Q(key_specs__icontains=search_query)
        )

    # Pagination: 9 products per page (3x3 grid)
    paginator = Paginator(products_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve search and filter query parameters for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    base_query_string = query_params.urlencode()

    context = {
        'selected_category': selected_category,
        'categories': categories,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'base_query_string': base_query_string,
        'total_count': products_qs.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """
    Product detail page view.
    Returns 404 for inactive products or products in inactive categories.
    Fetches related active products from the same active category.
    """
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True,
        category__is_active=True
    )
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        category__is_active=True
    ).exclude(pk=product.pk).select_related('category')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)
