from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from store.models import Product, Category
from banners.models import Banner
from .forms import ProductForm, CategoryForm, BannerForm, UserCreateForm, UserEditForm

User = get_user_model()


def is_staff_user(user):
    """Check if the user is logged in and has staff privileges."""
    return user.is_authenticated and user.is_staff


# ==============================================================================
# Overview
# ==============================================================================

@user_passes_test(is_staff_user, login_url='accounts:login')
def dashboard_home(request):
    """
    Store Operations Dashboard overview with stats, quick actions,
    and recent activity tables.
    """
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    disabled_products = Product.objects.filter(is_active=False).count()

    total_categories = Category.objects.count()

    total_banners = Banner.objects.count()
    active_banners = Banner.objects.filter(is_active=True).count()
    disabled_banners = Banner.objects.filter(is_active=False).count()

    total_users = User.objects.count()
    staff_users_count = User.objects.filter(is_staff=True).count()
    customer_users_count = User.objects.filter(is_staff=False).count()

    recent_products = Product.objects.select_related('category').order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'disabled_products': disabled_products,
        'total_categories': total_categories,
        'total_banners': total_banners,
        'active_banners': active_banners,
        'disabled_banners': disabled_banners,
        'total_users': total_users,
        'staff_users_count': staff_users_count,
        'customer_users_count': customer_users_count,
        'recent_products': recent_products,
        'recent_users': recent_users,
        'current_tab': 'overview',
    }
    return render(request, 'dashboard/index.html', context)


# ==============================================================================
# Products Management
# ==============================================================================

@user_passes_test(is_staff_user, login_url='accounts:login')
def product_list(request):
    """List and search all products inside the dashboard."""
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    status_filter = request.GET.get('status', '').strip()

    products = Product.objects.select_related('category').order_by('-created_at')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(key_specs__icontains=query) |
            Q(slug__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'disabled':
        products = products.filter(is_active=False)
    elif status_filter == 'featured':
        products = products.filter(is_featured=True)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'selected_status': status_filter,
        'total_count': Product.objects.count(),
        'filtered_count': products.count(),
        'current_tab': 'products',
    }
    return render(request, 'dashboard/product_list.html', context)


