from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationTest(TestCase):
    def test_create_regular_user(self):
        user = User.objects.create_user(
            username="brayan",
            email="brayan@centinela.epn.ec",
            password="SecurePass123!"
        )
        self.assertEqual(user.username, "brayan")
        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@centinela.epn.ec",
            password="AdminPass456!"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_email_is_stored(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@epn.edu.ec",
            password="Pass789!"
        )
        self.assertEqual(user.email, "test@epn.edu.ec")
