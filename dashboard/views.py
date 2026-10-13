from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from store.models import Product, Category
from banners.models import Banner

@staff_member_required
def dashboard_home(request):
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    total_banners = Banner.objects.count()
    recent_products = Product.objects.select_related('category').order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_categories': total_categories,
        'total_banners': total_banners,
        'recent_products': recent_products,
    }
    return render(request, 'dashboard/index.html', context)
