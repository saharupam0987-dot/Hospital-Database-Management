from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    department = models.CharField(max_length=20)
    officeNumber = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    type = models.CharField(max_length=10)
    available = models.BooleanField()

    def __str__(self):
        return f"Room {self.id} - {self.type}"

class Test(models.Model):
    testName = models.CharField(max_length=50)
    scheduledTime = models.DateTimeField()
    testReport = models.FileField(upload_to='test_reports/')
    reportGenerationTime = models.DateTimeField()
    patientID = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return self.testName

class Appointment(models.Model):
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    priority = models.IntegerField()

    appReport = models.FileField(
        upload_to='appointment_reports/',
        null=True,
        blank=True
    )

    reportGenerationTime = models.DateTimeField(
        null=True,
        blank=True
    )

    doctorID = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patientID = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return f"Appointment {self.id}"

class Operation(models.Model):
    opName = models.CharField(max_length=50)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    operationReport = models.FileField(upload_to='operation_reports/')
    reportGenerationTime = models.DateTimeField()
    opTheatre = models.ForeignKey(Room, on_delete=models.CASCADE)
    patientID = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctorID = models.ManyToManyField(Doctor)

    def __str__(self):
        return self.opName

class Admission(models.Model):
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(null=True, blank=True)
    patientID = models.ForeignKey(Patient, on_delete=models.CASCADE)
    roomID = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admission {self.id}"
class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('FRONT_DESK', 'Front Desk Operator'),
        ('DATA_ENTRY', 'Data Entry Operator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
        