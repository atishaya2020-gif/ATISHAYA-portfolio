import os
from io import StringIO
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient, APITestCase

from .admin import ContactMessageAdmin
from .models import ContactMessage, Profile, Project, Technology


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


class ContactEndpointTests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_valid_post_creates_contact_message_and_returns_201(self):
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Inquiry',
            'message': 'Hello, I would like to work with you.',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data,
            {'status': 'ok', 'message': 'Your message has been received.'},
        )

        msg = ContactMessage.objects.get(email='jane@example.com')
        self.assertEqual(msg.name, 'Jane Doe')
        self.assertEqual(msg.subject, 'Inquiry')
        self.assertEqual(msg.message, 'Hello, I would like to work with you.')
        self.assertFalse(msg.is_read)
        self.assertFalse(msg.is_replied)

    def test_unauthenticated_public_post_works(self):
        payload = {
            'name': 'Public User',
            'email': 'public@example.com',
            'message': 'Public message test.',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)

    def test_required_fields(self):
        res = self.client.post(
            '/api/contact/',
            {'email': 'a@b.com', 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('name', res.data)

        res = self.client.post(
            '/api/contact/',
            {'name': 'A', 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('email', res.data)

        res = self.client.post(
            '/api/contact/',
            {'name': 'A', 'email': 'a@b.com'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('message', res.data)

    def test_invalid_email_format(self):
        payload = {
            'name': 'Bad Email',
            'email': 'not-an-email',
            'message': 'Testing invalid email format.',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_whitespace_validation(self):
        payload = {
            'name': '  Padded Name  ',
            'email': '  padded@example.com  ',
            'subject': '  Padded Subject  ',
            'message': '  Padded message text.  ',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        msg = ContactMessage.objects.get(email='padded@example.com')
        self.assertEqual(msg.name, 'Padded Name')
        self.assertEqual(msg.subject, 'Padded Subject')
        self.assertEqual(msg.message, 'Padded message text.')

        res = self.client.post(
            '/api/contact/',
            {'name': '   ', 'email': 'test@example.com', 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

        res = self.client.post(
            '/api/contact/',
            {'name': 'Test', 'email': 'test@example.com', 'message': '   '},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_optional_subject(self):
        payload = {
            'name': 'No Subject',
            'email': 'nosubject@example.com',
            'message': 'No subject was provided.',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        msg = ContactMessage.objects.get(email='nosubject@example.com')
        self.assertEqual(msg.subject, '')

    def test_max_lengths(self):
        res = self.client.post(
            '/api/contact/',
            {'name': 'A' * 151, 'email': 'a@b.com', 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

        res = self.client.post(
            '/api/contact/',
            {'name': 'A', 'email': ('b' * 250) + '@b.com', 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

        res = self.client.post(
            '/api/contact/',
            {'name': 'A', 'email': 'a@b.com', 'subject': 'S' * 201, 'message': 'Hi'},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

        res = self.client.post(
            '/api/contact/',
            {'name': 'A', 'email': 'a@b.com', 'message': 'M' * 5001},
            format='json',
        )
        self.assertEqual(res.status_code, 400)

    def test_client_cannot_override_internal_fields(self):
        payload = {
            'name': 'Attacker',
            'email': 'attacker@example.com',
            'message': 'Trying to tamper fields.',
            'id': 9999,
            'is_read': True,
            'is_replied': True,
            'created_at': '2000-01-01T00:00:00Z',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        msg = ContactMessage.objects.get(email='attacker@example.com')
        self.assertNotEqual(msg.id, 9999)
        self.assertFalse(msg.is_read)
        self.assertFalse(msg.is_replied)
        self.assertNotIn('is_read', response.data)
        self.assertNotIn('is_replied', response.data)

    def test_get_is_rejected(self):
        response = self.client.get('/api/contact/')
        self.assertEqual(response.status_code, 405)

    def test_throttling_works(self):
        payload = {
            'name': 'Spammer',
            'email': 'spammer@example.com',
            'message': 'Repeated message.',
        }
        for _ in range(5):
            res = self.client.post('/api/contact/', payload, format='json')
            self.assertEqual(res.status_code, 201)
        res = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(res.status_code, 429)

    def test_admin_registration(self):
        self.assertTrue(admin.site.is_registered(ContactMessage))

    def test_email_notification_sent_on_valid_submission(self):
        payload = {
            'name': 'Alice Smith',
            'email': 'alice@example.com',
            'subject': 'Project Inquiry',
            'message': 'Can you build a site for me?',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn('Project Inquiry', sent_email.subject)
        self.assertIn('Alice Smith', sent_email.body)
        self.assertIn('alice@example.com', sent_email.body)
        self.assertIn('Can you build a site for me?', sent_email.body)
        self.assertEqual(sent_email.reply_to, ['alice@example.com'])

    def test_contact_message_saved_and_201_returned_when_email_fails(self):
        payload = {
            'name': 'Bob Miller',
            'email': 'bob@example.com',
            'subject': 'Failure test',
            'message': 'Testing SMTP failure handling.',
        }
        with patch(
            'portfolio.services.contact_email.EmailMessage.send',
            side_effect=Exception('SMTP connection timed out'),
        ):
            response = self.client.post('/api/contact/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data,
            {'status': 'ok', 'message': 'Your message has been received.'},
        )
        self.assertTrue(ContactMessage.objects.filter(email='bob@example.com').exists())

    def test_invalid_submissions_do_not_send_email(self):
        payload = {
            'name': 'Invalid Email User',
            'email': 'not-an-email',
            'message': 'Will fail validation.',
        }
        response = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_throttled_submissions_do_not_send_email(self):
        payload = {
            'name': 'Spammer',
            'email': 'spammer@example.com',
            'message': 'Repeated message.',
        }
        for _ in range(5):
            res = self.client.post('/api/contact/', payload, format='json')
            self.assertEqual(res.status_code, 201)

        mail.outbox.clear()

        res = self.client.post('/api/contact/', payload, format='json')
        self.assertEqual(res.status_code, 429)
        self.assertEqual(len(mail.outbox), 0)

    def test_admin_reply_link(self):
        msg = ContactMessage.objects.create(
            name='Test User',
            email='user@example.com',
            subject='Job Opportunity',
            message='Let us talk.',
        )
        admin_obj = ContactMessageAdmin(ContactMessage, admin.site)
        link = admin_obj.reply_link(msg)
        self.assertTrue('mailto:user' in link)
        self.assertIn('Reply via Email', link)
