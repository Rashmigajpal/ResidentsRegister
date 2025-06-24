from django.shortcuts import render
from .models import *

from PIL import Image
from pyzbar.pyzbar import decode

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.utils.timezone import now

from .forms import HostellerRegistrationForm, LeavePassForm, ComplaintForm, AttendanceForm, FeedbackForm, PaymentForm, AnnouncementForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required


import os
from django.shortcuts import get_object_or_404, redirect
import qrcode
from io import BytesIO
from django.conf import settings

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django.views import View

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.timezone import now


def logout_view(request):
    logout(request)  # Log the user out
    return redirect('home')  # Redirect to 'home' URL after logout




def home(request):
    return render(request, 'home.html')  # Create a home.html templates


@login_required
def admin_dashboard(request):
    if request.user.is_staff:
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('home')



def register_hosteller(request):
    if request.method == 'POST':
        form = HostellerRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            password = form.cleaned_data['password']

            if Hosteller.objects.filter(roll_number=roll_number).exists():
                messages.error(request, 'A hosteller with this roll number already exists.')
            else:
                hosteller = form.save(commit=False)
                hosteller.password = password  # Store password (hash it in production)
                hosteller.save()

                # Generate QR code for the newly registered hosteller
                generate_hosteller_qr_code(hosteller)

                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login_hosteller')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HostellerRegistrationForm()

    return render(request, 'hostel/register_hosteller.html', {'form': form})


def generate_hosteller_qr_code(hosteller):
    qr_data = f"{hosteller.roll_number}"  # Customize this as needed
    img = qrcode.make(qr_data)

    # Save QR code image to a BytesIO object
    img_file = BytesIO()
    img.save(img_file, format='PNG')
    img_file.seek(0)

    # Specify the static directory path
    static_directory = os.path.join(settings.BASE_DIR, 'static', 'qr_codes')
    os.makedirs(static_directory, exist_ok=True)  # Ensure the directory exists

    # Define the QR code file path
    qr_image_name = f"qr_code_{hosteller.roll_number}.png"
    qr_code_path = os.path.join(static_directory, qr_image_name)

    # Save the QR code file
    with open(qr_code_path, 'wb') as f:
        f.write(img_file.getvalue())

    # Update the hosteller's QR code field with the relative static URL
    hosteller.qr_image = f"qr_codes/{qr_image_name}"
    hosteller.save()

    print(f"QR Code saved at: {qr_code_path}")  # Debugging statement


import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Hosteller


