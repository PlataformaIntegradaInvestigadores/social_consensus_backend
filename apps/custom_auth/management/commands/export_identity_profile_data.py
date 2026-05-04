import json

from django.core.management.base import BaseCommand

from apps.custom_auth.models import Group, ProfileInformation, User


class Command(BaseCommand):
    help = "Exporta identidad, perfiles, grupos y membresias legacy para importarlas al microservicio."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="identity_profile_export.json")

    def handle(self, *args, **options):
        payload = {
            "users": [self.serialize_user(user) for user in User.objects.all()],
            "profiles": [self.serialize_profile(profile) for profile in ProfileInformation.objects.all()],
            "groups": [self.serialize_group(group) for group in Group.objects.all()],
            "group_memberships": [
                {"group_id": group.id, "users": list(group.users.values_list("id", flat=True))}
                for group in Group.objects.all()
            ],
        }

        with open(options["output"], "w", encoding="utf-8") as target:
            json.dump(payload, target, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Exportacion completada: {options['output']}"))

    def serialize_user(self, user):
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "password": user.password,
            "scopus_id": user.scopus_id,
            "investigation_camp": user.investigation_camp,
            "institution": user.institution,
            "email_institution": user.email_institution,
            "website": user.website,
            "profile_picture": str(user.profile_picture or ""),
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "interests": user.interests,
            "interaction_count": user.interaction_count,
        }

    def serialize_profile(self, profile):
        return {
            "user_id": profile.user_id,
            "about_me": profile.about_me,
            "disciplines": profile.disciplines,
            "contact_info": profile.contact_info,
        }

    def serialize_group(self, group):
        return {
            "id": group.id,
            "title": group.title,
            "description": group.description,
            "admin_id": group.admin_id,
            "voting_type": group.voting_type,
            "users": list(group.users.values_list("id", flat=True)),
        }
