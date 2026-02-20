"""
Seeder completo para presentación de tesis.
Borra TODA la data y crea usuarios, posts, comentarios, likes, encuestas, jobs.
Usuario principal: kennypinchao@hotmail.com / 12345678
"""
import random
import uuid
import math
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import transaction
from apps.custom_auth.models import Company
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.domain.entities.postulants import Postulants
from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.comment import Comment
from apps.feeds.domain.entities.like import Like
from apps.feeds.domain.entities.poll import Poll, PollOption, PollVote

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# DATOS SEMILLA
# ─────────────────────────────────────────────────────────────────────────────

RESEARCHER_PROFILES = [
    # (email, first, last, field, institution, interests)
    ('maria.gomez@example.com', 'María', 'Gómez', 'Data Science',
     'MIT', 'Specialized in predictive analytics, big data pipelines and real-time dashboards. Experienced with Spark and Kafka.'),
    ('carlos.ruiz@example.com', 'Carlos', 'Ruiz', 'Deep Learning',
     'Stanford University', 'Focused on convolutional neural networks and GANs applied to medical imaging. PyTorch enthusiast.'),
    ('ana.silva@example.com', 'Ana', 'Silva', 'Bioinformatics',
     'Harvard University', 'Working on protein folding prediction using AlphaFold and molecular dynamics simulations.'),
    ('david.chen@example.com', 'David', 'Chen', 'Quantum Computing',
     'University of Oxford', 'Developing error-corrected quantum algorithms for combinatorial optimization problems.'),
    ('elena.torres@example.com', 'Elena', 'Torres', 'Cybersecurity',
     'University of Cambridge', 'Researching zero-trust architectures and adversarial attacks on LLMs.'),
    ('james.wilson@example.com', 'James', 'Wilson', 'Robotics',
     'ETH Zurich', 'Working on autonomous drone navigation and SLAM algorithms in GPS-denied environments.'),
    ('sofia.martinez@example.com', 'Sofía', 'Martínez', 'NLP',
     'UC Berkeley', 'Focused on multilingual language models, dialogue systems, and text-to-speech synthesis.'),
    ('lucas.brown@example.com', 'Lucas', 'Brown', 'Cloud Computing',
     'Carnegie Mellon University', 'Expert in Kubernetes orchestration, service meshes and serverless patterns on AWS/GCP.'),
    ('isabella.rossi@example.com', 'Isabella', 'Rossi', 'IoT',
     'Politecnico di Milano', 'Designing smart-city sensor networks with edge AI inference on NVIDIA Jetson modules.'),
    ('william.taylor@example.com', 'William', 'Taylor', 'Blockchain',
     'University College London', 'Researching DeFi protocols, zero-knowledge proofs, and on-chain governance.'),
    ('valentina.lopez@example.com', 'Valentina', 'López', 'Computer Vision',
     'KAIST', 'Expert in real-time object detection (YOLO, DETR) and 3D scene reconstruction.'),
    ('ahmed.hassan@example.com', 'Ahmed', 'Hassan', 'Reinforcement Learning',
     'University of Toronto', 'Training multi-agent RL systems for collaborative robotics and game theory.'),
    ('laura.fernandez@example.com', 'Laura', 'Fernández', 'Digital Health',
     'Johns Hopkins University', 'Building AI-powered diagnostics from medical imaging and wearable sensor data.'),
    ('marco.bianchi@example.com', 'Marco', 'Bianchi', 'Software Engineering',
     'TU Munich', 'Researching formal verification of microservices and chaos engineering techniques.'),
    ('priya.patel@example.com', 'Priya', 'Patel', 'Machine Learning',
     'Indian Institute of Technology Delhi', 'Working on federated learning across hospitals to preserve patient privacy.'),
]

