import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.jobs.domain.entities.company import Company
from apps.jobs.domain.entities.jobs import Jobs


class JobsModelTest(TestCase):
    """Tests for the Jobs model creation and field behavior."""

    def setUp(self):
        self.company = Company.objects.create_user(
            username="empresa@test.com",
            password="CompanyPass123!",
            company_name="Tech Corp"
        )

    def test_job_creation_with_required_fields(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Backend Developer",
            description="Develop REST APIs with Django."
        )
        self.assertEqual(job.title, "Backend Developer")
        self.assertEqual(job.description, "Develop REST APIs with Django.")
        self.assertEqual(job.company, self.company)

    def test_job_creation_with_all_fields(self):
        deadline = timezone.now() + timezone.timedelta(days=30)
        job = Jobs.objects.create(
            company=self.company,
            title="Full Stack Engineer",
            description="Work on both frontend and backend.",
            requirements="3+ years experience in Python and React.",
            benefits="Health insurance, remote work.",
            location="Quito, Ecuador",
            job_type='full_time',
            experience_level='mid',
            salary_min=Decimal('2000.00'),
            salary_max=Decimal('4000.00'),
            is_remote=True,
            application_deadline=deadline
        )
        self.assertEqual(job.title, "Full Stack Engineer")
        self.assertEqual(job.requirements, "3+ years experience in Python and React.")
        self.assertEqual(job.benefits, "Health insurance, remote work.")
        self.assertEqual(job.location, "Quito, Ecuador")
        self.assertEqual(job.job_type, 'full_time')
        self.assertEqual(job.experience_level, 'mid')
        self.assertEqual(job.salary_min, Decimal('2000.00'))
        self.assertEqual(job.salary_max, Decimal('4000.00'))
        self.assertTrue(job.is_remote)
        self.assertEqual(job.application_deadline, deadline)

    def test_job_str_representation(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Data Scientist",
            description="Analyze data and build ML models."
        )
        self.assertEqual(str(job), "Data Scientist - Tech Corp")


class JobTypeChoicesTest(TestCase):
    """Tests for job_type choices validation."""

    def setUp(self):
        self.company = Company.objects.create_user(
            username="choices_company@test.com",
            password="ChoicesPass123!",
            company_name="Choices Inc"
        )

    def test_job_type_default_is_full_time(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Default Type Job",
            description="Testing default job_type."
        )
        self.assertEqual(job.job_type, 'full_time')

    def test_job_type_full_time(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Full Time Job",
            description="Full time position.",
            job_type='full_time'
        )
        self.assertEqual(job.job_type, 'full_time')
        self.assertEqual(job.get_job_type_display_name(), 'Tiempo completo')

    def test_job_type_part_time(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Part Time Job",
            description="Part time position.",
            job_type='part_time'
        )
        self.assertEqual(job.job_type, 'part_time')
        self.assertEqual(job.get_job_type_display_name(), 'Tiempo parcial')

    def test_job_type_contract(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Contract Job",
            description="Contract position.",
            job_type='contract'
        )
        self.assertEqual(job.job_type, 'contract')
        self.assertEqual(job.get_job_type_display_name(), 'Contrato')

    def test_job_type_internship(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Internship",
            description="Internship position.",
            job_type='internship'
        )
        self.assertEqual(job.job_type, 'internship')
        self.assertEqual(job.get_job_type_display_name(), 'Prácticas')

    def test_job_type_freelance(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Freelance Job",
            description="Freelance position.",
            job_type='freelance'
        )
        self.assertEqual(job.job_type, 'freelance')
        self.assertEqual(job.get_job_type_display_name(), 'Freelance')

    def test_invalid_job_type_raises_validation_error(self):
        job = Jobs(
            company=self.company,
            title="Invalid Type Job",
            description="This has an invalid job type.",
            job_type='invalid_type'
        )
        with self.assertRaises(ValidationError):
            job.full_clean()


