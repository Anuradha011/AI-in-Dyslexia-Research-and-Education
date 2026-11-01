from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import ParentStudentRequest, StudentProfile


class ParentRequestAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # create admin user
        self.admin = User.objects.create_user(
            username='admin', password='pass', role='admin',
            is_staff=True, is_superuser=True
        )
        self.parent = User.objects.create_user(username='pa', password='pass', role='parent')
        self.student = User.objects.create_user(username='st', password='pass', role='student')
        self.req = ParentStudentRequest.objects.create(
            parent=self.parent, student=self.student, status='pending'
        )
        self.client.login(username='admin', password='pass')

    def test_approve_request(self):
        url = reverse('admin_panel:approve_request', args=[self.req.pk])
        resp = self.client.post(url, {'admin_note': 'ok'})
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, 'approved')
        self.assertEqual(self.req.admin_note, 'ok')
        profile = StudentProfile.objects.get(user=self.student)
        self.assertEqual(profile.parent, self.parent)

    def test_reject_request(self):
        r2 = ParentStudentRequest.objects.create(
            parent=self.parent, student=self.student, status='pending'
        )
        url = reverse('admin_panel:reject_request', args=[r2.pk])
        resp = self.client.post(url, {'admin_note': 'no'})
        r2.refresh_from_db()
        self.assertEqual(r2.status, 'rejected')
        self.assertEqual(r2.admin_note, 'no')
