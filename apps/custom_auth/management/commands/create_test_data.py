"""
Django management command to create test data for the application.
Creates researchers, companies, jobs, and feed posts for testing purposes.
"""

import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from apps.custom_auth.models import Company
from apps.jobs.models import Jobs, Postulants
from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.comment import Comment
from apps.feeds.domain.entities.like import Like

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data: 44 researchers, 5 companies, jobs, and feed posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_test_data()

        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('🚀 Starting test data creation...'))
            
            # Create researchers
            researchers = self.create_researchers()
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(researchers)} researchers'))
            
            # Create companies
            companies = self.create_companies()
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(companies)} companies'))
            
            # Create jobs
            jobs = self.create_jobs(companies)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(jobs)} jobs'))
            
            # Create feed posts
            posts = self.create_feed_posts(researchers)
            self.stdout.write(self.style.SUCCESS(f'✅ Created {len(posts)} feed posts'))
            
            # Create comments and likes
            self.create_interactions(researchers, posts)
            self.stdout.write(self.style.SUCCESS('✅ Created comments and likes'))
            
            self.stdout.write(self.style.SUCCESS('🎉 Test data creation completed!'))
            self.print_summary()

    def clear_test_data(self):
        """Clear existing test data"""
        self.stdout.write(self.style.WARNING('🗑️  Clearing existing test data...'))
        
        # Delete test users (those with email containing 'test')
        User.objects.filter(username__contains='test').delete()
        Company.objects.filter(username__contains='test').delete()
        
        self.stdout.write(self.style.SUCCESS('✅ Existing test data cleared'))

    def create_researchers(self):
        """Create 44 test researchers"""
        researchers = []
        
        research_fields = [
            'Artificial Intelligence', 'Machine Learning', 'Computer Vision', 
            'Natural Language Processing', 'Robotics', 'Data Science',
            'Bioinformatics', 'Quantum Computing', 'Cybersecurity', 'Blockchain',
            'Internet of Things', 'Cloud Computing', 'Software Engineering',
            'Human-Computer Interaction', 'Database Systems', 'Networks',
            'Distributed Systems', 'Computer Graphics', 'Algorithms',
            'Computational Biology', 'Digital Health', 'Smart Cities'
        ]
        
        institutions = [
            'MIT', 'Stanford University', 'Carnegie Mellon University',
            'UC Berkeley', 'Harvard University', 'Oxford University',
            'Cambridge University', 'ETH Zurich', 'Universidad de Chile',
            'PUC Chile', 'Universidad de Santiago', 'Universidad Técnica Federico Santa María',
            'Universidad de Concepción', 'Universidad Austral de Chile'
        ]
        
        skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'R', 'MATLAB',
            'TensorFlow', 'PyTorch', 'React', 'Angular', 'Vue.js',
            'Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure',
            'Git', 'Linux', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL'
        ]
        
        for i in range(1, 45):  # 44 researchers
            email = f'researcher{i:02d}@test.com'
            first_name = f'Researcher{i:02d}'
            last_name = f'Test{i:02d}'
            research_field = random.choice(research_fields)
            institution = random.choice(institutions)
            bio = f'Experienced researcher in {research_field} with {random.randint(1, 20)} years of experience.'
            
            researcher = User.objects.create_user(
                username=email,  # El campo username es un EmailField
                password='testpass123',
                first_name=first_name,
                last_name=last_name,
                investigation_camp=research_field,
                institution=f"{institution} University",
                interests=bio,
                is_active=True
            )
            researchers.append(researcher)
        
        return researchers

    def create_companies(self):
        """Create 5 test companies"""
        companies = []
        
        company_data = [
            {
                'name': 'TechCorp Innovation',
                'industry': 'Technology',
                'size': 'Large',
                'description': 'Leading technology company specializing in AI and machine learning solutions.',
                'website': 'https://techcorp.com'
            },
            {
                'name': 'DataScience Solutions',
                'industry': 'Analytics',
                'size': 'Medium',
                'description': 'Data science consulting firm helping businesses leverage their data.',
                'website': 'https://datasciencesolutions.com'
            },
            {
                'name': 'BioTech Research Lab',
                'industry': 'Biotechnology',
                'size': 'Small',
                'description': 'Cutting-edge biotechnology research and development company.',
                'website': 'https://biotechlab.com'
            },
            {
                'name': 'FinTech Innovations',
                'industry': 'Finance',
                'size': 'Medium',
                'description': 'Revolutionary financial technology solutions for the modern world.',
                'website': 'https://fintechinnovations.com'
            },
            {
                'name': 'Green Energy Corp',
                'industry': 'Energy',
                'size': 'Large',
                'description': 'Sustainable energy solutions and research company.',
                'website': 'https://greenenergycorp.com'
            }
        ]
        
        for i, data in enumerate(company_data, 1):
            email = f'company{i:02d}@test.com'
            company = Company.objects.create_user(
                username=email,  # El campo username es un EmailField
                password='testpass123',
                company_name=data['name'],
                industry='technology' if 'tech' in data['industry'].lower() else 'other',
                description=data['description'],
                website=data['website'],
                phone=f'+1-555-{random.randint(1000, 9999)}',
                address=f'{random.randint(100, 999)} Innovation St, Tech City, TC {random.randint(10000, 99999)}',
                is_active=True
            )
            companies.append(company)
        
        return companies

    def create_jobs(self, companies):
        """Create test jobs for the companies"""
        jobs = []
        
        job_titles = [
            'Senior Data Scientist', 'Machine Learning Engineer', 'Research Scientist',
            'AI Research Engineer', 'Principal Software Engineer', 'Senior Backend Developer',
            'DevOps Engineer', 'Cloud Solutions Architect', 'Product Manager',
            'UX Research Specialist', 'Bioinformatics Researcher', 'Quantum Computing Researcher',
            'Cybersecurity Analyst', 'Blockchain Developer', 'Computer Vision Engineer',
            'NLP Research Scientist', 'Robotics Engineer', 'Data Engineer',
            'Full Stack Developer', 'Mobile App Developer'
        ]
        
        job_descriptions = [
            'We are looking for an experienced professional to join our innovative team.',
            'Join our cutting-edge research team and make a real impact.',
            'Exciting opportunity to work on groundbreaking projects.',
            'Be part of a dynamic team solving complex technical challenges.',
            'Work with the latest technologies in a collaborative environment.'
        ]
        
        requirements = [
            'PhD in Computer Science or related field',
            'Masters degree with 3+ years experience',
            'Strong programming skills in Python/Java',
            'Experience with machine learning frameworks',
            'Knowledge of cloud platforms (AWS/GCP/Azure)',
            'Excellent communication and teamwork skills'
        ]
        
        benefits = [
            'Competitive salary and equity package',
            'Comprehensive health and dental insurance',
            'Flexible work arrangements and remote options',
            'Professional development opportunities',
            'Generous vacation and parental leave policies',
            'State-of-the-art equipment and office spaces'
        ]
        
        job_types = ['full_time', 'part_time', 'contract', 'internship', 'freelance']
        experience_levels = ['entry', 'junior', 'mid', 'senior', 'lead']
        
        for company in companies:
            # Each company creates 3-5 jobs
            num_jobs = random.randint(3, 5)
            for _ in range(num_jobs):
                job = Jobs.objects.create(
                    title=random.choice(job_titles),
                    description=random.choice(job_descriptions),
                    requirements='\n'.join(random.sample(requirements, random.randint(3, 5))),
                    benefits='\n'.join(random.sample(benefits, random.randint(3, 4))),
                    company=company,
                    location=f'{random.choice(["Remote", "New York", "San Francisco", "Boston", "Seattle", "Austin"])}',
                    job_type=random.choice(job_types),
                    experience_level=random.choice(experience_levels),
                    salary_min=random.randint(60000, 120000),
                    salary_max=random.randint(120000, 200000),
                    is_remote=random.choice([True, False]),
                    view_count=random.randint(10, 500),
                    application_count=random.randint(0, 50)
                )
                jobs.append(job)
        
        return jobs

    def create_feed_posts(self, researchers):
        """Create test feed posts"""
        posts = []
        
        post_contents = [
            "Just published a new paper on machine learning applications in healthcare! 🎉",
            "Excited to share our latest research findings at the upcoming conference.",
            "Looking for collaborators on an AI project focused on climate change solutions.",
            "Great discussion at today's seminar about the future of quantum computing.",
            "Happy to announce that our team received funding for the next phase of research!",
            "Interesting insights from the latest Nature paper on neural networks.",
            "Working on a fascinating project that combines computer vision with robotics.",
            "Attending the AI conference next week - looking forward to networking!",
            "Just completed a successful experiment with promising results.",
            "Sharing some thoughts on the ethical implications of AI in society.",
            "Our latest algorithm achieved state-of-the-art results on the benchmark dataset!",
            "Collaborating with international researchers on a groundbreaking project.",
            "Excited about the potential applications of our new methodology.",
            "Presenting our work at the workshop - feedback has been very positive!",
            "Working late in the lab, but the results are worth it! 💪",
            "Just submitted our paper to a top-tier journal - fingers crossed!",
            "Grateful for the opportunity to work with such talented colleagues.",
            "Breaking: our research was featured in the university newsletter!",
            "Thinking about the next steps for our research direction.",
            "Coffee and code - the perfect combination for productivity! ☕",
            "Mentoring undergraduate students has been incredibly rewarding.",
            "Our open-source project just reached 1000 stars on GitHub! 🌟",
            "Debugging code at 2 AM - the researcher's life! 🐛",
            "Excited to start a new collaboration with industry partners.",
            "Just finished reviewing papers for the conference - great submissions this year!"
        ]
        
        # Create posts for random researchers
        for _ in range(40):  # Create 40 posts
            author = random.choice(researchers)
            post = FeedPost.objects.create(
                author=author,
                content=random.choice(post_contents),
                is_public=True,
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                views_count=random.randint(5, 200),
                likes_count=random.randint(0, 50),
                comments_count=random.randint(0, 15),
                shares_count=random.randint(0, 10)
            )
            posts.append(post)
        
        return posts

    def create_interactions(self, researchers, posts):
        """Create comments and likes for posts"""
        comment_texts = [
            "Great work! Looking forward to reading the full paper.",
            "Congratulations on this achievement!",
            "Very interesting approach - have you considered...?",
            "This is exactly what our field needs right now.",
            "Impressive results! How long did the experiment take?",
            "Thanks for sharing this valuable insight.",
            "Could you share more details about the methodology?",
            "This opens up so many new research directions!",
            "Excellent work - keep it up!",
            "I'd love to collaborate on something similar.",
            "The implications of this research are fascinating.",
            "Have you thought about applying this to other domains?",
            "This could revolutionize the field!",
            "Well done! The scientific community will benefit greatly.",
            "Inspiring work - motivates me to push harder in my own research."
        ]
        
        # Create comments
        for post in posts:
            num_comments = random.randint(0, 8)
            for _ in range(num_comments):
                commenter = random.choice(researchers)
                if commenter != post.author:  # Don't comment on own posts
                    Comment.objects.create(
                        post=post,
                        author=commenter,
                        content=random.choice(comment_texts),
                        created_at=post.created_at + timedelta(
                            hours=random.randint(1, 24 * 7)
                        )
                    )
        
        # Create likes
        post_content_type = ContentType.objects.get_for_model(FeedPost)
        
        for post in posts:
            num_likes = random.randint(0, 25)
            likers = random.sample(researchers, min(num_likes, len(researchers)))
            for liker in likers:
                if liker != post.author:  # Don't like own posts
                    Like.objects.create(
                        user=liker,
                        content_type=post_content_type,
                        object_id=post.id
                    )

    def print_summary(self):
        """Print a summary of created data"""
        self.stdout.write(self.style.SUCCESS('\n📊 SUMMARY OF CREATED TEST DATA:'))
        self.stdout.write(f'👥 Researchers: {User.objects.filter(username__contains="test").count()}')
        self.stdout.write(f'🏢 Companies: {Company.objects.filter(username__contains="test").count()}')
        self.stdout.write(f'💼 Jobs: {Jobs.objects.filter(company__username__contains="test").count()}')
        self.stdout.write(f'📝 Feed Posts: {FeedPost.objects.filter(author__username__contains="test").count()}')
        self.stdout.write(f'💬 Comments: {Comment.objects.filter(author__username__contains="test").count()}')
        self.stdout.write(f'❤️  Likes: {Like.objects.filter(user__username__contains="test").count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 LOGIN CREDENTIALS:'))
        self.stdout.write('📧 Researchers: researcher01@test.com to researcher44@test.com')
        self.stdout.write('📧 Companies: company01@test.com to company05@test.com')
        self.stdout.write('🔒 Password for all accounts: testpass123')
        
        self.stdout.write(self.style.SUCCESS('\n🚀 Ready for testing!'))
