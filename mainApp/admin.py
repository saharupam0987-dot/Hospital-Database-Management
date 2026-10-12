from django.contrib import admin
from .models import Doctor, Patient, Room, Test, Appointment, Operation, Admission, Profile

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Room)
admin.site.register(Test)
admin.site.register(Appointment)
admin.site.register(Operation)
admin.site.register(Admission)
admin.site.register(Profile)