COMPANY_PROFILES = [
    # (name, industry_code, description, website)
    ('TechNova Solutions', 'technology',
     'Leading AI and software development company building enterprise-grade recommendation systems.',
     'https://technova.com'),
    ('DataMinds Analytics', 'consulting',
     'Consulting firm specialising in big-data architecture, analytics pipelines and predictive modelling.',
     'https://dataminds.com'),
    ('CyberShield Security', 'technology',
     'Providing enterprise cloud security, SOC-as-a-service and vulnerability assessments.',
     'https://cybershield.com'),
    ('BioGenesis Labs', 'health',
     'Pioneering computational biology workflows for drug discovery and genomic sequencing.',
     'https://biogenesislabs.com'),
    ('CloudScale Systems', 'technology',
     'Helping startups and enterprises migrate to Kubernetes-native multi-cloud architectures.',
     'https://cloudscale.io'),
]

JOB_POSTINGS = [
    # (title, desc, reqs, benefits, level, salary_min, salary_max, remote, location)
    ('Senior Machine Learning Engineer',
     'Lead the design and deployment of production ML pipelines using PyTorch and TensorFlow Serving.',
     'Python, PyTorch, TensorFlow, MLOps, Docker, AWS SageMaker',
     'Remote work, Health insurance, Stock options, $2k/year learning budget',
     'senior', 120000, 180000, True, 'Remote'),
    ('Data Scientist – Retail Analytics',
     'Build predictive demand-forecasting models and A/B testing frameworks for retail clients.',
     'Python, SQL, Scikit-learn, Statistics, Tableau',
     'Bonus plan, Flexible hours, Gym membership',
     'mid', 90000, 130000, False, 'New York'),
    ('Backend Developer (Django / Node)',
     'Design and scale microservice APIs handling 10k+ RPS with Django REST Framework.',
     'Python, Django, PostgreSQL, Redis, Docker, CI/CD',
     'Stock options, Remote work, Unlimited PTO',
     'mid', 85000, 125000, True, 'Remote'),
    ('Cybersecurity Analyst',
     'Monitor cloud infra with SIEM tools, respond to incidents and harden Kubernetes clusters.',
     'Network Security, AWS Security Hub, Kubernetes, Linux',
     'Continuous training, Remote, Certification reimbursement',
     'junior', 70000, 100000, True, 'London'),
    ('Bioinformatics Researcher',
     'Analyse whole-genome sequencing data with custom pipelines built in Nextflow and Python.',
     'R, Python, Genomics, Nextflow, HPC',
     'Health insurance, 401k match, Relocation package',
     'senior', 110000, 160000, False, 'Boston'),
    ('Cloud Solutions Architect',
     'Design multi-region, highly-available AWS/Azure architectures for enterprise SaaS products.',
     'AWS Certified, Kubernetes, Terraform, Networking',
     'Remote, Bonus, Conference travel budget',
     'lead', 150000, 220000, True, 'Remote'),
    ('NLP Engineer',
     'Fine-tune and deploy LLMs for conversational AI, RAG pipelines and intent classification.',
     'NLP, Transformers, Python, LangChain, Vector databases',
     'Flexible hours, Stock options, Training budget',
     'mid', 100000, 155000, True, 'San Francisco'),
    ('Frontend Developer (Angular)',
     'Build responsive SPA interfaces with Angular 16+, Tailwind CSS and state management via NgRx.',
     'Angular, TypeScript, Tailwind, RxJS, Jest',
     'Health insurance, Remote work, Home-office stipend',
     'junior', 65000, 95000, True, 'Remote'),
    ('DevOps / SRE Engineer',
     'Maintain CI/CD pipelines, observability stacks (Prometheus + Grafana) and infrastructure as code.',
     'Docker, Kubernetes, Terraform, GitLab CI, Prometheus',
     'On-call bonus, Remote, Learning budget',
     'mid', 95000, 140000, True, 'Berlin'),
    ('Product Manager – AI Platform',
     'Own the roadmap for our internal ML platform used by 200+ engineers across the company.',
     'Product management, Agile, Data literacy, Stakeholder management',
     'Equity, Health insurance, Annual retreat',
     'senior', 130000, 175000, False, 'New York'),
]

