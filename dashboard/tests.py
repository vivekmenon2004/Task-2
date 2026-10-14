from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from store.models import Category, Product
from banners.models import Banner

User = get_user_model()


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@example.com',
            password='Password123!',
            is_staff=True
        )
        self.customer_user = User.objects.create_user(
            username='regularcustomer',
            email='customer@example.com',
            password='Password123!',
            is_staff=False
        )
        self.category = Category.objects.create(name='MacBook', description='Laptops')
        self.active_product = Product.objects.create(
            name='MacBook Pro 16',
            price=249900.00,
            category=self.category,
            is_active=True
        )
        self.disabled_product = Product.objects.create(
            name='MacBook Air M1 (Discontinued)',
            price=79900.00,
            category=self.category,
            is_active=False
        )
        self.banner = Banner.objects.create(
            title='Pro Beyond',
            subtitle='MacBook Pro with M3 Max',
            is_active=True
        )

    def test_staff_login_redirects_to_dashboard_by_default(self):
        """When staff/admin user logs in without ?next, they should land on /dashboard/ by default."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'staffadmin',
            'password': 'Password123!',
        })
        self.assertRedirects(response, reverse('dashboard:home'))

    def test_customer_login_redirects_to_profile_by_default(self):
        """When non-staff customer logs in, they should redirect to profile by default."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'regularcustomer',
            'password': 'Password123!',
        })
        self.assertRedirects(response, reverse('accounts:profile'))

    def test_anonymous_user_redirected_to_login(self):
        """Anonymous users must be redirected to the login page."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertIn('next=/dashboard/', response.url)

    def test_non_staff_user_redirected_to_login(self):
        """Authenticated users without staff privileges must be redirected to login."""
        self.client.login(username='regularcustomer', password='Password123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertIn('next=/dashboard/', response.url)

    def test_staff_user_can_access_dashboard(self):
        """Staff users can access the dashboard with status 200 OK."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')

    def test_header_dashboard_link_visibility(self):
        """Header should display the dashboard link only for staff users."""
        # Anonymous user
        anon_response = self.client.get(reverse('store:home'))
        self.assertNotContains(anon_response, '/dashboard/')

        # Non-staff customer
        self.client.login(username='regularcustomer', password='Password123!')
        cust_response = self.client.get(reverse('store:home'))
        self.assertNotContains(cust_response, '/dashboard/')
        self.client.logout()

        # Staff user
        self.client.login(username='staffadmin', password='Password123!')
        staff_response = self.client.get(reverse('store:home'))
        self.assertContains(staff_response, '/dashboard/')

    def test_stat_cards_and_counts_accuracy(self):
        """Dashboard must show accurate real-time statistics from the database."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['total_products'], 2)
        self.assertEqual(response.context['active_products'], 1)
        self.assertEqual(response.context['disabled_products'], 1)
        self.assertEqual(response.context['total_categories'], 1)
        self.assertEqual(response.context['total_banners'], 1)
        self.assertEqual(response.context['active_banners'], 1)
        self.assertEqual(response.context['disabled_banners'], 0)
        self.assertEqual(response.context['total_users'], 2)

    def test_dashboard_internal_action_links(self):
        """Quick action buttons and links should navigate to dashboard internal pages."""
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

        # Internal dashboard links
        self.assertContains(response, reverse('dashboard:product_create'))
        self.assertContains(response, reverse('dashboard:category_create'))
        self.assertContains(response, reverse('dashboard:banner_create'))
        self.assertContains(response, reverse('dashboard:user_list'))
        self.assertContains(response, reverse('dashboard:product_list'))
        self.assertContains(response, reverse('dashboard:category_list'))
        self.assertContains(response, reverse('dashboard:banner_list'))


class DashboardCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@example.com',
            password='Password123!',
            is_staff=True
        )
        self.category = Category.objects.create(name='Audio', description='Headphones')
        self.client.login(username='staffadmin', password='Password123!')

    def test_product_crud_flow(self):
        """Test creating, editing, toggling, and deleting a product inside dashboard."""
        # 1. Product list
        list_resp = self.client.get(reverse('dashboard:product_list'))
        self.assertEqual(list_resp.status_code, 200)

        # 2. Product create
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile(
            name='test_img.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )
        create_resp = self.client.post(reverse('dashboard:product_create'), {
            'name': 'AirPods Max',
            'category': self.category.pk,
            'price': '59900.00',
            'image': test_image,
            'description': 'High-fidelity audio.',
            'key_specs': 'Active Noise Cancellation',
            'is_active': True,
        })
        self.assertRedirects(create_resp, reverse('dashboard:product_list'))
        product = Product.objects.get(name='AirPods Max')
        self.assertEqual(product.price, 59900.00)

        # 3. Product edit
        edit_resp = self.client.post(reverse('dashboard:product_edit', args=[product.pk]), {
            'name': 'AirPods Max (USB-C)',
            'category': self.category.pk,
            'price': '59900.00',
            'description': 'Updated with USB-C.',
            'is_active': True,
        })
        self.assertRedirects(edit_resp, reverse('dashboard:product_list'))
        product.refresh_from_db()
        self.assertEqual(product.name, 'AirPods Max (USB-C)')

        # 4. Product toggle status
        toggle_resp = self.client.get(reverse('dashboard:product_toggle', args=[product.pk]) + '?field=is_active')
        product.refresh_from_db()
        self.assertFalse(product.is_active)

        # 5. Product delete
        del_resp = self.client.post(reverse('dashboard:product_delete', args=[product.pk]))
        self.assertRedirects(del_resp, reverse('dashboard:product_list'))
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())

    def test_category_crud_flow(self):
        """Test creating, editing, and deleting a category inside dashboard."""
        create_resp = self.client.post(reverse('dashboard:category_create'), {
            'name': 'Smartphones',
            'description': 'Flagship mobile devices',
            'is_active': True,
        })
        self.assertRedirects(create_resp, reverse('dashboard:category_list'))
        cat = Category.objects.get(name='Smartphones')

        edit_resp = self.client.post(reverse('dashboard:category_edit', args=[cat.pk]), {
            'name': 'iPhone',
            'description': 'iPhone family',
            'is_active': True,
        })
        self.assertRedirects(edit_resp, reverse('dashboard:category_list'))
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'iPhone')

        del_resp = self.client.post(reverse('dashboard:category_delete', args=[cat.pk]))
        self.assertRedirects(del_resp, reverse('dashboard:category_list'))
        self.assertFalse(Category.objects.filter(pk=cat.pk).exists())

    def test_banner_crud_flow(self):
        """Test creating, editing, toggling, and deleting a banner inside dashboard."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile(
            name='banner.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )
        create_resp = self.client.post(reverse('dashboard:banner_create'), {
            'title': 'iPhone 16 Pro',
            'subtitle': 'Hello, Apple Intelligence.',
            'image': test_image,
            'button_text': 'Learn more',
            'button_link': '/products/',
            'order': 1,
            'is_active': True,
        })
        self.assertRedirects(create_resp, reverse('dashboard:banner_list'))
        banner = Banner.objects.get(title='iPhone 16 Pro')

        toggle_resp = self.client.get(reverse('dashboard:banner_toggle', args=[banner.pk]))
        banner.refresh_from_db()
        self.assertFalse(banner.is_active)

        del_resp = self.client.post(reverse('dashboard:banner_delete', args=[banner.pk]))
        self.assertRedirects(del_resp, reverse('dashboard:banner_list'))
        self.assertFalse(Banner.objects.filter(pk=banner.pk).exists())

    def test_user_crud_flow(self):
        """Test creating, editing, toggling, and deleting a user inside dashboard."""
        create_resp = self.client.post(reverse('dashboard:user_create'), {
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'SecurePassword123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': False,
            'is_active': True,
        })
        self.assertRedirects(create_resp, reverse('dashboard:user_list'))
        user = User.objects.get(username='johndoe')

        # Toggle staff
        toggle_resp = self.client.get(reverse('dashboard:user_toggle', args=[user.pk]) + '?field=is_staff')
        user.refresh_from_db()
        self.assertTrue(user.is_staff)

        # Edit user
        edit_resp = self.client.post(reverse('dashboard:user_edit', args=[user.pk]), {
            'username': 'johndoe',
            'email': 'john.doe@corporate.com',
            'first_name': 'Jonathan',
            'last_name': 'Doe',
            'is_staff': True,
            'is_active': True,
        })
        self.assertRedirects(edit_resp, reverse('dashboard:user_list'))
        user.refresh_from_db()
        self.assertEqual(user.email, 'john.doe@corporate.com')

        # Delete user
        del_resp = self.client.post(reverse('dashboard:user_delete', args=[user.pk]))
        self.assertRedirects(del_resp, reverse('dashboard:user_list'))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
