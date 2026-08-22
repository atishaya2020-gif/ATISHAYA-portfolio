from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from portfolio.models import (
    Education,
    Profile,
    ProfileFocus,
    Project,
    ProjectArchitecture,
    ProjectFeature,
    Technology,
)

TECHNOLOGY_CATALOG = [
    ('Python', Technology.Category.BACKEND),
    ('Django', Technology.Category.BACKEND),
    ('Django REST Framework', Technology.Category.BACKEND),
    ('REST APIs', Technology.Category.BACKEND),
    ('JWT Authentication', Technology.Category.BACKEND),
    ('Django ORM', Technology.Category.BACKEND),
    ('React', Technology.Category.FRONTEND),
    ('JavaScript', Technology.Category.FRONTEND),
    ('TypeScript', Technology.Category.FRONTEND),
    ('Vite', Technology.Category.FRONTEND),
    ('React Router', Technology.Category.FRONTEND),
    ('Axios', Technology.Category.FRONTEND),
    ('Tailwind CSS', Technology.Category.FRONTEND),
    ('Framer Motion', Technology.Category.FRONTEND),
    ('PostgreSQL', Technology.Category.DATABASE),
    ('SQLite', Technology.Category.DATABASE),
    ('Neon PostgreSQL', Technology.Category.DATABASE),
    ('Render', Technology.Category.CLOUD_DEPLOYMENT),
    ('Vercel', Technology.Category.CLOUD_DEPLOYMENT),
    ('Cloudinary', Technology.Category.CLOUD_DEPLOYMENT),
    ('Gunicorn', Technology.Category.CLOUD_DEPLOYMENT),
    ('WhiteNoise', Technology.Category.CLOUD_DEPLOYMENT),
    ('Git', Technology.Category.TOOLS),
    ('GitHub', Technology.Category.TOOLS),
    ('Postman', Technology.Category.TOOLS),
    ('Django 6', Technology.Category.BACKEND),
    ('Django 5.2', Technology.Category.BACKEND),
    ('Django Authentication', Technology.Category.BACKEND),
    ('Django Templates', Technology.Category.BACKEND),
    ('Django Forms', Technology.Category.BACKEND),
    ('Django Filter', Technology.Category.BACKEND),
    ('React 19', Technology.Category.FRONTEND),
    ('React Hot Toast', Technology.Category.FRONTEND),
    ('Lucide React', Technology.Category.FRONTEND),
]