# ─── POSTS: variados en tema, idioma y estilo ────────────────────────────────
GENERIC_POSTS = [
    # AI / ML
    ("Just published our new paper on Transformer-XL architectures! We achieved a 15 % improvement in "
     "inference latency while maintaining BLEU scores. 🚀\n\n"
     "Key takeaway: knowledge distillation plus quantisation is the way forward for edge deployment.\n"
     "#AI #MachineLearning #Transformers",
     ['AI', 'MachineLearning', 'Transformers']),

    ("Has anyone benchmarked the new Llama 3 model against Mixtral on code-generation tasks? "
     "We ran a head-to-head comparison and the results were surprising. Thread below 👇\n"
     "#LLM #OpenSource #CodeGeneration",
     ['LLM', 'OpenSource', 'CodeGeneration']),

    ("Reinforcement Learning from Human Feedback (RLHF) is powerful but expensive. "
     "We've been experimenting with Direct Preference Optimisation (DPO) instead and getting "
     "comparable alignment quality at a fraction of the compute cost. 💡\n"
     "#RLHF #DPO #Alignment",
     ['RLHF', 'DPO', 'Alignment']),

    # Data Science
    ("Tip for fellow data scientists: normalise your features BEFORE splitting into train/test. "
     "Sounds obvious, but data leakage is the number-one silent killer of model performance in production.\n"
     "#DataScience #BestPractices",
     ['DataScience', 'BestPractices']),

    ("We just migrated our entire analytics warehouse from Redshift to BigQuery. "
     "Latency dropped 40 %, costs went down 25 %. Happy to share the migration playbook!\n"
     "#DataEngineering #BigQuery #CloudMigration",
     ['DataEngineering', 'BigQuery', 'CloudMigration']),

    # Cybersecurity
    ("🔒 Zero-trust is NOT just a marketing buzzword. After implementing microsegmentation "
     "and mTLS across all our services, lateral movement in a compromised cluster became practically impossible.\n"
     "#Cybersecurity #ZeroTrust #DevSecOps",
     ['Cybersecurity', 'ZeroTrust', 'DevSecOps']),

    # Open Source
    ("We just open-sourced our bioinformatics pipeline for whole-genome variant calling. "
     "Built with Nextflow + Docker → fully reproducible on any HPC or cloud. Give it a ⭐ on GitHub!\n"
     "#Bioinformatics #OpenSource #Genomics",
     ['Bioinformatics', 'OpenSource', 'Genomics']),

    # Software Engineering
    ("Hot take: monorepos are great for small teams, but after ~50 engineers the CI bottleneck "
     "becomes a real productivity drain. We switched to a poly-repo + Bazel approach and deploy speed "
     "improved 4×.\n#SoftwareEngineering #DevOps #CI",
     ['SoftwareEngineering', 'DevOps', 'CI']),

    ("Docker Compose for local dev, Kubernetes for staging/prod. The mental model is simpler "
     "when you separate concerns like this. Don't over-engineer your dev environment.\n"
     "#Docker #Kubernetes #DevOps",
     ['Docker', 'Kubernetes', 'DevOps']),

    # Quantum & Blockchain
    ("Excited to share our latest quantum error-correction benchmark. We achieved logical qubit "
     "fidelity of 99.6 % using surface codes on a 72-qubit processor. The road to fault-tolerant QC "
     "is shorter than many think. ⚛️\n#QuantumComputing #ErrorCorrection",
     ['QuantumComputing', 'ErrorCorrection']),

    ("Unpopular opinion: most blockchain projects don't need a blockchain. But for cross-border "
     "supply-chain provenance, the combination of ZK-proofs + on-chain attestation is genuinely powerful.\n"
     "#Blockchain #ZKProofs #SupplyChain",
     ['Blockchain', 'ZKProofs', 'SupplyChain']),

    # Computer Vision
    ("Real-time 3D scene reconstruction from a single monocular camera using NeRFs is now possible "
     "at 30 FPS on consumer GPUs. The implications for AR/VR are massive.\n"
     "#ComputerVision #NeRF #AR",
     ['ComputerVision', 'NeRF', 'AR']),

    # IoT / Edge
    ("Deployed TensorFlow Lite models on a fleet of 500 NVIDIA Jetson Nano boards for edge anomaly "
     "detection in a manufacturing plant. Inference under 10 ms per frame. 🏭\n"
     "#IoT #EdgeAI #Manufacturing",
     ['IoT', 'EdgeAI', 'Manufacturing']),

    # Career / Soft Skills
    ("Reminder: writing clean documentation is as important as writing clean code. "
     "Your future self (and your teammates) will thank you.\n"
     "#CareerAdvice #Documentation #Engineering",
     ['CareerAdvice', 'Documentation', 'Engineering']),

    ("Attended an amazing talk on ethical AI at the ACM FAccT conference. We NEED more diverse "
     "voices in ML research to build systems that work for everyone.\n"
     "#Ethics #AI #Diversity #FAccT",
     ['Ethics', 'AI', 'Diversity']),

    # NLP
    ("RAG (Retrieval-Augmented Generation) is the most practical architecture for enterprise LLM "
     "apps right now. Fine-tuning is expensive and fragile; RAG + vector search is cheaper and "
     "more controllable.\n#NLP #RAG #VectorSearch",
     ['NLP', 'RAG', 'VectorSearch']),

    # Health
    ("Our AI-powered retinal scan model detected diabetic retinopathy with 97.3 % sensitivity "
     "in a field trial across 12 rural clinics. Early detection saves eyesight. 👁️\n"
     "#DigitalHealth #AI #MedicalImaging",
     ['DigitalHealth', 'AI', 'MedicalImaging']),

    # Robotics
    ("We just completed 100 hours of autonomous flight with our SLAM-based drone in a GPS-denied "
     "warehouse. Zero collisions, zero human interventions. 🤖✈️\n"
     "#Robotics #Drones #SLAM",
     ['Robotics', 'Drones', 'SLAM']),

    # Cloud
    ("FinOps tip: schedule your dev/staging Kubernetes pods to scale to zero overnight. "
     "We saved ~$4,200/month in AWS bills just by adding a CronJob + KEDA scaler.\n"
     "#Cloud #FinOps #Kubernetes #AWS",
     ['Cloud', 'FinOps', 'Kubernetes']),

    # General Research
    ("Best Paper Award at CVPR 2026! 🏆 Our method for unsupervised domain adaptation "
     "outperformed all baselines by a significant margin. Huge thanks to my co-authors.\n"
     "#CVPR2026 #Research #ComputerVision",
     ['CVPR2026', 'Research', 'ComputerVision']),
]

