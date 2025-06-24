from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import date



class Hostel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Hosteller(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=20, unique=True, primary_key=True)
    password = models.CharField(max_length=128)  # Store hashed password
    hostel = models.ForeignKey('Hostel', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=15, blank=True)
    qr_image = models.CharField(max_length=255, blank=True, null=True)  # Store path in static/qr_codes/
    student_image = models.ImageField(upload_to='student_images/', blank=True, null=True)  # Student image
    is_inside = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=15, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=20)
    email = models.EmailField(default='172003rash@gmail.com')
    branch = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=255, blank=True)

    father_name = models.CharField(max_length=255, blank=True)
    mother_name = models.CharField(max_length=255, blank=True)
    father_image = models.ImageField(upload_to='parent_images/', blank=True, null=True)  # father image
    mother_image = models.ImageField(upload_to='parent_images/', blank=True, null=True)  # mother image
    parent_address = models.CharField(max_length=255, blank=True)
    parent_number = models.CharField(max_length=15, blank=True)

    lg_name = models.CharField(max_length=255, blank=True)
    relation = models.CharField(max_length=255, blank=True)
    lg_number = models.CharField(max_length=255, blank=True)
    lg_address = models.CharField(max_length=255, blank=True)





    def __str__(self):
        return self.name

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # Hash the password before saving

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt')):
            self.set_password(self.password)  # Hash password only if it's plain text
        super().save(*args, **kwargs)


class EntryExitLog(models.Model):
    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Automatically set entry time
    exit_time = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Log for {self.hosteller.name}"


# //////////////////////////////////////// Management Section /////////////////////////////

class LeavePass(models.Model):
    LEAVE_CHOICES = [
        ('outing', 'Outing'),
        ('work', 'Work'),
        ('college_holiday', 'College Holiday'),
        ('family_function', 'Family Function'),
    ]

    LEAVE_ID_MAPPING = {
        'outing': 1,
        'work': 2,
        'college_holiday': 3,
        'family_function': 4,
    }

    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    leave_type = models.CharField(
        max_length=20, choices=LEAVE_CHOICES, default='work'
    )
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')

    def is_active(self):
        """ Check if the leave pass is still active (not expired) """
        return self.to_date >= date.today()

    def get_leave_id(self):
        """ Returns a fixed unique ID based on leave type """
        return self.LEAVE_ID_MAPPING.get(self.leave_type, 0)

    def __str__(self):
        return f"Leave Pass for {self.hosteller.name} ({self.get_leave_id_display()}) - {self.from_date} to {self.to_date}"





class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    COMPLAINT_CHOICES = [
        ('light_fan', 'Light/Fan Issue'),
        ('wifi', 'WiFi Issue'),
        ('water', 'Water Issue'),
        ('cleaning', 'Cleaning Issue'),
        ('bathroom', 'Bathroom Cleanliness Issue'),
    ]

    COMPLAINT_ID_MAPPING = {
        'light_fan': 1,
        'wifi': 2,
        'water': 3,
        'cleaning': 4,
        'bathroom': 5,
    }

    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    complaint_type = models.CharField(
        max_length=20, choices=COMPLAINT_CHOICES, default='light_fan'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_complaint_id(self):
        """ Returns a fixed unique ID based on complaint type """
        return self.COMPLAINT_ID_MAPPING.get(self.complaint_type, 0)

    def __str__(self):
        return f"{self.get_complaint_id()} - {self.get_complaint_type_display()} ({self.get_status_display()})"



class Attendance(models.Model):
    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('hosteller', 'date')  # ✅ Ensures uniqueness per hosteller



from django.db import models
from django.contrib.auth.models import User


class Payment(models.Model):
    PAYMENT_TYPES = [
        ('mess', 'Mess Fee'),
        ('hostel', 'Hostel Fee'),
        ('utilities', 'Water & Electricity'),
    ]

    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')
    check_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')],
                              default='pending')

    def __str__(self):
        return f"{self.hosteller.name} - {self.payment_type} - {self.amount}"


class Feedback(models.Model):
    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.hosteller.name} - Rating: {self.rating}"


class Announcement(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.title


class MessDetail(models.Model):
    meal_type = models.CharField(max_length=50)  # e.g., Breakfast, Lunch, Dinner
    menu = models.TextField()
    timing = models.TimeField()
    last_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    left_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.meal_type} - {self.menu}"


class Notification(models.Model):
    hosteller = models.ForeignKey(Hosteller, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.hosteller.name}'


from .storages import StaticFileStorage

class Gallery(models.Model):
    image = models.ImageField(storage=StaticFileStorage(), upload_to='')  # No need for 'upload_to'