PROJECTS = [
    {
        'title': 'Aurora',
        'subtitle': 'E-Commerce Platform',
        'slug': 'aurora',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'featured': True,
        'order': 1,
        'github_url': 'https://github.com/atishaya2020-gif/aurora-ecommerce',
        'live_url': 'https://aurora-ecommerce.onrender.com',
        'api_url': '',
        'short_description': 'A full-stack Django e-commerce platform built around real-world backend functionality.',
        'full_description': 'Aurora is a full-stack Django e-commerce platform built around real-world backend functionality. It includes product management, categories, search, sorting, shopping carts, wishlists, orders, reviews, ratings, authentication, an administrative dashboard, and REST APIs.',
        'overview': 'A full-stack Django e-commerce platform combining product management, shopping functionality, user features, administration, and a REST API.',
        'architecture': [
            'Django models and application logic handle products, categories, carts, wishlists, reviews, ratings and orders.',
            'Django REST Framework provides CRUD APIs with search, filtering and ordering.',
            'PostgreSQL provides persistent application data, with Neon used for hosted PostgreSQL infrastructure.',
            'Cloudinary handles uploaded media.',
            'Gunicorn and WhiteNoise support production deployment on Render.',
        ],
        'features': [
            'Product catalog',
            'Categories',
            'Product search',
            'Price sorting',
            'Product detail pages',
            'Product images',
            'Customer reviews',
            'Rating system',
            'User registration and login',
            'User profiles',
            'Shopping cart',
            'Wishlist',
            'Orders',
            'Order history',
            'Admin dashboard',
            'Product, user and order management',
            'Revenue statistics',
            'Top-product statistics',
            'REST API',
            'CRUD API operations',
            'API search, filtering and ordering',
        ],
        'technologies': [
            'Python',
            'Django 6',
            'Django REST Framework',
            'PostgreSQL',
            'Neon PostgreSQL',
            'Cloudinary',
            'Gunicorn',
            'WhiteNoise',
            'Git',
            'GitHub',
        ],
    },
    {
        'title': 'Pulse',
        'subtitle': 'Full-Stack Social Media Platform',
        'slug': 'pulse',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'featured': True,
        'order': 2,
        'github_url': 'https://github.com/atishaya2020-gif/django-react-social-media',
        'live_url': 'https://django-react-social-media.vercel.app',
        'api_url': 'https://django-react-social-media.onrender.com',
        'short_description': 'A full-stack social media platform built with React and Django REST Framework.',
        'full_description': 'Pulse is a full-stack social media application built with React and Django REST Framework. Users can register, authenticate with JWT, create posts with images, like posts, comment, manage profiles, follow users, and search and filter content.',
        'overview': 'A full-stack social media application connecting a React frontend to a Django REST API with JWT authentication, PostgreSQL and cloud media storage.',
        'architecture': [
            'React provides the frontend application and user interface.',
            'Axios communicates with the Django REST API.',
            'JWT authentication handles access and refresh tokens.',
            'Django REST Framework provides the API layer.',
            'Django Filter, search and ordering support API content discovery.',
            'PostgreSQL/Neon stores application data.',
            'Cloudinary handles profile and post media.',
            'Vercel hosts the frontend while Render hosts the backend API.',
        ],
        'features': [
            'User registration',
            'Login and authentication',
            'JWT access and refresh tokens',
            'Automatic JWT token refresh',
            'Text posts',
            'Image posts',
            'Likes and unlikes',
            'Comments',
            'User profiles',
            'Follow and unfollow',
            'Search',
            'Filtering',
            'Ordering',
            'Responsive React interface',
            'Cloud media storage',
            'REST API',
        ],
        'technologies': [
            'React 19',
            'Vite',
            'React Router',
            'Axios',
            'Framer Motion',
            'Tailwind CSS',
            'React Hot Toast',
            'Lucide React',
            'Django',
            'Django REST Framework',
            'JWT Authentication',
            'Django Filter',
            'PostgreSQL',
            'Neon PostgreSQL',
            'Cloudinary',
            'Render',
            'Vercel',
        ],
    },
    {
        'title': 'Django Blog',
        'subtitle': 'Production Blogging Platform',
        'slug': 'django-blog',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'featured': True,
        'order': 3,
        'github_url': 'https://github.com/atishaya2020-gif/django-blog',
        'live_url': 'https://django-blog-vy9y.onrender.com',
        'api_url': '',
        'short_description': 'A production-deployed Django blogging platform with authentication, content management and social interactions.',
        'full_description': 'A Django blogging platform featuring authentication, post management, categories, comments, likes, image uploads, cloud-backed media storage and PostgreSQL deployment.',
        'overview': 'A Django blogging platform demonstrating authentication, content management, social interactions, media handling and production deployment.',
        'architecture': [
            'Django templates provide the server-rendered frontend.',
            'Django ORM models posts, categories, comments and likes.',
            'Authentication protects user-specific actions.',
            'Author ownership checks protect post editing and deletion.',
            'Cloudinary handles uploaded blog images.',
            'PostgreSQL is used for production data storage.',
            'Gunicorn and WhiteNoise support production deployment on Render.',
        ],
        'features': [
            'User registration',
            'Login and logout',
            'User profiles',
            'Create posts',
            'Edit posts',
            'Delete posts',
            'Categories',
            'Category filtering',
            'Search',
            'Comments',
            'Likes and unlikes',
            'Image uploads',
            'Author ownership protection',
            'Django Admin',
            'PostgreSQL production database',
            'Cloudinary media storage',
            'Production deployment',
        ],
        'technologies': [
            'Python',
            'Django 5.2',
            'Django ORM',
            'Django Authentication',
            'Django Templates',
            'PostgreSQL',
            'SQLite',
            'Cloudinary',
            'Gunicorn',
            'WhiteNoise',
            'Render',
            'Git',
            'GitHub',
        ],
    },
    {
        'title': 'E-Library',
        'subtitle': 'Digital Library Platform',
        'slug': 'e-library',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'featured': False,
        'order': 4,
        'github_url': 'https://github.com/atishaya2020-gif/E-Library-Django',
        'live_url': 'https://e-library-django-82z7.onrender.com/',
        'api_url': '',
        'short_description': 'A Django-powered digital library for discovering, uploading and reading PDF books.',
        'full_description': 'A Django-powered digital library application where authenticated users can upload books, explore available books, search and filter the library, and read or download PDF files online.',
        'overview': 'A Django digital library focused on authenticated book contributions, search, filtering, PDF handling and cloud-backed media storage.',
        'architecture': [
            'Django models represent books, categories and authors.',
            'Session authentication protects user contribution features.',
            'Django forms handle book creation and editing.',
            'PDF uploads are handled through Django file fields.',
            'Cloudinary provides cloud-backed media storage.',
            'PostgreSQL supports production deployment.',
            'Gunicorn and WhiteNoise support deployment on Render.',
        ],
        'features': [
            'User registration',
            'Login and logout',
            'Session authentication',
            'Book uploads',
            'Book metadata',
            'Categories',
            'Search',
            'Category filtering',
            'Book exploration',
            'Book details',
            'Online PDF viewing',
            'PDF downloads',
            'User-specific contributions',
            'Edit uploaded books',
            'Delete uploaded books',
            'Cloud media storage',
            'Production deployment',
        ],
        'technologies': [
            'Python',
            'Django 5.2',
            'Django Authentication',
            'PostgreSQL',
            'SQLite',
            'Cloudinary',
            'Gunicorn',
            'WhiteNoise',
            'Render',
            'Git',
            'GitHub',
        ],
    },
    {
        'title': 'Student Management System',
        'subtitle': 'Django Student Management Application',
        'slug': 'student-management',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'featured': False,
        'order': 5,
        'github_url': 'https://github.com/atishaya2020-gif/student-management-django',
        'live_url': 'https://student-management-django-hp5s.onrender.com',
        'api_url': '',
        'short_description': 'A Django and PostgreSQL application for managing user-specific student records.',
        'full_description': 'A Django and PostgreSQL application for managing user-specific student records with authentication, CRUD operations, search, pagination and a profile view.',
        'overview': 'A Django application demonstrating authenticated CRUD operations, user-scoped records, search, pagination and PostgreSQL deployment.',
        'architecture': [
            'Django models store student records associated with authenticated users.',
            'Django Forms handle student creation and editing.',
            'Authentication protects student-management pages.',
            'Query filtering scopes records to the current user.',
            'Search and pagination support the student listing.',
            'Neon PostgreSQL provides hosted database infrastructure.',
            'Gunicorn and WhiteNoise support production deployment.',
        ],
        'features': [
            'User registration',
            'Authentication',
            'User-specific student records',
            'Add student',
            'Edit student',
            'Delete student',
            'Search',
            'Pagination',
            'Profile',
            'Student count',
            'Protected pages',
            'PostgreSQL deployment',
        ],
        'technologies': [
            'Python',
            'Django 6',
            'Django Authentication',
            'Django Forms',
            'Django ORM',
            'PostgreSQL',
            'Neon PostgreSQL',
            'Gunicorn',
            'WhiteNoise',
            'Render',
            'Git',
            'GitHub',
        ],
    },
]