KENNY_POSTS = [
    ("¡Hola a todos! Estoy trabajando en mi tesis sobre algoritmos de consenso social y "
     "sistemas de recomendación basados en embeddings vectoriales. El objetivo es demostrar "
     "cómo los vectores pueden mejorar la personalización de contenido en redes sociales académicas. 🎓\n"
     "#Tesis #AI #RecommendationSystems",
     ['Tesis', 'AI', 'RecommendationSystems']),

    ("Implementé búsqueda semántica con pgvector en PostgreSQL y los resultados son impresionantes: "
     "la relevancia de las recomendaciones subió un 35 % comparado con TF-IDF. La clave fue normalizar "
     "los embeddings a norma unitaria antes de usar la distancia coseno.\n"
     "#PostgreSQL #VectorSearch #pgvector",
     ['PostgreSQL', 'VectorSearch', 'pgvector']),

    ("Optimicé mis Dockerfiles usando python:3.11-slim-bookworm + multi-stage builds. "
     "El tamaño de la imagen bajó de 1.2 GB a 380 MB y el build time se redujo un 60 %. "
     "¡Cada segundo cuenta cuando haces CI/CD! 🐳\n"
     "#Docker #DevOps #Optimization",
     ['Docker', 'DevOps', 'Optimization']),

    ("Dato interesante: al agregar healthchecks a todos los servicios en Docker Compose con "
     "`depends_on: condition: service_healthy`, los errores de conexión al iniciar los contenedores "
     "desaparecieron por completo. Parece obvio, pero muchos lo omiten.\n"
     "#Docker #Microservices #BestPractices",
     ['Docker', 'Microservices', 'BestPractices']),

    ("Acabo de integrar Celery + Redis para tareas asíncronas en mi backend Django. "
     "Ahora el cálculo de embeddings y la actualización de scores de engagement se ejecutan "
     "en background sin bloquear las respuestas HTTP. ⚡\n"
     "#Django #Celery #Redis #Backend",
     ['Django', 'Celery', 'Redis']),
]