@user_passes_test(is_staff_user, login_url='accounts:login')
def product_create(request):
    """Add a new product directly from the dashboard."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('dashboard:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': 'Add New Product',
        'subtitle': 'Add a new hardware device or accessory to your storefront catalog.',
        'back_url': 'dashboard:product_list',
        'current_tab': 'products',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def product_edit(request, pk):
    """Edit an existing product directly from the dashboard."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('dashboard:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': f'Edit Product: {product.name}',
        'subtitle': 'Update pricing, images, specifications, or visibility.',
        'instance': product,
        'back_url': 'dashboard:product_list',
        'delete_url': 'dashboard:product_delete',
        'current_tab': 'products',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def product_delete(request, pk):
    """Delete a product directly from the dashboard."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" has been deleted.')
        return redirect('dashboard:product_list')

    return render(request, 'dashboard/confirm_delete.html', {
        'object_name': product.name,
        'model_name': 'Product',
        'back_url': 'dashboard:product_list',
        'current_tab': 'products',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def product_toggle_status(request, pk):
    """Quickly toggle active/featured status."""
    product = get_object_or_404(Product, pk=pk)
    field = request.GET.get('field', 'is_active')
    if field == 'is_featured':
        product.is_featured = not product.is_featured
        product.save()
        status_text = "featured" if product.is_featured else "unfeatured"
        messages.success(request, f'Product "{product.name}" marked as {status_text}.')
    else:
        product.is_active = not product.is_active
        product.save()
        status_text = "active" if product.is_active else "disabled"
        messages.success(request, f'Product "{product.name}" marked as {status_text}.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:product_list'))


# ==============================================================================
# Categories Management
# ==============================================================================

@user_passes_test(is_staff_user, login_url='accounts:login')
def category_list(request):
    """List and manage all categories directly inside the dashboard."""
    query = request.GET.get('q', '').strip()
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')

    if query:
        categories = categories.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(slug__icontains=query)
        )

    return render(request, 'dashboard/category_list.html', {
        'categories': categories,
        'query': query,
        'total_count': Category.objects.count(),
        'current_tab': 'categories',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def category_create(request):
    """Add a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('dashboard:category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': 'Add New Category',
        'subtitle': 'Create a new collection to categorize your store items.',
        'back_url': 'dashboard:category_list',
        'current_tab': 'categories',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def category_edit(request, pk):
    """Edit a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('dashboard:category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': f'Edit Category: {category.name}',
        'subtitle': 'Update category details and storefront visibility.',
        'instance': category,
        'back_url': 'dashboard:category_list',
        'delete_url': 'dashboard:category_delete',
        'current_tab': 'categories',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def category_delete(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" and associated references removed.')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/confirm_delete.html', {
        'object_name': category.name,
        'model_name': 'Category',
        'warning_text': 'Deleting this category may affect products linked to it.',
        'back_url': 'dashboard:category_list',
        'current_tab': 'categories',
    })


# ==============================================================================
# Banners Management
# ==============================================================================

@user_passes_test(is_staff_user, login_url='accounts:login')
def banner_list(request):
    """List and manage all hero banners."""
    banners = Banner.objects.all().order_by('order', '-created_at')
    return render(request, 'dashboard/banner_list.html', {
        'banners': banners,
        'total_count': banners.count(),
        'current_tab': 'banners',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def banner_create(request):
    """Add a new hero promotional banner."""
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f'Banner "{banner.title}" added to carousel.')
            return redirect('dashboard:banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BannerForm()

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': 'Add Hero Banner',
        'subtitle': 'Create high-impact showcase slides for the homepage hero carousel.',
        'back_url': 'dashboard:banner_list',
        'current_tab': 'banners',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def banner_edit(request, pk):
    """Edit a banner."""
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, f'Banner "{banner.title}" updated successfully.')
            return redirect('dashboard:banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BannerForm(instance=banner)

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': f'Edit Banner: {banner.title}',
        'subtitle': 'Adjust headline, promotional image, destination button, or slide order.',
        'instance': banner,
        'back_url': 'dashboard:banner_list',
        'delete_url': 'dashboard:banner_delete',
        'current_tab': 'banners',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def banner_delete(request, pk):
    """Delete a banner."""
    banner = get_object_or_404(Banner, pk=pk)
    if request.method == 'POST':
        title = banner.title
        banner.delete()
        messages.success(request, f'Banner "{title}" removed from carousel.')
        return redirect('dashboard:banner_list')

    return render(request, 'dashboard/confirm_delete.html', {
        'object_name': banner.title,
        'model_name': 'Banner',
        'back_url': 'dashboard:banner_list',
        'current_tab': 'banners',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def banner_toggle_status(request, pk):
    """Quickly toggle banner active status."""
    banner = get_object_or_404(Banner, pk=pk)
    banner.is_active = not banner.is_active
    banner.save()
    status_text = "active" if banner.is_active else "disabled"
    messages.success(request, f'Banner "{banner.title}" is now {status_text}.')
    return redirect('dashboard:banner_list')


# ==============================================================================
# Users Management
# ==============================================================================

@user_passes_test(is_staff_user, login_url='accounts:login')
def user_list(request):
    """List and manage all registered users."""
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()

    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    if role_filter == 'staff':
        users = users.filter(is_staff=True)
    elif role_filter == 'customer':
        users = users.filter(is_staff=False)
    elif role_filter == 'superuser':
        users = users.filter(is_superuser=True)

    return render(request, 'dashboard/user_list.html', {
        'users': users,
        'query': query,
        'selected_role': role_filter,
        'total_count': User.objects.count(),
        'filtered_count': users.count(),
        'current_tab': 'users',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def user_create(request):
    """Create a new user account directly from dashboard."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f'User account "{new_user.username}" created successfully.')
            return redirect('dashboard:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreateForm()

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': 'Create New User',
        'subtitle': 'Provision a new customer or staff member account.',
        'back_url': 'dashboard:user_list',
        'current_tab': 'users',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def user_edit(request, pk):
    """Edit user details and roles."""
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account "{target_user.username}" updated successfully.')
            return redirect('dashboard:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserEditForm(instance=target_user)

    return render(request, 'dashboard/form.html', {
        'form': form,
        'title': f'Edit User: {target_user.username}',
        'subtitle': 'Update user profile, administrative privileges, or reset password.',
        'instance': target_user,
        'back_url': 'dashboard:user_list',
        'delete_url': 'dashboard:user_delete' if target_user != request.user else None,
        'current_tab': 'users',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def user_delete(request, pk):
    """Delete a user account."""
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, "You cannot delete your own active staff account.")
        return redirect('dashboard:user_list')

    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User account "{username}" has been deleted.')
        return redirect('dashboard:user_list')

    return render(request, 'dashboard/confirm_delete.html', {
        'object_name': target_user.username,
        'model_name': 'User Account',
        'warning_text': 'All data associated with this user will be removed.',
        'back_url': 'dashboard:user_list',
        'current_tab': 'users',
    })


@user_passes_test(is_staff_user, login_url='accounts:login')
def user_toggle_status(request, pk):
    """Quickly toggle user active or staff status."""
    target_user = get_object_or_404(User, pk=pk)
    field = request.GET.get('field', 'is_active')

    if target_user == request.user and field in ('is_staff', 'is_active'):
        messages.error(request, "You cannot alter your own staff or active status.")
        return redirect('dashboard:user_list')

    if field == 'is_staff':
        target_user.is_staff = not target_user.is_staff
        target_user.save()
        status_text = "Staff Admin" if target_user.is_staff else "Customer"
        messages.success(request, f'User "{target_user.username}" role updated to {status_text}.')
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status_text = "active" if target_user.is_active else "inactive"
        messages.success(request, f'User "{target_user.username}" is now {status_text}.')

    return redirect('dashboard:user_list')