class ExperienceLevelChoicesTest(TestCase):
    """Tests for experience_level choices validation."""

    def setUp(self):
        self.company = Company.objects.create_user(
            username="exp_company@test.com",
            password="ExpPass123!",
            company_name="Experience Corp"
        )

    def test_experience_level_default_is_entry(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Entry Level Job",
            description="Testing default experience level."
        )
        self.assertEqual(job.experience_level, 'entry')

    def test_experience_level_entry(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Entry Job",
            description="Entry level.",
            experience_level='entry'
        )
        self.assertEqual(job.get_experience_display_name(), 'Sin experiencia')

    def test_experience_level_junior(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Junior Job",
            description="Junior level.",
            experience_level='junior'
        )
        self.assertEqual(job.experience_level, 'junior')
        self.assertEqual(job.get_experience_display_name(), 'Junior (1-2 años)')

    def test_experience_level_mid(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Mid Job",
            description="Mid level.",
            experience_level='mid'
        )
        self.assertEqual(job.experience_level, 'mid')
        self.assertEqual(job.get_experience_display_name(), 'Intermedio (3-5 años)')

    def test_experience_level_senior(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Senior Job",
            description="Senior level.",
            experience_level='senior'
        )
        self.assertEqual(job.experience_level, 'senior')
        self.assertEqual(job.get_experience_display_name(), 'Senior (5+ años)')

    def test_experience_level_lead(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Lead Job",
            description="Lead level.",
            experience_level='lead'
        )
        self.assertEqual(job.experience_level, 'lead')
        self.assertEqual(job.get_experience_display_name(), 'Líder técnico (7+ años)')

    def test_invalid_experience_level_raises_validation_error(self):
        job = Jobs(
            company=self.company,
            title="Invalid Exp Job",
            description="This has an invalid experience level.",
            experience_level='expert'
        )
        with self.assertRaises(ValidationError):
            job.full_clean()


class SalaryRangeTest(TestCase):
    """Tests for salary range logic."""

    def setUp(self):
        self.company = Company.objects.create_user(
            username="salary_company@test.com",
            password="SalaryPass123!",
            company_name="Salary Corp"
        )

    def test_salary_min_less_than_max(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Good Salary Job",
            description="Valid salary range.",
            salary_min=Decimal('1500.00'),
            salary_max=Decimal('3000.00')
        )
        self.assertLess(job.salary_min, job.salary_max)

    def test_salary_min_equals_max(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Fixed Salary Job",
            description="Fixed salary.",
            salary_min=Decimal('2500.00'),
            salary_max=Decimal('2500.00')
        )
        self.assertEqual(job.salary_min, job.salary_max)

    def test_salary_fields_nullable(self):
        job = Jobs.objects.create(
            company=self.company,
            title="No Salary Info",
            description="Salary not disclosed."
        )
        self.assertIsNone(job.salary_min)
        self.assertIsNone(job.salary_max)

    def test_salary_decimal_precision(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Precise Salary Job",
            description="Test decimal precision.",
            salary_min=Decimal('1234.56'),
            salary_max=Decimal('7890.12')
        )
        self.assertEqual(job.salary_min, Decimal('1234.56'))
        self.assertEqual(job.salary_max, Decimal('7890.12'))


class IsRemoteDefaultTest(TestCase):
    """Tests for is_remote default value."""

    def setUp(self):
        self.company = Company.objects.create_user(
            username="remote_company@test.com",
            password="RemotePass123!",
            company_name="Remote Corp"
        )

    def test_is_remote_default_false(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Office Job",
            description="On-site work."
        )
        self.assertFalse(job.is_remote)

    def test_is_remote_can_be_true(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Remote Job",
            description="Work from anywhere.",
            is_remote=True
        )
        self.assertTrue(job.is_remote)

    def test_job_has_timestamps(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Timestamped Job",
            description="Testing timestamps."
        )
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)

    def test_job_default_metrics(self):
        job = Jobs.objects.create(
            company=self.company,
            title="Metrics Job",
            description="Testing default metrics."
        )
        self.assertEqual(job.interactions_score, 0.0)
        self.assertEqual(job.view_count, 0)
        self.assertEqual(job.application_count, 0)
