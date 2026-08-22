from rest_framework.test import APITestCase

from .models import Profile, Project, Technology


class HealthEndpointTests(APITestCase):
    def test_health_returns_ok(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'ok'})


def _create_project(**overrides):
    defaults = {
        'title': 'Test Project',
        'slug': 'test-project',
        'short_description': 'A short description.',
        'category': Project.Category.FULLSTACK,
        'status': Project.Status.COMPLETED,
        'order': 0,
    }
    defaults.update(overrides)
    return Project.objects.create(**defaults)


class ProjectEndpointTests(APITestCase):
    def test_project_list_returns_200(self):
        _create_project()
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_project_detail_resolves_by_slug(self):
        _create_project(
            full_description='Long description.',
            overview='Overview text.',
        )
        response = self.client.get('/api/projects/test-project/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], 'test-project')
        self.assertIn('features', response.data)
        self.assertIn('architecture', response.data)
        self.assertIn('technologies', response.data)

    def test_featured_filter(self):
        _create_project(title='A', slug='a')
        _create_project(title='B', slug='b', featured=True)
        response = self.client.get('/api/projects/?featured=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['slug'] for item in response.data],
            ['b'],
        )

    def test_project_list_ordered_by_order_then_title(self):
        _create_project(title='Zeta', slug='zeta', order=1)
        _create_project(title='Alpha', slug='alpha', order=0)
        response = self.client.get('/api/projects/')
        self.assertEqual(
            [item['slug'] for item in response.data],
            ['alpha', 'zeta'],
        )


class TechnologyEndpointTests(APITestCase):
    def test_technology_list_returns_200(self):
        Technology.objects.create(
            name='Django',
            category=Technology.Category.BACKEND,
            slug='django',
        )
        response = self.client.get('/api/technologies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['name'], 'Django')


class ProfileEndpointTests(APITestCase):
    def test_profile_returns_200_when_profile_exists(self):
        Profile.objects.create(
            name='Test User',
            role='Developer',
            introduction='Hello.',
        )
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test User')