COMMENT_POOL = [
    "This is incredibly insightful, thanks for sharing!",
    "I completely agree. Have you considered extending this to federated settings?",
    "Great work! I'd love to read the full paper. Could you share a link?",
    "Interesting perspective. We had similar results in our lab.",
    "Congratulations on the achievement! Well deserved. 🎉",
    "Could you share the GitHub repository? I'd like to contribute.",
    "This is exactly what I was looking for. Thanks a lot!",
    "Have you thought about how this scales with 10× the data?",
    "We implemented something similar but with a different loss function – results were comparable.",
    "Excellent write-up. Adding this to my reading list for the weekend.",
    "The ethical implications section is really important. More researchers should discuss this.",
    "How long did the training take? What hardware did you use?",
    "This could be a game-changer for small-scale deployments.",
    "I had the same experience when I migrated our pipeline last quarter.",
    "Would love to collaborate on a follow-up study. Let me know!",
    "Have you benchmarked against the Hugging Face version?",
    "Saving this for my students – perfect example for our ML course.",
    "This aligns well with the results from [Smith et al., 2025]. Nice!",
    "Can confirm this works! Just tested it on our staging environment.",
    "Really appreciate you sharing this openly. Open science for the win! 🙌",
]

KENNY_COMMENTS = [
    "¡Excelente post! Esto se alinea mucho con lo que estoy investigando en mi tesis.",
    "Muy interesante, ¿usaste algún framework específico para los embeddings?",
    "Genial, yo implementé algo similar con pgvector. Los resultados son prometedores.",
    "Gracias por compartir, esto me ayuda mucho con mi investigación.",
    "¿Podrías compartir más detalles sobre la arquitectura que usaste?",
]

POLL_DATA = [
    # (question, options, is_multiple)
    ("What is the MOST impactful ML trend for 2026?",
     ["Foundation models (GPT, Llama, Gemini)", "Edge AI / tiny-ML",
      "AI Agents & tool-use", "Multimodal models", "AI safety & alignment"],
     False),
    ("Which vector database do you prefer for production?",
     ["pgvector (PostgreSQL)", "Pinecone", "Weaviate", "Milvus / Zilliz", "Qdrant"],
     False),
    ("What programming languages do you use regularly? (multiple)",
     ["Python", "JavaScript / TypeScript", "Rust", "Go", "Java / Kotlin", "C / C++"],
     True),
]


