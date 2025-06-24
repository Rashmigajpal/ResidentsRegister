from django import forms
from django.contrib.auth.models import User
from .models import Hosteller, LeavePass, Complaint, Attendance, Feedback, MessDetail, Payment, Announcement


class HostellerRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    class Meta:
        model = Hosteller
        fields = [
            'name', 'roll_number', 'hostel','room_number', 'mobile_number', 'student_image',
            'branch', 'semester', 'father_name', 'mother_name', 'father_image', 'mother_image', 'parent_number',
            'address', 'lg_name', 'relation', 'lg_number', 'lg_address',
            'password'
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

class LeavePassForm(forms.ModelForm):
    class Meta:
        model = LeavePass
        fields = ['from_date', 'to_date', 'reason']
        widgets = {
            'from_date': forms.DateInput(attrs={'type': 'date'}),
            'to_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    leave_id = forms.ChoiceField(choices=LeavePass.LEAVE_CHOICES, label="Leave Type")


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['hosteller', 'complaint_type','status', 'description']
        exclude = ['hosteller']  # ❗ This is key


    complaint_id = forms.ChoiceField(choices=Complaint.COMPLAINT_CHOICES, label="Complaint Type")



class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [ 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=[('Present', 'Present'), ('Absent', 'Absent')]),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['hosteller', 'comment', 'rating']

from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'transaction_id', 'payment_status', 'check_status']
        widgets = {
            'transaction_id': forms.TextInput(attrs={'readonly': 'readonly'}),
            'payment_status': forms.HiddenInput(),
            'check_status': forms.HiddenInput(),  # Ensure check_status is hidden in the form
        }
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'created_at']
        widgets = {
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # Allow input in a user-friendly datetime format
        }

class MessDetailForm(forms.ModelForm):
    class Meta:
        model = MessDetail
        fields = ['meal_type', 'menu', 'timing', 'last_amount', 'current_amount', 'left_amount', 'total_amount']
        widgets = {
            'meal_type': forms.TextInput(attrs={'class': 'form-control'}),
            'menu': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'timing': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'last_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'left_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from .models import Gallery

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['image']