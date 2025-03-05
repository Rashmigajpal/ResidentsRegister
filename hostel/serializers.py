from rest_framework import serializers
from .models import (
    Hosteller, Payment, Attendance, Announcement, Feedback,
    Complaint, LeavePass, EntryExitLog, Notification, MessDetail, Gallery
)

class HostellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hosteller
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'

class LeavePassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePass
        fields = '__all__'

class EntryExitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryExitLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class MessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessDetail
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'
