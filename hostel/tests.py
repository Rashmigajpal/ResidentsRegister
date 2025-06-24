from django.test import TestCase, Client
from django.urls import reverse
from .models import Hosteller, Hostel, EntryExitLog,MessDetail, Feedback, Complaint, Attendance, LeavePass, Payment
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.conf import settings
import json

import os
from PIL import Image
import io
import qrcode
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.core import mail
from django.utils.timezone import now
import os
from PIL import Image

import os
from PIL import Image
import io
import qrcode

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.hostel = Hostel.objects.create(name="Test Hostel", address="123 Test Address")

        self.hosteller = Hosteller.objects.create(
            name='Test Hosteller',
            roll_number='123ABC',
            password='testpass123',  # Will be hashed in save()
            hostel=self.hostel
        )

        # Create an admin user for admin_dashboard test
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', is_staff=True)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_admin_dashboard_as_admin(self):
        # Create a Django admin user
        admin_user = User.objects.create_user(username='admin', password='adminpass', is_staff=True)

        # Login the admin user
        self.client.login(username='admin', password='adminpass')

        # Call the admin_dashboard view
        response = self.client.get(reverse('admin_dashboard'))

        # Assert that the page loads correctly
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_as_non_admin(self):
        self.client.logout()
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to home

    def test_logout_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('logout_view'))
        self.assertEqual(response.status_code, 302)  # Should redirect to home

    def test_register_hosteller_get(self):
        response = self.client.get(reverse('register_hosteller'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hostel/register_hosteller.html')

    def test_login_hosteller_fail(self):
        response = self.client.post(reverse('login_hosteller'), {
            'roll_number': 'wrong',
            'password': 'wrong'
        })
        self.assertContains(response, 'Invalid roll number or password.')

    def test_login_hosteller_success(self):
        Hosteller.objects.create(
            name="Test User",
            roll_number="123ABC",
            password="hostel123",
            hostel=self.hostel,
            email="test@example.com"
        )

        response = self.client.post(reverse('login_hosteller'), {
            'roll_number': '123ABC',
            'password': 'hostel123'
        })

        self.assertEqual(response.status_code, 302)  # or 200 depending on redirect

    def test_get_hosteller_from_session(self):
        request = HttpRequest()

        # Dummy get_response function
        middleware = SessionMiddleware(get_response=lambda req: None)
        middleware.process_request(request)
        request.session.save()

        request.session['hosteller_id'] = self.hosteller.roll_number

        from hostel.views import get_hosteller_from_session
        hosteller = get_hosteller_from_session(request)

        self.assertEqual(hosteller.roll_number, self.hosteller.roll_number)

    def setUp(self):
        self.client = Client()
        self.hostel = Hostel.objects.create(name="Test Hostel", address="Test Address")

        self.hosteller = Hosteller.objects.create(
            name="Test User",
            roll_number="ROLL123",
            password="12345",
            hostel=self.hostel,
            email="test@example.com"
        )

    def test_generate_qr_code_view(self):
        response = self.client.get(reverse('generate_qr_code', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Hosteller.objects.get(roll_number="ROLL123").qr_image.startswith("qr_codes/"))

    def test_scan_qr_code_entry_exit(self):
        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("qr.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'college'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EntryExitLog.objects.filter(hosteller=self.hosteller).count(), 1)

    def test_scan_exit_after_entry(self):
        EntryExitLog.objects.create(hosteller=self.hosteller, entry_time=timezone.now(), venue="gate")
        self.hosteller.is_inside = True
        self.hosteller.save()

        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("qr_exit.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'gate'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(EntryExitLog.objects.get(hosteller=self.hosteller).exit_time)

    def test_invalid_qr_code_scan(self):
        invalid_qr = qrcode.make("INVALID_ROLL")
        img_byte_arr = io.BytesIO()
        invalid_qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("invalid_qr.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'hostel'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('scan_qr_code'))

    def test_generate_qr_code_view(self):
        response = self.client.get(reverse('generate_qr_code', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 302)  # Redirect to hosteller_list
        updated_hosteller = Hosteller.objects.get(roll_number="ROLL123")
        self.assertTrue(updated_hosteller.qr_image.startswith("qr_codes/"))

    def test_scan_qr_code_entry_exit(self):
        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile(
            "qr.png",
            img_byte_arr.read(),
            content_type="image/png"
        )

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'college'
        })
        self.assertEqual(response.status_code, 302)

        logs = EntryExitLog.objects.filter(hosteller=self.hosteller)
        self.assertEqual(logs.count(), 1)
        self.assertTrue(logs.first().entry_time)

    def test_scan_exit_after_entry(self):
        EntryExitLog.objects.create(hosteller=self.hosteller, entry_time=timezone.now(), venue="gate")
        self.hosteller.is_inside = True
        self.hosteller.save()

        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile(
            "qr_exit.png",
            img_byte_arr.read(),
            content_type="image/png"
        )

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'gate'
        })
        self.assertEqual(response.status_code, 302)

        log = EntryExitLog.objects.get(hosteller=self.hosteller)
        self.assertIsNotNone(log.exit_time)

    def test_invalid_qr_code_scan(self):
        invalid_qr = qrcode.make("INVALID_ROLL")
        img_byte_arr = io.BytesIO()
        invalid_qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile(
            "invalid_qr.png",
            img_byte_arr.read(),
            content_type="image/png"
        )

        response = self.client.post(reverse('scan_qr_code'), {
            'qr_code': uploaded_file,
            'venue': 'hostel'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('scan_qr_code'))

    def test_hosteller_detail_view(self):
        response = self.client.get(reverse('hosteller_detail', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hosteller.name)

    def test_delete_hosteller_view(self):
        response = self.client.post(reverse('delete_hosteller', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Hosteller.DoesNotExist):
            Hosteller.objects.get(roll_number=self.hosteller.roll_number)

    def test_download_profile_view(self):
        response = self.client.get(reverse('download_profile', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generate_qr_code_view(self):
        response = self.client.get(reverse('generate_qr_code', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 302)
        updated_hosteller = Hosteller.objects.get(roll_number="ROLL123")
        self.assertTrue(updated_hosteller.qr_image.startswith("qr_codes/"))

    def test_scan_qr_code_entry_exit(self):
        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("qr.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {'qr_code': uploaded_file, 'venue': 'college'})
        self.assertEqual(response.status_code, 302)

        logs = EntryExitLog.objects.filter(hosteller=self.hosteller)
        self.assertEqual(logs.count(), 1)
        self.assertTrue(logs.first().entry_time)

    def test_scan_exit_after_entry(self):
        EntryExitLog.objects.create(hosteller=self.hosteller, entry_time=timezone.now(), venue="gate")
        self.hosteller.is_inside = True
        self.hosteller.save()

        qr = qrcode.make(self.hosteller.roll_number)
        img_byte_arr = io.BytesIO()
        qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("qr_exit.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {'qr_code': uploaded_file, 'venue': 'gate'})
        self.assertEqual(response.status_code, 302)

        log = EntryExitLog.objects.get(hosteller=self.hosteller)
        self.assertIsNotNone(log.exit_time)

    def test_invalid_qr_code_scan(self):
        invalid_qr = qrcode.make("INVALID_ROLL")
        img_byte_arr = io.BytesIO()
        invalid_qr.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        uploaded_file = SimpleUploadedFile("invalid_qr.png", img_byte_arr.read(), content_type="image/png")

        response = self.client.post(reverse('scan_qr_code'), {'qr_code': uploaded_file, 'venue': 'hostel'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('scan_qr_code'))

    def test_hosteller_detail_view(self):
        response = self.client.get(reverse('hosteller_detail', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hosteller.name)



    def test_delete_hosteller_view(self):
        response = self.client.post(reverse('delete_hosteller', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Hosteller.objects.filter(roll_number=self.hosteller.roll_number).exists())

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard', args=[self.hosteller.roll_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hosteller.name)

    def test_mess_detail_view(self):
        response = self.client.get(reverse('mess_details_view'))
        self.assertEqual(response.status_code, 200)



    def test_submit_attendance_view(self):
        response = self.client.post(reverse('submit_attendance', args=[self.hosteller.roll_number]), {
            'date': timezone.now().date(),
            'status': 'Present'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Attendance.objects.filter(hosteller=self.hosteller).exists())



    def test_submit_payment_view(self):
        response = self.client.post(reverse('submit_payment', args=[self.hosteller.roll_number]), {
            'amount': '1000.00',
            'payment_type': 'mess',
            'transaction_id': 'TXN123456',
            'payment_status': 'pending',
            'check_status': 'pending'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Payment.objects.filter(hosteller=self.hosteller).exists())

    def test_manage_attendance_view(self):
        response = self.client.get(reverse('manage_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_students', response.context)

    def test_manage_payment_query_view(self):
        response = self.client.get(reverse('manage_payment_query'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_view(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_announcement_list_view(self):
        response = self.client.get(reverse('announcement_list'))
        self.assertEqual(response.status_code, 200)

    def test_manage_announcements_get(self):
        response = self.client.get(reverse('manage_announcements'))
        self.assertEqual(response.status_code, 200)

    def test_manage_announcements_post(self):
        response = self.client.post(reverse('manage_announcements'), {
            'title': 'Test Announcement',
            'content': 'Important notice.'
        })
        self.assertEqual(response.status_code, 302)

    def test_approval_leave_pass_view_get(self):
        response = self.client.get(reverse('approval_leave_pass'))
        self.assertEqual(response.status_code, 200)

    def test_resolve_complaint_view_get(self):
        response = self.client.get(reverse('resolve_complaint'))
        self.assertEqual(response.status_code, 200)

    def test_update_complaint_status_api(self):
        complaint = Complaint.objects.create(hosteller=self.hosteller, complaint_type='water', status='pending',
                                             description='Tap issue')
        response = self.client.post(reverse('update_complaint_status', args=[complaint.id]),
                                    data=json.dumps({'status': 'resolved'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'resolved')

    def test_update_leave_status_api(self):
        leave = LeavePass.objects.create(hosteller=self.hosteller, leave_type='personal', reason='vacation',
                                         from_date=timezone.now(), to_date=timezone.now(), status='pending')
        response = self.client.post(reverse('update_leave_status', args=[leave.id]),
                                    data=json.dumps({'status': 'approved'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        leave.refresh_from_db()
        self.assertEqual(leave.status, 'approved')

