from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create or update default admin and test user credentials'

    def handle(self, *args, **options):
        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(username='admin')
        admin_user.set_password('admin123')
        admin_user.email = 'admin@vcart.store'
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'Manager'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] {status} superuser: admin (password: admin123)'))

        # 2. Test Customer User
        test_user, created = User.objects.get_or_create(username='testuser')
        test_user.set_password('TestUser123!')
        test_user.email = 'testuser@vcart.store'
        test_user.first_name = 'Test'
        test_user.last_name = 'Customer'
        test_user.is_staff = False
        test_user.is_superuser = False
        test_user.is_active = True
        test_user.save()
        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'[SUCCESS] {status} test user: testuser (password: TestUser123!)'))