def login_hosteller(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        password = request.POST.get('password')

        try:
            hosteller = Hosteller.objects.get(roll_number=roll_number)

            if check_password(password, hosteller.password):  # Ensure password is hashed
                request.session['hosteller_id'] = hosteller.roll_number  # Store roll number in session

                # Check if student image exists
                image_url = None
                if hosteller.student_image:
                    image_path = os.path.join(settings.MEDIA_ROOT, hosteller.student_image.name)
                    if os.path.exists(image_path):
                        image_url = hosteller.student_image.url  # Use media URL if image exists
                    else:
                        print(f"Image not found at path: {image_path}")

                return redirect('dashboard', hosteller_id=hosteller.roll_number)  # Pass ID for dashboard view
            else:
                messages.error(request, 'Invalid roll number or password.')
        except Hosteller.DoesNotExist:
            messages.error(request, 'Invalid roll number or password.')

    return render(request, 'hostel/login_hosteller.html')


def get_hosteller_from_session(request):
    hosteller_id = request.session.get('hosteller_id')
    return get_object_or_404(Hosteller, roll_number=hosteller_id) if hosteller_id else None


def hostel_list(request):
    hostels = Hostel.objects.all()
    return render(request, 'hostel_list.html', {'hostels': hostels})


def hosteller_list(request, hostel_id):
    hostel = get_object_or_404(Hostel, id=hostel_id)
    hostellers = Hosteller.objects.filter(hostel=hostel)
    total_hostellers = hostellers.count()  # Get the total count of hostellers

    return render(request, 'hosteller_list.html', {
        'hostel': hostel,
        'hostellers': hostellers,
        'total_hostellers': total_hostellers  # Pass the count to the templates
    })


import os
import qrcode
from io import BytesIO



def generate_qr_code(request, roll_number):
    hosteller = get_object_or_404(Hosteller, roll_number=roll_number)

    # Generate QR code
    qr_data = f"Name: {hosteller.name}\nRoll Number: {hosteller.roll_number}"
    img = qrcode.make(qr_data)

    # Ensure static/qr_codes/ directory exists
    qr_code_dir = os.path.join(settings.BASE_DIR, 'static', 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)

    # Save QR code in static/qr_codes/
    qr_image_name = f"qr_code_{hosteller.roll_number}.png"
    qr_code_path = os.path.join(qr_code_dir, qr_image_name)

    img.save(qr_code_path, format="PNG")  # Save the QR code


    # Store relative path to 'static/qr_codes/' in the database
    hosteller.qr_image = f"qr_codes/{qr_image_name}"  # Relative path
    hosteller.save()
    return redirect('hosteller_list', hostel_id=hosteller.hostel.id)



from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Hosteller, EntryExitLog
from pyzbar.pyzbar import decode
from PIL import Image
from django.conf import settings
from datetime import time
from decimal import Decimal

def scan_qr_code(request):
    missing_entries = []  # List to collect hostellers with missing entry logs
    now = timezone.now()
    notify_time = time(5, 3)  # Set notification time to 5:45 PM

    if request.method == 'POST':
        if 'qr_code' in request.FILES:
            qr_code_image = request.FILES['qr_code']
            img = Image.open(qr_code_image)
            decoded_objects = decode(img)

            if decoded_objects:
                qr_code = decoded_objects[0].data.decode('utf-8')

                # Attempt to retrieve the hosteller
                try:
                    hosteller = Hosteller.objects.get(roll_number=qr_code)
                except ObjectDoesNotExist:
                    messages.error(request, 'Hosteller not found.')
                    return redirect('scan_qr_code')

                # Get selected venue from form data (only used for new entry logs)
                venue = request.POST.get('venue', 'college')  # Default to 'college' if not provided

                # Get all existing logs for the hosteller
                logs = EntryExitLog.objects.filter(hosteller=hosteller).order_by('-entry_time')

                if logs.exists():
                    last_log = logs.first()  # Get the most recent log

                    if last_log.entry_time and not last_log.exit_time:
                        # If the last log has an entry time but no exit time, log it as an exit without changing the venue
                        last_log.exit_time = now
                        last_log.save()
                        hosteller.is_inside = False
                        hosteller.save()
                        messages.success(request, 'Exit logged.')
                    elif last_log.exit_time:
                        # If the last log has an exit time, create a new entry log with the selected venue
                        new_log = EntryExitLog(hosteller=hosteller, entry_time=now, venue=venue)
                        new_log.save()
                        hosteller.is_inside = True
                        hosteller.save()
                        messages.success(request, 'Entry logged.')
                else:
                    # No previous logs exist, so consider this as a new entry log
                    new_log = EntryExitLog(hosteller=hosteller, entry_time=now, venue=venue)
                    new_log.save()
                    hosteller.is_inside = True
                    hosteller.save()
                    messages.success(request, 'Entry logged for new hosteller.')

                # Only check for missing entries after 5:45 PM
                if now.time() >= notify_time:
                    hostellers_with_missing_entries = EntryExitLog.objects.filter(entry_time__isnull=True)
                    if hostellers_with_missing_entries.exists():
                        for log in hostellers_with_missing_entries:
                            missing_entries.append(log.hosteller)
                            # Add fine to hosteller’s record using Decimal for the amount
                            log.hosteller.fine += Decimal("100.00")  # Fine amount
                            log.hosteller.save()

            else:
                messages.error(request, 'No QR code found in the image.')

            # Notify admin if there are any missing entries
            if missing_entries:
                notify_admin_and_hostellers(missing_entries)

            return redirect('scan_qr_code')

    return render(request, 'scan_qr_code.html')


def notify_admin_and_hostellers(missing_entries):
    # Notify admin with list of hostellers
    subject = "Alert: Hostellers with Missing Entry Logs"
    message = (
            "The following hostellers have an exit log but are missing an entry log or have an empty entry time:\n\n"
            + "\n".join([f"{hosteller.name} - Fine: ${hosteller.fine}" for hosteller in missing_entries])
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    admin_email = settings.ADMIN_EMAIL
    send_mail(subject, message, from_email, [admin_email])

    # Notify each hosteller individually via email with fine details and reason
    for hosteller in missing_entries:
        reason = "Missed Entry Log after 5:45 PM"
        fine_message = (
            f"Dear {hosteller.name},\n\n"
            f"You have been fined ${hosteller.fine} for the following reason:\n"
            f"{reason}.\n"
            f"Please ensure timely logging in the future to avoid further fines.\n\n"
            "Thank you."
        )

        # Send fine notification email to the hosteller
        send_mail(
            subject="Fine Notification",
            message=fine_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[hosteller.email],
        )




def hosteller_detail(request, roll_number):
    hosteller = get_object_or_404(Hosteller, roll_number=roll_number)
    return render(request, 'hosteller_detail.html', {'hosteller': hosteller})


from django.conf import settings
from reportlab.lib.pagesizes import letter
import os


def download_profile(request, roll_number):
    hosteller = get_object_or_404(Hosteller, roll_number=roll_number)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{hosteller.roll_number}_profile.pdf"'

    # Create the PDF canvas
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Draw border boxes for layout
    p.setLineWidth(0)
    p.rect(50, height - 200, 200, 150)  # Box for profile image and name
    p.rect(300, height - 200, 250, 150)  # Box for details

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 50, "Hosteller Profile")

    # Profile Image Box
    if hosteller.student_image:
        try:
            image_path = os.path.join(settings.MEDIA_ROOT, hosteller.student_image.name)
            p.drawImage(image_path, 75, height - 180, width=100, height=100)
        except Exception as e:
            print(f"Error loading hosteller image: {e}")

    # Name and Position under the image
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(150, height - 230, hosteller.name)
    p.setFont("Helvetica", 10)
    p.drawCentredString(150, height - 245, f"{hosteller.branch} Department")
    p.drawCentredString(150, height - 260, f"Semester: {hosteller.semester}")

    # Hosteller Details Section
    p.setFont("Helvetica-Bold", 10)
    details = [
        ("Roll Number", hosteller.roll_number),
        ("Mobile", hosteller.mobile_number),
        ("Branch", hosteller.branch),
        ("Semester", hosteller.semester),
        ("Address", hosteller.address),
        ("Currently Inside", "Yes" if hosteller.is_inside else "No")
    ]
    y_position = height - 220
    for label, value in details:
        p.drawString(310, y_position, f"{label}: {value}")
        y_position -= 15

    # QR Code Image
    # QR Code Image
    if hosteller.qr_image:
        try:
            qr_image_path = os.path.join(settings.STATIC_ROOT, hosteller.qr_image)
            if os.path.exists(qr_image_path):  # Ensure the file exists
                p.drawImage(qr_image_path, 150, 50, width=100, height=100)
            else:
                print(f"QR image not found: {qr_image_path}")
        except Exception as e:
            print(f"Error loading QR image: {e}")

    # Finalize the PDF
    p.showPage()
    p.save()

    return response


def delete_hosteller(request, roll_number):
    hosteller = get_object_or_404(Hosteller, roll_number=roll_number)
    if request.method == 'POST':
        hosteller.delete()
        messages.success(request, 'Hosteller deleted successfully.')
        return redirect('hostel_list')  # Adjust this redirect as needed
    return render(request, 'confirm_delete.html', {'hosteller': hosteller})


#//////////////////////////management section//////////////////

from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'hostel_dashboard.html'

    def get(self, request, *args, **kwargs):
        roll_number = kwargs.get('hosteller_id')  # Adjust this based on how you capture the ID in the URL
        hosteller = get_object_or_404(Hosteller, roll_number=roll_number)  # Use roll_number instead of id

        submit_payment_url = reverse('submit_payment', args=[hosteller.roll_number])
        submit_attendance_url = reverse('submit_attendance', args=[hosteller.roll_number])
        submit_complaint_url = reverse('submit_complaint', args=[hosteller.roll_number])
        submit_feedback_url = reverse('submit_feedback', args=[hosteller.roll_number])
        submit_leave_pass_url = reverse('submit_leave_pass', args=[hosteller.roll_number])

        latest_announcements = Announcement.objects.all().order_by('-created_at')[:5]
        gallery_images = Gallery.objects.all()
        mess_details = MessDetail.objects.last()  # Fetch the most recent mess details



        # Pass the hosteller to the context
        context = {
            'hosteller': hosteller,
            'submit_payment_url': submit_payment_url ,
            'submit_attendance_url': submit_attendance_url,
            'submit_complaint_url': submit_complaint_url,
            'submit_feedback_url': submit_feedback_url,
            'submit_leave_pass_url': submit_leave_pass_url,
            'latest_announcements': latest_announcements,  # Add the latest announcements to the context
            'gallery_images': gallery_images,  # Add gallery images to the context
            'mess_details': mess_details,  # Pass mess details to templates

            # Pass URL to templates

            # add other context variables if needed
        }
        return self.render_to_response(context)


from django.shortcuts import get_object_or_404




def submit_leave_pass(request, hosteller_id):
    hosteller = Hosteller.objects.get(roll_number=hosteller_id)

    # Check if an active leave pass exists
    active_leave = LeavePass.objects.filter(hosteller=hosteller, to_date__gte=now().date()).exists()

    if active_leave:
        messages.error(request, "You already have an active leave request! Please wait until it expires or is deleted.")
        return redirect('success_page')  # Redirect to a success/error page

    if request.method == 'POST':
        form = LeavePassForm(request.POST)
        if form.is_valid():
            leave_pass = form.save(commit=False)
            leave_pass.hosteller = hosteller
            leave_pass.save()
            messages.success(request, "Leave pass submitted successfully!")
            return redirect('success_page')
        else:
            print(form.errors)


    else:
        form = LeavePassForm()

    return render(request, 'leave_pass.html', {'form': form, 'hosteller': hosteller})

def submit_complaint(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)

    if request.method == 'POST':
        print(request.POST)  # Debugging
        form = ComplaintForm(request.POST)

        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.hosteller = hosteller
            complaint.save()
            return redirect('complaint_success', hosteller_id=hosteller.roll_number)
        else:
            print("Form is invalid:", form.errors)

    else:
        form = ComplaintForm()

    return render(request, 'complaint.html', {'form': form, 'hosteller': hosteller})

def complaint_success(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)
    return render(request, 'success_complaint.html', {'hosteller':hosteller})


def submit_feedback(request, hosteller_id):
    # Get hosteller instance from the provided `hosteller_id`
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            # Send email to the developer
            subject = "New Feedback Submission"
            message = f"""
                       New Feedback Submitted:
                       Hosteller: {feedback.hosteller}
                       Comment: {feedback.comment}
                       Rating: {feedback.rating} Stars
                       """
            recipient_email = "shiva171403@gmail.com"  # Replace with the actual developer's email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

            feedback.hosteller = hosteller  # Assign hosteller
            feedback.save()
            return redirect('feedback_success', hosteller_id=hosteller.roll_number)  # Redirect after successful submission
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form, 'hosteller': hosteller})

