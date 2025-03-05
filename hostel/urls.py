from django.conf import settings
from django.conf.urls.static import static
from hostel.views import *
from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic import RedirectView
from .admin import admin_site

urlpatterns = [
    # Redirect home page to hostels
    path('', views.home, name='home'),  # Root URL points to home view

    # Admin site
    path('admin/', admin_site.urls),  # Custom admin site

    # Admin dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Registration and login pages
    path('register/', views.register_hosteller, name='register_hosteller'),
    path('login/', views.login_hosteller, name='login_hosteller'),

    # Hostel list and details
    path('hostels/', hostel_list, name='hostel_list'),
    path('hostels/<int:hostel_id>/hostellers/', hosteller_list, name='hosteller_list'),
    path('hostellers/<str:roll_number>/qr_code/', generate_qr_code, name='generate_qr_code'),
    path('scan/', scan_qr_code, name='scan_qr_code'),
    path('hostellers/<str:roll_number>/', hosteller_detail, name='hosteller_detail'),
    path('hostellers/<str:roll_number>/download/', download_profile, name='download_profile'),
    path('hostellers/<str:roll_number>/delete/', delete_hosteller, name='delete_hosteller'),

    # Dashboard and submission forms
    path('dashboard/<str:hosteller_id>/', DashboardView.as_view(), name='dashboard'),
    path('submit_complaint/<str:hosteller_id>/', submit_complaint, name='submit_complaint'),
    path('submit_leave_pass/<str:hosteller_id>/', submit_leave_pass, name='submit_leave_pass'),
    path('submit_feedback/<str:hosteller_id>/', submit_feedback, name='submit_feedback'),
    path('submit_attendance/<str:hosteller_id>/', submit_attendance, name='submit_attendance'),
    path('hostel/submit_payment/<str:hosteller_id>/', submit_payment, name='submit_payment'),

    # Admin management pages
    path('manage_announcements/', manage_announcements, name='manage_announcements'),
    path('approval-leave-pass/', approval_leave_pass, name='approval_leave_pass'),
    path('hostel/resolve-complaint/', views.resolve_complaint, name='resolve_complaint'),
    path('manage_payment_query/', manage_payment_query, name='manage_payment_query'),
    path('manage_attendance/', manage_attendance, name='manage_attendance'),
    path('update-attendance/', update_attendance, name='update_attendance'),  # ✅ New URL for updating attendance

    path('hostel/generate_invoice/<str:hosteller_id>/', views.generate_invoice, name='generate_invoice'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('upload_gallery_image/<str:roll_number>/', upload_gallery_image, name='gallery'),
path('about-hostel/<str:hosteller_id>/', views.about_hostel, name='about_hostel'),
    path('mess-details/', mess_details_view, name='mess_details'),

    # Success page
    path('success/', success_page, name='success_page'),
    path('feedback/success/<str:hosteller_id>/', feedback_success, name='feedback_success'),
    path('complaint/success/<str:hosteller_id>/', complaint_success, name='complaint_success'),
    path('attendance/success/<str:hosteller_id>/', attendance_success, name='attendance_success'),
    path('complaints/update_complaint_status/<int:complaint_id>/', update_complaint_status, name='update_complaint_status'),
    path('hostel/update_leave_status/<int:leave_id>/', update_leave_status, name='update_leave_status'),


    #///////////////////////////////////------------ANDROID APP---------------///////////////////////

    path('api/hostellers/', HostellerListCreate.as_view(), name='hosteller-list'),
    path('api/hostellers/<int:pk>/', HostellerDetail.as_view(), name='hosteller-detail'),

    path('api/payments/', PaymentListCreate.as_view(), name='payment-list'),
    path('api/payments/<int:pk>/', PaymentDetail.as_view(), name='payment-detail'),

    path('api/attendance/', AttendanceListCreate.as_view(), name='attendance-list'),
    path('api/attendance/<int:pk>/', AttendanceDetail.as_view(), name='attendance-detail'),

    path('api/announcements/', AnnouncementListCreate.as_view(), name='announcement-list'),
    path('api/announcements/<int:pk>/', AnnouncementDetail.as_view(), name='announcement-detail'),

    path('api/feedbacks/', FeedbackListCreate.as_view(), name='feedback-list'),
    path('api/feedbacks/<int:pk>/', FeedbackDetail.as_view(), name='feedback-detail'),

    path('api/complaints/', ComplaintListCreate.as_view(), name='complaint-list'),
    path('api/complaints/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),

    path('api/leavepass/', LeavePassListCreate.as_view(), name='leavepass-list'),
    path('api/leavepass/<int:pk>/', LeavePassDetail.as_view(), name='leavepass-detail'),

    path('api/entryexit/', EntryExitLogListCreate.as_view(), name='entryexit-list'),
    path('api/entryexit/<int:pk>/', EntryExitLogDetail.as_view(), name='entryexit-detail'),

    path('api/notifications/', NotificationListCreate.as_view(), name='notification-list'),
    path('api/notifications/<int:pk>/', NotificationDetail.as_view(), name='notification-detail'),

    path('api/messdetails/', MessDetailListCreate.as_view(), name='messdetail-list'),
    path('api/messdetails/<int:pk>/', MessDetailDetail.as_view(), name='messdetail-detail'),

    path('api/gallery/', GalleryListCreate.as_view(), name='gallery-list'),
    path('api/gallery/<int:pk>/', GalleryDetail.as_view(), name='gallery-detail'),

]
# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

