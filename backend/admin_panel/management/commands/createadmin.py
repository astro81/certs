from django.core.management.base import BaseCommand
from admin_panel.models import AdminUser

class Command(BaseCommand):
    help = 'Create an admin user'

    def handle(self, *args, **kwargs):
        email = input('Admin Email: ')
        password = input('Password: ')
        if AdminUser.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR('Admin already exists'))
        else:
            AdminUser.objects.create_user(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Admin {email} created successfully'))