def feedback_success(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)

    return render(request, 'success_feedback.html', {'hosteller':hosteller})


from django.db.utils import IntegrityError



def submit_attendance(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)  # Get hosteller or return 404
    today = now().date()

    # Check if attendance already exists
    if Attendance.objects.filter(hosteller=hosteller, date=today).exists():
        messages.warning(request, "⚠️ Attendance already submitted for today!")
        return redirect('attendance_success', hosteller_id=hosteller.roll_number)

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                attendance = form.save(commit=False)
                attendance.hosteller = hosteller
                attendance.date = today
                attendance.save()
                messages.success(request, "✅ Attendance recorded successfully!")
                return redirect('attendance_success', hosteller_id=hosteller.roll_number)
            except IntegrityError:
                messages.error(request, "⚠️ Duplicate entry detected! Attendance already marked.")
        else:
            messages.error(request, "❌ Invalid form submission. Please check the fields.")
            print(form.errors)  # Debugging: print form errors to console

    else:
        form = AttendanceForm()

    return render(request, 'attendance.html', {'form': form, 'hosteller': hosteller})



def attendance_success(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)
    return render(request, 'success_attendance.html', {'hosteller':hosteller})


from django.contrib import messages
from .models import Hosteller, Payment
from .forms import PaymentForm
def submit_payment(request, hosteller_id):
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)
    transaction_id = hosteller.roll_number

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)

            # Auto-fill payment details
            payment.hosteller = hosteller
            payment.transaction_id = transaction_id
            payment.payment_status = 'pending'  # Default status
            payment.check_status = 'pending'  # Added check_status field

            try:
                payment.save()
                messages.success(request, f"Payment submitted! Your transaction ID is {transaction_id}. Awaiting admin approval.")
                return redirect('submit_payment', hosteller_id=hosteller_id)
            except Exception as e:
                messages.error(request, f"Error saving payment: {e}")
                print(f"Error saving payment: {e}")  # Debugging output

        else:
            messages.error(request, "Invalid form submission. Please check your inputs.")
            print("Form errors:", form.errors)  # Debugging output

    else:
        form = PaymentForm(initial={
            'hosteller_name': hosteller.name,
            'transaction_id': transaction_id
        })

    return render(request, 'payments.html', {
        'form': form,
        'hosteller': hosteller,
        'transaction_id': transaction_id
    })