PROFILE = {
    'name': 'Atishaya Jain',
    'role': 'Backend-Focused Developer',
    'introduction': 'Backend-focused developer who likes building things from the ground up — turning ideas into working systems and learning through the process.',
    'philosophy': 'I like building things from the ground up — turning ideas into working systems and learning through the process.',
    'career_goal': 'I want a career where I can build real software, keep learning, work on meaningful systems, and have opportunities to work in different places and environments.',
    'current_focus': 'Django REST Framework and API development\nBackend systems',
    'what_i_build': 'Production-deployed Django applications with PostgreSQL\nREST APIs with JWT authentication and filtering/ordering\nFull-stack apps where React talks to a Django API',
}

EDUCATION = [
    {
        'label': 'B.Tech CSE — 2nd Year · 3rd Semester',
        'title': 'CGC Landran',
        'description': 'Specialisation in IoT with Cybersecurity including Blockchain.',
        'order': 1,
    },
]

PROFILE_FOCUS = [
    {'label': 'Focus', 'value': 'Backend systems', 'order': 1},
    {'label': 'Learning', 'value': 'DRF & APIs', 'order': 2},
    {'label': 'Year', 'value': '2nd · Sem 3', 'order': 3},
]


class Command(BaseCommand):
    help = 'Seed real portfolio content.'

    @transaction.atomic
    def handle(self, *args, **options):
        technology_map = self.seed_technologies()
        self.seed_projects(technology_map)
        self.seed_profile()
        self.stdout.write(self.style.SUCCESS('Portfolio seed complete.'))
        self.stdout.write(f'Projects seeded: {len(PROJECTS)}')
        self.stdout.write(f'Technologies seeded: {len(TECHNOLOGY_CATALOG)}')
        self.stdout.write('Profile seeded: 1')
        self.stdout.write(f'Education records seeded: {len(EDUCATION)}')
        self.stdout.write(f'Profile focus records seeded: {len(PROFILE_FOCUS)}')

    def seed_technologies(self):
        technology_map = {}
        order_by_category = {}
        for name, category in TECHNOLOGY_CATALOG:
            order_by_category[category] = order_by_category.get(category, 0) + 1
            technology, _ = Technology.objects.update_or_create(
                slug=slugify(name),
                defaults={
                    'name': name,
                    'category': category,
                    'description': '',
                    'order': order_by_category[category],
                },
            )
            technology_map[name] = technology
        return technology_map

    def seed_projects(self, technology_map):
        _reserved = {'features', 'architecture', 'technologies'}
        for project_data in PROJECTS:
            defaults = {k: v for k, v in project_data.items() if k not in _reserved}
            project, _ = Project.objects.update_or_create(
                slug=defaults['slug'],
                defaults=defaults,
            )
            project.technologies.set(
                [technology_map[name] for name in project_data['technologies']]
            )
            project.features.all().delete()
            ProjectFeature.objects.bulk_create(
                ProjectFeature(project=project, text=text, order=index)
                for index, text in enumerate(project_data['features'], start=1)
            )
            project.architecture_items.all().delete()
            ProjectArchitecture.objects.bulk_create(
                ProjectArchitecture(project=project, text=text, order=index)
                for index, text in enumerate(project_data['architecture'], start=1)
            )

    def seed_profile(self):
        profile = Profile.objects.order_by('id').first()
        if profile is None:
            profile = Profile.objects.create(**PROFILE)
        else:
            for field, value in PROFILE.items():
                setattr(profile, field, value)
            profile.save()

        profile.education.all().delete()
        Education.objects.bulk_create(
            Education(profile=profile, **education)
            for education in EDUCATION
        )

        profile.focus_items.all().delete()
        ProfileFocus.objects.bulk_create(
            ProfileFocus(profile=profile, **focus)
            for focus in PROFILE_FOCUS
        )