class Command(BaseCommand):
    help = (
        'Seed database for thesis presentation. '
        'Deletes ALL existing data and creates fresh users, posts, comments, likes, polls and jobs. '
        'Main user: kennypinchao@hotmail.com / 12345678'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-embeddings',
            action='store_true',
            help='Skip embedding generation (faster, useful if the embedding service is down)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🗑️  Wiping ALL existing data …'))
        self._wipe_database()

        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('🚀 Creating presentation data …\n'))

            kenny = self._create_main_user()
            researchers = self._create_researchers()
            all_users = [kenny] + researchers
            self.stdout.write(self.style.SUCCESS(f'  👤 Main user created: {kenny.username}'))
            self.stdout.write(self.style.SUCCESS(f'  👥 {len(researchers)} researchers created'))

            companies = self._create_companies()
            self.stdout.write(self.style.SUCCESS(f'  🏢 {len(companies)} companies created'))

            jobs = self._create_jobs(companies)
            self.stdout.write(self.style.SUCCESS(f'  💼 {len(jobs)} job postings created'))

            posts = self._create_posts(kenny, researchers, all_users)
            self.stdout.write(self.style.SUCCESS(f'  📝 {len(posts)} feed posts created'))

            n_comments, n_likes = self._create_interactions(kenny, researchers, all_users, posts)
            self.stdout.write(self.style.SUCCESS(f'  💬 {n_comments} comments created'))
            self.stdout.write(self.style.SUCCESS(f'  ❤️  {n_likes} likes created'))

            polls_created = self._create_polls(kenny, all_users, posts)
            self.stdout.write(self.style.SUCCESS(f'  📊 {polls_created} polls with votes created'))

            postulants = self._create_postulants(kenny, researchers, jobs)
            self.stdout.write(self.style.SUCCESS(f'  📄 {postulants} job applications created'))

        if not options.get('no_embeddings'):
            self.stdout.write(self.style.WARNING('\n🧠 Generating embeddings (this may take a while) …'))
            self._update_embeddings(all_users, posts, jobs)

        self._print_summary(kenny, researchers, companies, jobs, posts)

    # ─────────────────────────────────────────────────────────────────────
    # WIPE
    # ─────────────────────────────────────────────────────────────────────
    def _wipe_database(self):
        PollVote.objects.all().delete()
        PollOption.objects.all().delete()
        Poll.objects.all().delete()
        Like.objects.all().delete()
        Comment.objects.all().delete()
        FeedPost.objects.all().delete()
        Postulants.objects.all().delete()
        Jobs.objects.all().delete()
        Company.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('  ✅ Database wiped\n'))

    # ─────────────────────────────────────────────────────────────────────
    # USERS
    # ─────────────────────────────────────────────────────────────────────
    def _create_main_user(self):
        return User.objects.create_user(
            username='kennypinchao@hotmail.com',
            password='12345678',
            first_name='Kenny',
            last_name='Pinchao',
            investigation_camp='Artificial Intelligence',
            institution='Universidad Técnica del Norte',
            interests=(
                'Passionate about AI, Machine Learning, recommendation systems and scalable '
                'software architectures. Researching social consensus algorithms, vector-based '
                'personalisation and NLP techniques for academic social networks.'
            ),
            is_active=True,
        )

    def _create_researchers(self):
        researchers = []
        for email, first, last, field, inst, interests in RESEARCHER_PROFILES:
            r = User.objects.create_user(
                username=email,
                password='password123',
                first_name=first,
                last_name=last,
                investigation_camp=field,
                institution=inst,
                interests=interests,
                is_active=True,
            )
            researchers.append(r)
        return researchers

    # ─────────────────────────────────────────────────────────────────────
    # COMPANIES
    # ─────────────────────────────────────────────────────────────────────
    def _create_companies(self):
        companies = []
        for name, industry, desc, website in COMPANY_PROFILES:
            c = Company.objects.create_user(
                username=f'contact@{name.lower().replace(" ", "")}.com',
                password='password123',
                company_name=name,
                industry=industry,
                description=desc,
                website=website,
                phone=f'+1-555-{random.randint(1000, 9999)}',
                address=f'{random.randint(100, 999)} Innovation Blvd, Tech District',
                is_active=True,
            )
            companies.append(c)
        return companies

    # ─────────────────────────────────────────────────────────────────────
    # JOBS
    # ─────────────────────────────────────────────────────────────────────
    def _create_jobs(self, companies):
        jobs = []
        for title, desc, reqs, benefits, level, s_min, s_max, remote, loc in JOB_POSTINGS:
            company = random.choice(companies)
            j = Jobs.objects.create(
                title=title,
                description=desc,
                requirements=reqs,
                benefits=benefits,
                company=company,
                location=loc,
                job_type='full_time',
                experience_level=level,
                salary_min=s_min,
                salary_max=s_max,
                is_remote=remote,
                view_count=random.randint(50, 500),
                application_count=random.randint(5, 60),
            )
            jobs.append(j)
        return jobs

    # ─────────────────────────────────────────────────────────────────────
    # POSTS
    # ─────────────────────────────────────────────────────────────────────
    def _create_posts(self, kenny, researchers, all_users):
        posts = []
        now = timezone.now()

        # Generic posts – each authored by a random researcher
        for content, tags in GENERIC_POSTS:
            author = random.choice(researchers)
            post = FeedPost.objects.create(
                author=author,
                content=content,
                tags=tags,
                is_public=True,
                created_at=now - timedelta(
                    days=random.randint(0, 14),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
                views_count=random.randint(20, 400),
                likes_count=0,
                comments_count=0,
                shares_count=random.randint(0, 8),
            )
            posts.append(post)

        # Kenny's own posts – more recent
        for content, tags in KENNY_POSTS:
            post = FeedPost.objects.create(
                author=kenny,
                content=content,
                tags=tags,
                is_public=True,
                created_at=now - timedelta(
                    days=random.randint(0, 3),
                    hours=random.randint(0, 12),
                ),
                views_count=random.randint(80, 600),
                likes_count=0,
                comments_count=0,
                shares_count=random.randint(2, 12),
            )
            posts.append(post)

        return posts

    # ─────────────────────────────────────────────────────────────────────
    # INTERACTIONS (comments + likes)
    # ─────────────────────────────────────────────────────────────────────
    def _create_interactions(self, kenny, researchers, all_users, posts):
        post_ct = ContentType.objects.get_for_model(FeedPost)
        comment_ct = ContentType.objects.get_for_model(Comment)
        total_comments = 0
        total_likes = 0

        for post in posts:
            # ── LIKES on post ──
            num_likes = random.randint(3, min(12, len(all_users)))
            likers = random.sample(all_users, num_likes)
            for liker in likers:
                if liker.id != post.author_id:
                    Like.objects.create(
                        user=liker,
                        content_type=post_ct,
                        object_id=post.id,
                    )
                    total_likes += 1

            # ── COMMENTS on post ──
            num_comments = random.randint(1, 5)
            commenters = random.sample(all_users, min(num_comments, len(all_users)))
            created_comments = []
            for commenter in commenters:
                if commenter.id == post.author_id:
                    continue
                text = random.choice(COMMENT_POOL)
                c = Comment.objects.create(
                    post=post,
                    author=commenter,
                    content=text,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 72)),
                )
                created_comments.append(c)
                total_comments += 1

                # 30 % chance of a reply to this comment
                if random.random() < 0.3 and len(all_users) > 2:
                    replier = random.choice([u for u in all_users if u.id != commenter.id])
                    reply = Comment.objects.create(
                        post=post,
                        author=replier,
                        content=random.choice(COMMENT_POOL),
                        parent_comment=c,
                        created_at=c.created_at + timedelta(hours=random.randint(1, 24)),
                    )
                    total_comments += 1
                    c.replies_count = 1
                    c.save(update_fields=['replies_count'])

                    # Like on the reply
                    Like.objects.create(user=commenter, content_type=comment_ct, object_id=reply.id)
                    reply.likes_count = 1
                    reply.save(update_fields=['likes_count'])
                    total_likes += 1

                # 50 % chance Kenny likes the comment
                if random.random() < 0.5 and commenter.id != kenny.id:
                    Like.objects.create(user=kenny, content_type=comment_ct, object_id=c.id)
                    c.likes_count = (c.likes_count or 0) + 1
                    c.save(update_fields=['likes_count'])
                    total_likes += 1

            # Kenny adds a comment on ~40 % of other people's posts
            if post.author_id != kenny.id and random.random() < 0.4:
                kenny_c = Comment.objects.create(
                    post=post,
                    author=kenny,
                    content=random.choice(KENNY_COMMENTS),
                    created_at=post.created_at + timedelta(hours=random.randint(2, 48)),
                )
                total_comments += 1

            # Update post counters accurately
            actual_likes = Like.objects.filter(content_type=post_ct, object_id=post.id).count()
            actual_comments = Comment.objects.filter(post=post).count()
            post.likes_count = actual_likes
            post.comments_count = actual_comments
            post.save(update_fields=['likes_count', 'comments_count'])

            # Recalculate engagement score
            post.update_engagement_score()

        return total_comments, total_likes

    # ─────────────────────────────────────────────────────────────────────
    # POLLS
    # ─────────────────────────────────────────────────────────────────────
    def _create_polls(self, kenny, all_users, posts):
        """Create polls attached to some of Kenny's posts, with votes from various users."""
        kenny_posts = [p for p in posts if p.author_id == kenny.id]
        polls_created = 0

        for idx, (question, options_text, is_multi) in enumerate(POLL_DATA):
            if idx >= len(kenny_posts):
                break

            target_post = kenny_posts[idx]

            poll = Poll.objects.create(
                question=question,
                is_multiple_choice=is_multi,
                is_anonymous=False,
                allows_other=False,
                is_active=True,
            )

            option_objs = []
            for order, text in enumerate(options_text):
                opt = PollOption.objects.create(poll=poll, text=text, order=order)
                option_objs.append(opt)

            # Attach poll to post
            target_post.poll = poll
            target_post.save(update_fields=['poll'])

            # Cast votes from random users
            voters = random.sample(all_users, min(random.randint(6, 12), len(all_users)))
            for voter in voters:
                if is_multi:
                    # vote for 1-3 options
                    chosen = random.sample(option_objs, random.randint(1, min(3, len(option_objs))))
                else:
                    chosen = [random.choice(option_objs)]

                for opt in chosen:
                    try:
                        PollVote.objects.create(user=voter, poll=poll, option=opt)
                        opt.votes_count += 1
                        opt.save(update_fields=['votes_count'])
                    except Exception:
                        pass  # unique constraint – voter already voted this option

            polls_created += 1

        return polls_created

    # ─────────────────────────────────────────────────────────────────────
    # POSTULANTS
    # ─────────────────────────────────────────────────────────────────────
    def _create_postulants(self, kenny, researchers, jobs):
        total = 0
        # Kenny applies to some jobs
        kenny_jobs = random.sample(jobs, min(3, len(jobs)))
        for job in kenny_jobs:
            try:
                Postulants.objects.create(user=kenny, job=job)
                total += 1
            except Exception:
                pass

        # Other researchers apply randomly
        for researcher in researchers:
            apply_jobs = random.sample(jobs, random.randint(0, 3))
            for job in apply_jobs:
                try:
                    Postulants.objects.create(user=researcher, job=job)
                    total += 1
                except Exception:
                    pass

        return total

    # ─────────────────────────────────────────────────────────────────────
    # EMBEDDINGS
    # ─────────────────────────────────────────────────────────────────────
    def _update_embeddings(self, all_users, posts, jobs):
        try:
            from apps.feeds.domain.services.feed_service import FeedService
            from apps.custom_auth.domain.services.user_vector_service import user_vector_service

            feed_service = FeedService()

            # Post embeddings
            ok, fail = 0, 0
            for post in posts:
                try:
                    feed_service.update_post_embedding(post.id)
                    ok += 1
                except Exception as e:
                    fail += 1
            self.stdout.write(f'  📄 Post embeddings: {ok} OK, {fail} failed')

            # User embeddings
            ok, fail = 0, 0
            for user in all_users:
                try:
                    user_vector_service.update_user_feed_embedding(user.id)
                    user_vector_service.update_user_job_embedding(user.id)
                    ok += 1
                except Exception as e:
                    fail += 1
            self.stdout.write(f'  👤 User embeddings: {ok} OK, {fail} failed')

            # Job embeddings (if the service supports it)
            try:
                from apps.jobs.domain.services.vector_recommendation_service import VectorRecommendationService
                vec_service = VectorRecommendationService()
                ok, fail = 0, 0
                for job in jobs:
                    try:
                        vec_service.update_job_embedding(job.id)
                        ok += 1
                    except Exception:
                        fail += 1
                self.stdout.write(f'  💼 Job embeddings: {ok} OK, {fail} failed')
            except ImportError:
                self.stdout.write(self.style.WARNING('  ⚠️  Job embedding service not available'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Embedding generation failed: {e}'))
            self.stdout.write(self.style.WARNING('  💡 Run again later or use --no-embeddings'))

    # ─────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    def _print_summary(self, kenny, researchers, companies, jobs, posts):
        self.stdout.write(self.style.SUCCESS('\n' + '═' * 60))
        self.stdout.write(self.style.SUCCESS('  🎉  PRESENTATION DATA READY'))
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(f'  👤 Main user   : kennypinchao@hotmail.com / 12345678')
        self.stdout.write(f'  👥 Researchers : {len(researchers)} (password: password123)')
        self.stdout.write(f'  🏢 Companies   : {len(companies)} (password: password123)')
        self.stdout.write(f'  💼 Jobs        : {len(jobs)}')
        self.stdout.write(f'  📝 Posts       : {FeedPost.objects.count()}')
        self.stdout.write(f'  💬 Comments    : {Comment.objects.count()}')
        self.stdout.write(f'  ❤️  Likes       : {Like.objects.count()}')
        self.stdout.write(f'  📊 Polls       : {Poll.objects.count()}')
        self.stdout.write(self.style.SUCCESS('═' * 60 + '\n'))
