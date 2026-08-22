import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase, APIClient

from .models import Profile, Project, Technology


class BootstrapAdminTests(TestCase):
    COMMAND = 'bootstrap_admin'

    def test_missing_env_vars_skips_safely(self):
        out = StringIO()
        with patch.dict(os.environ, {}, clear=True):
            call_command(self.COMMAND, stdout=out)
        output = out.getvalue()
        self.assertIn('skipped', output)
        self.assertEqual(User.objects.count(), 0)

    def test_first_run_creates_superuser(self):
        out = StringIO()
        env = {
            'ADMIN_USERNAME': 'testadmin',
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'secret-pass-123',
        }
        with patch.dict(os.environ, env, clear=True):
            call_command(self.COMMAND, stdout=out)
        self.assertTrue(User.objects.filter(username='testadmin').exists())
        self.assertTrue(User.objects.get(username='testadmin').is_superuser)
        self.assertIn('created successfully', out.getvalue())

    def test_second_run_does_not_duplicate(self):
        env = {
            'ADMIN_USERNAME': 'testadmin',
            'ADMIN_EMAIL': 'admin@test.com',
            'ADMIN_PASSWORD': 'secret-pass-123',
        }
        with patch.dict(os.environ, env, clear=True):
            call_command(self.COMMAND, stdout=StringIO())
            call_command(self.COMMAND, stdout=StringIO())
        self.assertEqual(User.objects.filter(username='testadmin').count(), 1)

    def test_password_never_appears_in_output(self):
        out = StringIO()
        env = {
            'ADMIN_USERNAME': 'secureadmin',
            'ADMIN_EMAIL': 'secure@test.com',
            'ADMIN_PASSWORD': 'my-super-secret-password',
        }
        with patch.dict(os.environ, env, clear=True):
            call_command(self.COMMAND, stdout=out)
        self.assertNotIn('my-super-secret-password', out.getvalue())

    def test_existing_user_password_not_overwritten(self):
        User.objects.create_user('existing', 'exist@test.com', 'old-password')
        env = {
            'ADMIN_USERNAME': 'existing',
            'ADMIN_EMAIL': 'exist@test.com',
            'ADMIN_PASSWORD': 'new-password',
        }
        out = StringIO()
        with patch.dict(os.environ, env, clear=True):
            call_command(self.COMMAND, stdout=out)
        user = User.objects.get(username='existing')
        self.assertTrue(user.check_password('old-password'))
        self.assertFalse(user.check_password('new-password'))
        self.assertIn('already exists', out.getvalue())


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
