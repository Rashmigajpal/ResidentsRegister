from django.contrib import admin
from .models import Hostel, Hosteller, EntryExitLog, LeavePass, Complaint, Attendance, Feedback, MessDetail, Notification, Payment
from .views import admin_dashboard
from django.urls import path


class CustomAdminSite(admin.AdminSite):
    site_header = 'My Custom Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('admin-dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name='custom_admin')



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')









@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')

@admin.register(Hosteller)
class HostellerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'roll_number', 'mobile_number',
        'branch', 'semester', 'address',
        'is_inside', 'qr_image', 'student_image', 'password'
    )
    search_fields = ('name', 'roll_number', 'mobile_number', 'branch')
    list_filter = ('is_inside',)

@admin.register(EntryExitLog)
class EntryExitLogAdmin(admin.ModelAdmin):
    list_display = ('hosteller', 'entry_time', 'exit_time', 'venue')
    list_filter = ('entry_time', 'exit_time', 'hosteller')
    search_fields = ('hosteller__name', 'hosteller__roll_number', 'venue')


# Register your models here.

class LeavePassAdmin(admin.ModelAdmin):
    list_display = ('hosteller', 'get_leave_id', 'from_date', 'to_date', 'status')
    list_filter = ('leave_type', 'status')  # Use 'leave_id' which exists in your model

    def get_leave_id(self, obj):
        """Returns the numeric ID for the leave type."""
        LEAVE_ID_MAPPING = {
            'outing': 1,
            'work': 2,
            'college_holiday': 3,
            'family_function': 4,
        }
        return LEAVE_ID_MAPPING.get(obj.leave_id, 0)

    get_leave_id.short_description = "Leave ID"

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('hosteller', 'get_complaint_id', 'status', 'created_at')
    list_filter = ('complaint_type', 'status')  # Use 'complaint_id' which exists in your model

    def get_complaint_id(self, obj):
        """Returns the numeric ID for the complaint type."""
        COMPLAINT_ID_MAPPING = {
            'light_fan': 1,
            'wifi': 2,
            'water': 3,
            'cleaning': 4,
            'bathroom': 5,
        }
        return COMPLAINT_ID_MAPPING.get(obj.complaint_id, 0)

    get_complaint_id.short_description = "Complaint ID"  # Rename the column


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('hosteller', 'date', 'status')
    list_filter = ('status',)
    search_fields = ('hosteller__first_name',)  # Assuming Hosteller has a first_name field
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('hosteller', 'comment', 'rating', 'created_at')

class MessDetailAdmin(admin.ModelAdmin):
    list_display = ('meal_type', 'menu', 'timing', 'total_amount')

class HostellerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')  # Update with actual fields in Hosteller model
    search_fields = ('first_name', 'last_name', 'email')


# Register the models with their respective admin classes

admin.site.register(LeavePass, LeavePassAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(MessDetail, MessDetailAdmin)




