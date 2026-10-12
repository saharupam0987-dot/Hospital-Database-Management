"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from mainApp.views import (
    operation_list,
    operation_create,
    operation_edit,
    operation_delete,
)
from mainApp.views import room_list, room_create, room_edit, room_delete
from mainApp.views import doctor_list, doctor_create,doctor_edit, doctor_delete
from mainApp.views import (
    home,
    login_view,
    logout_view,
    admin_dashboard,
    doctor_dashboard,
    frontdesk_dashboard,
    dataentry_dashboard,
    patient_list,
    patient_create,
    patient_edit,
    patient_delete,
    appointment_list,
    appointment_create,
    appointment_edit,
    appointment_delete,
    admission_list,
    admission_create,
    admission_edit,
    admission_delete,
    test_list,
    test_create,
    test_edit,
    test_delete,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("doctor-dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("frontdesk-dashboard/", frontdesk_dashboard, name="frontdesk_dashboard"),
    path("dataentry-dashboard/", dataentry_dashboard, name="dataentry_dashboard"),
    path("patients/", patient_list, name="patient_list"),
    path("patients/add/", patient_create, name="patient_create"),
    path("patients/<int:patient_id>/edit/", patient_edit, name="patient_edit"),
    path("patients/<int:patient_id>/delete/", patient_delete, name="patient_delete"),
    path("appointments/", appointment_list, name="appointment_list"),
    path("appointments/add/", appointment_create, name="appointment_create"),
    path(
        "appointments/<int:appointment_id>/edit/",
        appointment_edit,
        name="appointment_edit",
    ),
    path(
        "appointments/<int:appointment_id>/delete/",
        appointment_delete,
        name="appointment_delete",
    ),
    path("admissions/", admission_list, name="admission_list"),
    path("admissions/add/", admission_create, name="admission_create"),
    path("admissions/<int:admission_id>/edit/", admission_edit, name="admission_edit"),
    path(
        "admissions/<int:admission_id>/delete/",
        admission_delete,
        name="admission_delete",
    ),
    path("tests/", test_list, name="test_list"),
    path("tests/add/", test_create, name="test_create"),
    path("tests/<int:test_id>/edit/", test_edit, name="test_edit"),
    path("tests/<int:test_id>/delete/", test_delete, name="test_delete"),
    path("operations/", operation_list, name="operation_list"),
    path("operations/add/", operation_create, name="operation_create"),
    path("operations/<int:operation_id>/edit/", operation_edit, name="operation_edit"),
    path(
        "operations/<int:operation_id>/delete/",
        operation_delete,
        name="operation_delete",
    ),
    path('rooms/', room_list, name='room_list'),
    path('rooms/add/', room_create, name='room_create'),
    
path(
    'rooms/<int:room_id>/edit/',
    room_edit,
    name='room_edit'
),

path(
    'rooms/<int:room_id>/delete/',
    room_delete,
    name='room_delete'
),
path('doctors/', doctor_list, name='doctor_list'),
path('doctors/add/', doctor_create, name='doctor_create'),
path(
    'doctors/<int:doctor_id>/edit/',
    doctor_edit,
    name='doctor_edit'
),

path(
    'doctors/<int:doctor_id>/delete/',
    doctor_delete,
    name='doctor_delete'
),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