class MessDetailView(View):
    def get(self, request):
        mess_details = MessDetail.objects.all()  # Get all mess details
        return render(request, 'mess_details.html', {'mess_details': mess_details})

#/////////////////////////////////////admin access////////////////////


@staff_member_required
def admin_dashboard(request):
    """Fetch all complaints and allow resolving them without requiring complaint_id in URL."""
    complaints = Complaint.objects.all()

    return render(request, 'admin_dashboard.html', {'complaints': complaints})



@staff_member_required
def manage_announcements(request):
    # Admin can add announcements
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement created successfully.')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()

    return render(request, 'manage_announcements.html', {'form': form})

def announcement_list(request):
    announcements = Announcement.objects.all()
    return render(request, 'announcement_list.html', {'announcements': announcements})

from django.shortcuts import get_object_or_404

from .forms import LeavePassForm
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
@staff_member_required
@csrf_exempt
def approval_leave_pass(request):
    """ Approve or toggle leave status dynamically """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            leave_id = data.get("leave_id")  # Get leave_id from POST data
            new_status = data.get("status")

            leave_pass = get_object_or_404(LeavePass, id=leave_id)

            if new_status in ["approved", "pending", "rejected"]:
                leave_pass.status = new_status
                leave_pass.save()
                return JsonResponse({"success": True, "new_status": new_status})
            else:
                return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Fetch all leave requests
    leave_passes = LeavePass.objects.all()
    return render(request, 'approve_leave_pass.html', {'leave_passes': leave_passes})


