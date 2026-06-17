import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.custom_auth.models import MagicLink
from apps.custom_auth.domain.entities.group import Group, GroupUser

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


class MagicLinkTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="linkuser",
            email="link@centinela.epn.ec",
            password="LinkPass123!"
        )

    def test_magic_link_is_valid_when_new(self):
        link = MagicLink.objects.create(user=self.user)
        self.assertTrue(link.is_valid())
        self.assertFalse(link.is_used)

    def test_magic_link_invalid_when_expired(self):
        link = MagicLink(
            user=self.user,
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        link.save()
        self.assertFalse(link.is_valid())

    def test_magic_link_invalid_when_used(self):
        link = MagicLink.objects.create(user=self.user)
        link.is_used = True
        link.save()
        self.assertFalse(link.is_valid())


class GroupModelTest(TestCase):
    """Tests for Group model creation and behavior."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="group_admin@centinela.epn.ec",
            password="GroupPass123!",
            first_name="Group",
            last_name="Admin"
        )
        self.member_user = User.objects.create_user(
            username="group_member@centinela.epn.ec",
            password="MemberPass123!",
            first_name="Group",
            last_name="Member"
        )
        self.member_user2 = User.objects.create_user(
            username="group_member2@centinela.epn.ec",
            password="Member2Pass123!",
            first_name="Second",
            last_name="Member"
        )

    def test_group_creation_with_admin(self):
        group = Group.objects.create(
            title="Research Team",
            description="A team for research purposes.",
            admin=self.admin_user
        )
        self.assertEqual(group.title, "Research Team")
        self.assertEqual(group.description, "A team for research purposes.")
        self.assertEqual(group.admin, self.admin_user)

    def test_group_str_representation(self):
        group = Group.objects.create(
            title="Test Group",
            description="Testing str.",
            admin=self.admin_user
        )
        self.assertEqual(str(group), "Test Group")

    def test_group_id_is_10_chars(self):
        group = Group.objects.create(
            title="ID Group",
            description="Testing ID length.",
            admin=self.admin_user
        )
        self.assertEqual(len(group.id), 10)

    def test_group_id_is_alphanumeric(self):
        group = Group.objects.create(
            title="Alphanumeric Group",
            description="Testing ID format.",
            admin=self.admin_user
        )
        self.assertTrue(group.id.isalnum())

    def test_group_voting_type_default_positional(self):
        group = Group.objects.create(
            title="Default Voting Group",
            description="Should default to Positional Voting.",
            admin=self.admin_user
        )
        self.assertEqual(group.voting_type, 'Positional Voting')

    def test_group_voting_type_positional(self):
        group = Group.objects.create(
            title="Positional Group",
            description="Explicit positional voting.",
            admin=self.admin_user,
            voting_type=Group.VotingType.POSITIONAL
        )
        self.assertEqual(group.voting_type, 'Positional Voting')

    def test_group_voting_type_nonpositional(self):
        group = Group.objects.create(
            title="Non-Positional Group",
            description="Non-positional voting.",
            admin=self.admin_user,
            voting_type=Group.VotingType.NONPOSITIONAL
        )
        self.assertEqual(group.voting_type, 'Non-Positional Voting')

    def test_invalid_voting_type_raises_validation_error(self):
        group = Group(
            title="Invalid Voting",
            description="Invalid voting type.",
            admin=self.admin_user,
            voting_type='invalid_choice'
        )
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_add_user_to_group(self):
        group = Group.objects.create(
            title="Members Group",
            description="Group with members.",
            admin=self.admin_user
        )
        GroupUser.objects.create(group=group, user=self.member_user)
        self.assertIn(self.member_user, group.users.all())

    def test_add_multiple_users_to_group(self):
        group = Group.objects.create(
            title="Multi Members Group",
            description="Group with multiple members.",
            admin=self.admin_user
        )
        GroupUser.objects.create(group=group, user=self.member_user)
        GroupUser.objects.create(group=group, user=self.member_user2)
        self.assertEqual(group.users.count(), 2)

    def test_remove_user_from_group(self):
        group = Group.objects.create(
            title="Remove User Group",
            description="Testing user removal.",
            admin=self.admin_user
        )
        gu = GroupUser.objects.create(group=group, user=self.member_user)
        self.assertEqual(group.users.count(), 1)
        gu.delete()
        self.assertEqual(group.users.count(), 0)

    def test_group_admin_is_not_automatically_member(self):
        group = Group.objects.create(
            title="Admin Not Member",
            description="Admin is not auto-added as member.",
            admin=self.admin_user
        )
        self.assertNotIn(self.admin_user, group.users.all())

    def test_group_admin_relationship(self):
        group = Group.objects.create(
            title="Admin Relation Group",
            description="Testing admin FK.",
            admin=self.admin_user
        )
        self.assertEqual(group.admin.id, self.admin_user.id)
        self.assertIn(group, self.admin_user.administered_groups.all())