@csrf_exempt
def update_leave_status(request, leave_id):
    """ Fetch LeavePass details and handle status update """
    leave_pass = get_object_or_404(LeavePass, id=leave_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get("status")

            if new_status in ["approved", "pending", "rejected"]:
                leave_pass.status = new_status
                leave_pass.save()
                return JsonResponse({"success": True, "new_status": new_status})
            else:
                return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid data format"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@staff_member_required
def resolve_complaint(request):
    complaints = Complaint.objects.filter(status='pending')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        if complaint_id:
            complaint = get_object_or_404(Complaint, id=complaint_id)
            complaint.status = 'resolved'
            complaint.save()
            messages.success(request, 'Complaint marked as resolved.')
        return redirect('resolve_complaint')

    return render(request, 'resolve_complaint.html', {'complaints': complaints})




@csrf_exempt
def update_complaint_status(request, complaint_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get("status")
            complaint = Complaint.objects.get(id=complaint_id)
            complaint.status = new_status
            complaint.save()
            return JsonResponse({"success": True, "new_status": new_status})
        except Complaint.DoesNotExist:
            return JsonResponse({"success": False, "error": "Complaint not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)



import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Payment


@staff_member_required
@csrf_exempt  # Remove this in production, use CSRF token instead
def manage_payment_query(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            new_status = data.get('status')

            payment = get_object_or_404(Payment, id=payment_id)
            payment.check_status = new_status.lower()
            payment.save()

            return JsonResponse({'success': True, 'new_status': new_status})
        except Exception as e:
            print("Error updating payment status:", str(e))  # Debugging
            return JsonResponse({'success': False, 'error': str(e)})

    payments = Payment.objects.all()
    return render(request, 'manage_payment_query.html', {'payments': payments})



def manage_attendance(request):
    today = now().date()
    # {{ total_students }}
    # Fetch all hostellers grouped by semester
    hostellers_by_semester = {}
    all_hostellers = Hosteller.objects.all().order_by('semester', 'name')
    total_students = all_hostellers.count()  # Count all students

    for hosteller in all_hostellers:
        semester = ''.join(filter(str.isdigit, hosteller.semester))  # Normalize semester numbers
        if semester not in hostellers_by_semester:
            hostellers_by_semester[semester] = []
        hostellers_by_semester[semester].append(hosteller)

    # Get attendance records for today
    attendance_records = {a.hosteller.roll_number: a.status for a in Attendance.objects.filter(date=today)}

    # Count present students
    present_students_count = sum(1 for status in attendance_records.values() if status == "Present")

    return render(request, 'manage_attendance_template.html', {
        'today': today,
        'hostellers_by_semester': hostellers_by_semester,
        'attendance_records': attendance_records,
        'total_students': total_students,
        'present_students_count': present_students_count,
    })

@csrf_exempt
def update_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        hosteller_id = data.get('hosteller_id')
        status = data.get('status')
        today = now().date()

        if hosteller_id and status:
            attendance, created = Attendance.objects.update_or_create(
                hosteller_id=hosteller_id, date=today,
                defaults={'status': status}
            )
            return JsonResponse({"success": True, "message": "Attendance updated successfully!"})

    return JsonResponse({"success": False, "message": "Invalid request!"})


def success_page(request):
    # Get the hosteller's roll number from the session or request
    hosteller_roll_number = request.session.get('hosteller_id')

    # Retrieve the hosteller instance
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_roll_number)

    return render(request, 'success.html', {'hosteller': hosteller})


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_invoice(request, hosteller_id):
    # Fetch the latest payment for the given hosteller
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)
    payment = Payment.objects.filter(hosteller=hosteller).order_by('-created_at').first()

    if not payment:
        return HttpResponse("No payment record found.", content_type="text/plain")

    # Determine Due Date based on payment type
    due_date = "8th of Every Month" if payment.payment_type == "mess" else "Before Admission to Next Year"

    # Define response as a PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{hosteller.roll_number}.pdf"'

    # Create the PDF object
    p = canvas.Canvas(response)

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Hostel Payment Invoice")

    # Invoice Details
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Hosteller Name: {hosteller.name}")
    p.drawString(100, 730, f"Roll Number: {hosteller.roll_number}")
    p.drawString(100, 710, f"Transaction ID: {payment.transaction_id}")
    p.drawString(100, 690, f"Payment Type: {payment.payment_type.capitalize()} Fee")
    p.drawString(100, 670, f"Total Amount Paid: ₹{payment.amount}")
    p.drawString(100, 650, f"Due Date: {due_date}")
    p.drawString(100, 630, "Mess Committee: GEC Girls Hostel")

    # Date of Payment
    p.drawString(100, 600, f"Date of Payment: {payment.created_at.strftime('%d-%m-%Y')}")

    # Date of Invoice Generation
    p.drawString(100, 580, f"Invoice Generated On: {datetime.now().strftime('%d-%m-%Y')}")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, 550, "Thank you for your payment!")

    # Save PDF
    p.showPage()
    p.save()

    return response

from .models import Gallery
from .forms import GalleryForm

def upload_gallery_image(request, roll_number):
    hosteller = get_object_or_404(Hosteller, roll_number=roll_number)  # Fetch hosteller using roll_number
    images = Gallery.objects.all()
    form = GalleryForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        gallery_image = form.save(commit=False)
        gallery_image.save()
        return redirect('gallery', roll_number=hosteller.roll_number)  # Redirect to the gallery page

    return render(request, 'gallary.html', {'images': images, 'form': form, 'hosteller': hosteller})

from django.shortcuts import render


def about_hostel(request, hosteller_id):
    # Fetch the hosteller instance
    hosteller = get_object_or_404(Hosteller, roll_number=hosteller_id)

    context = {
        'hosteller': hosteller,
        'dashboard_url': '/dashboard/' + hosteller_id  # Example for passing dashboard link
    }
    return render(request, 'about_hostel.html', context)

from .models import MessDetail

def mess_details_view(request):
    mess_details = MessDetail.objects.last()

    context = {
        'mess_details': mess_details
    }

    return render(request, 'mess_details.html', context)


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////----------------- ANDROID APP ---------------------///////////////////////////////////////////////

from rest_framework import generics
from .models import Hosteller, Payment, Attendance, Announcement, Feedback, Complaint, LeavePass, EntryExitLog, Notification, MessDetail, Gallery
from .serializers import HostellerSerializer, PaymentSerializer, AttendanceSerializer, AnnouncementSerializer, FeedbackSerializer, ComplaintSerializer, LeavePassSerializer, EntryExitLogSerializer, NotificationSerializer, MessDetailSerializer, GallerySerializer

# Hosteller API
class HostellerListCreate(generics.ListCreateAPIView):
    queryset = Hosteller.objects.all()
    serializer_class = HostellerSerializer

class HostellerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hosteller.objects.all()
    serializer_class = HostellerSerializer

# Payment API
class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# Attendance API
class AttendanceListCreate(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

# Announcement API
class AnnouncementListCreate(generics.ListCreateAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

class AnnouncementDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

# Feedback API
class FeedbackListCreate(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class FeedbackDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

# Complaint API
class ComplaintListCreate(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

class ComplaintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

# LeavePass API
class LeavePassListCreate(generics.ListCreateAPIView):
    queryset = LeavePass.objects.all()
    serializer_class = LeavePassSerializer

class LeavePassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeavePass.objects.all()
    serializer_class = LeavePassSerializer

# EntryExit API
class EntryExitLogListCreate(generics.ListCreateAPIView):
    queryset = EntryExitLog.objects.all()
    serializer_class = EntryExitLogSerializer

class EntryExitLogDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = EntryExitLog.objects.all()
    serializer_class = EntryExitLogSerializer

# Notification API
class NotificationListCreate(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class NotificationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

# MessDetail API
class MessDetailListCreate(generics.ListCreateAPIView):
    queryset = MessDetail.objects.all()
    serializer_class = MessDetailSerializer

class MessDetailDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MessDetail.objects.all()
    serializer_class = MessDetailSerializer

# Gallery API
class GalleryListCreate(generics.ListCreateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer

class GalleryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer






