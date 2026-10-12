from mainApp.decorators import role_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Patient, Appointment, Doctor, Admission, Room, Test, Operation
from django.utils import timezone
from django.utils.dateparse import parse_datetime


def parse_local_datetime(value):
    if not value:
        return None

    parsed = parse_datetime(value)

    if parsed is not None and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())

    return parsed


def update_room_availability(room):
    has_active_admission = Admission.objects.filter(
        roomID=room, endTime__isnull=True
    ).exists()

    room.available = not has_active_admission
    room.save(update_fields=["available"])


@login_required(login_url="login")
def home(request):
    profile = request.user.profile

    return render(request, "mainApp/home.html", {"profile": profile})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request, "mainApp/login.html", {"error": "Invalid username or password."}
        )

    return render(request, "mainApp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@role_required(["ADMIN"])
def admin_dashboard(request):
    return render(request, "mainApp/admin_dashboard.html")


@role_required(["DOCTOR"])
def doctor_dashboard(request):
    return render(request, "mainApp/doctor_dashboard.html")


@role_required(["FRONT_DESK"])
def frontdesk_dashboard(request):
    return render(request, "mainApp/frontdesk_dashboard.html")


@role_required(["DATA_ENTRY"])
def dataentry_dashboard(request):
    return render(request, "mainApp/dataentry_dashboard.html")


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def patient_list(request):
    patients = Patient.objects.all()

    return render(request, "mainApp/patient_list.html", {"patients": patients})


@role_required(["ADMIN", "FRONT_DESK"])
def patient_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        phoneNumber = request.POST.get("phoneNumber")
        email = request.POST.get("email")

        Patient.objects.create(
            name=name,
            dob=dob if dob else None,
            gender=gender,
            address=address,
            phoneNumber=phoneNumber,
            email=email,
        )

        return redirect("patient_list")

    return render(request, "mainApp/patient_create.html")


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def patient_edit(request, patient_id):
    patient = Patient.objects.get(id=patient_id)

    if request.method == "POST":
        patient.name = request.POST.get("name")
        patient.dob = request.POST.get("dob") or None
        patient.gender = request.POST.get("gender")
        patient.address = request.POST.get("address")
        patient.phoneNumber = request.POST.get("phoneNumber")
        patient.email = request.POST.get("email")

        patient.save()

        return redirect("patient_list")

    return render(request, "mainApp/patient_edit.html", {"patient": patient})


@role_required(["ADMIN"])
def patient_delete(request, patient_id):
    patient = Patient.objects.get(id=patient_id)

    if request.method == "POST":
        has_appointments = Appointment.objects.filter(patientID=patient).exists()

        has_admissions = Admission.objects.filter(patientID=patient).exists()

        has_tests = Test.objects.filter(patientID=patient).exists()

        has_operations = Operation.objects.filter(patientID=patient).exists()

        if has_appointments or has_admissions or has_tests or has_operations:
            return render(
                request,
                "mainApp/patient_delete.html",
                {
                    "patient": patient,
                    "error": (
                        "This patient has linked hospital records "
                        "and cannot be deleted."
                    ),
                },
            )

        patient.delete()
        return redirect("patient_list")

    return render(
        request,
        "mainApp/patient_delete.html",
        {"patient": patient},
    )


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def appointment_list(request):
    appointments = Appointment.objects.all()

    return render(
        request, "mainApp/appointment_list.html", {"appointments": appointments}
    )


@role_required(["ADMIN", "FRONT_DESK"])
def appointment_create(request):
    if request.method == "POST":
        startTime = parse_local_datetime(request.POST.get("startTime"))
        endTime = parse_local_datetime(request.POST.get("endTime"))

        if startTime is not None and endTime is not None and endTime < startTime:
            return render(
                request,
                "mainApp/appointment_create.html",
                {
                    "doctors": Doctor.objects.all(),
                    "patients": Patient.objects.all(),
                    "error": ("End time must be after the start time."),
                },
            )

        priority = request.POST.get("priority")
        doctorID = request.POST.get("doctorID")
        patientID = request.POST.get("patientID")

        Appointment.objects.create(
            startTime=startTime,
            endTime=endTime,
            priority=priority,
            doctorID_id=doctorID,
            patientID_id=patientID,
        )

        return redirect("appointment_list")

    doctors = Doctor.objects.all()
    patients = Patient.objects.all()

    return render(
        request,
        "mainApp/appointment_create.html",
        {
            "doctors": doctors,
            "patients": patients,
        },
    )


@role_required(["ADMIN", "FRONT_DESK"])
def appointment_edit(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == "POST":
        appointment.startTime = parse_local_datetime(request.POST.get("startTime"))
        appointment.endTime = parse_local_datetime(request.POST.get("endTime"))

        if (
            appointment.startTime is not None
            and appointment.endTime is not None
            and appointment.endTime < appointment.startTime
        ):
            return render(
                request,
                "mainApp/appointment_edit.html",
                {
                    "appointment": appointment,
                    "doctors": Doctor.objects.all(),
                    "patients": Patient.objects.all(),
                    "error": ("End time must be after the start time."),
                },
            )

        appointment.priority = request.POST.get("priority")
        appointment.doctorID_id = request.POST.get("doctorID")
        appointment.patientID_id = request.POST.get("patientID")

        appointment.save()

        return redirect("appointment_list")

    doctors = Doctor.objects.all()
    patients = Patient.objects.all()

    return render(
        request,
        "mainApp/appointment_edit.html",
        {
            "appointment": appointment,
            "doctors": doctors,
            "patients": patients,
        },
    )


@role_required(["ADMIN", "FRONT_DESK"])
def appointment_delete(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    if request.method == "POST":
        appointment.delete()
        return redirect("appointment_list")

    return render(
        request, "mainApp/appointment_delete.html", {"appointment": appointment}
    )


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def admission_list(request):
    admissions = Admission.objects.all()
    return render(request, "mainApp/admission_list.html", {"admissions": admissions})


@role_required(["ADMIN", "FRONT_DESK"])
def admission_create(request):
    if request.method == "POST":
        startTime = parse_local_datetime(request.POST.get("startTime"))
        endTime = parse_local_datetime(request.POST.get("endTime"))

        if startTime is not None and endTime is not None and endTime < startTime:
            return render(
                request,
                "mainApp/admission_create.html",
                {
                    "patients": Patient.objects.all(),
                    "rooms": Room.objects.filter(available=True),
                    "error": ("Discharge time must be after " "the admission time."),
                },
            )

        patientID = request.POST.get("patientID")
        roomID = request.POST.get("roomID")

        # Prevent assigning an occupied room to an active admission.
        has_active_admission = Admission.objects.filter(
            roomID_id=roomID, endTime__isnull=True
        ).exists()

        if endTime is None and has_active_admission:
            return render(
                request,
                "mainApp/admission_create.html",
                {
                    "patients": Patient.objects.all(),
                    "rooms": Room.objects.filter(available=True),
                    "error": (
                        "This room is occupied. Please select "
                        "another available room."
                    ),
                },
            )

        admission = Admission.objects.create(
            startTime=startTime,
            endTime=endTime,
            patientID_id=patientID,
            roomID_id=roomID,
        )

        update_room_availability(admission.roomID)

        return redirect("admission_list")

    patients = Patient.objects.all()
    rooms = Room.objects.filter(available=True)

    return render(
        request,
        "mainApp/admission_create.html",
        {
            "patients": patients,
            "rooms": rooms,
        },
    )


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def admission_edit(request, admission_id):
    admission = Admission.objects.get(id=admission_id)

    if request.method == "POST":
        startTime = parse_local_datetime(request.POST.get("startTime"))
        endTime = parse_local_datetime(request.POST.get("endTime"))

        if startTime is not None and endTime is not None and endTime < startTime:
            rooms = (
                Room.objects.filter(available=True)
                | Room.objects.filter(id=admission.roomID_id)
            ).distinct()

            return render(
                request,
                "mainApp/admission_edit.html",
                {
                    "admission": admission,
                    "patients": Patient.objects.all(),
                    "rooms": rooms,
                    "error": ("Discharge time must be after " "the admission time."),
                },
            )

        patientID = request.POST.get("patientID")
        roomID = request.POST.get("roomID")

        # Check whether another active admission uses this room.
        has_active_admission = (
            Admission.objects.filter(
                roomID_id=roomID,
                endTime__isnull=True,
            )
            .exclude(id=admission.id)
            .exists()
        )

        if endTime is None and has_active_admission:
            rooms = (
                Room.objects.filter(available=True)
                | Room.objects.filter(id=admission.roomID_id)
            ).distinct()

            return render(
                request,
                "mainApp/admission_edit.html",
                {
                    "admission": admission,
                    "patients": Patient.objects.all(),
                    "rooms": rooms,
                    "error": (
                        "This room is occupied by another patient. "
                        "Please select another available room."
                    ),
                },
            )

        old_room = admission.roomID

        admission.startTime = startTime
        admission.endTime = endTime
        admission.patientID_id = patientID
        admission.roomID_id = roomID
        admission.save()

        update_room_availability(old_room)
        update_room_availability(admission.roomID)

        return redirect("admission_list")

    rooms = (
        Room.objects.filter(available=True)
        | Room.objects.filter(id=admission.roomID_id)
    ).distinct()

    return render(
        request,
        "mainApp/admission_edit.html",
        {
            "admission": admission,
            "patients": Patient.objects.all(),
            "rooms": rooms,
        },
    )


@role_required(["ADMIN", "FRONT_DESK"])
def admission_delete(request, admission_id):
    admission = Admission.objects.get(id=admission_id)

    if request.method == "POST":
        room = admission.roomID

        admission.delete()

        update_room_availability(room)

        return redirect("admission_list")

    return render(request, "mainApp/admission_delete.html", {"admission": admission})


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR", "DATA_ENTRY"])
def test_list(request):
    tests = Test.objects.all()
    return render(request, "mainApp/test_list.html", {"tests": tests})


@role_required(["ADMIN", "FRONT_DESK", "DATA_ENTRY"])
def test_create(request):
    if request.method == "POST":
        testName = request.POST.get("testName")
        scheduledTime = parse_local_datetime(request.POST.get("scheduledTime"))
        reportGenerationTime = parse_local_datetime(
            request.POST.get("reportGenerationTime")
        )

        if (
            scheduledTime is not None
            and reportGenerationTime is not None
            and reportGenerationTime < scheduledTime
        ):
            return render(
                request,
                "mainApp/test_create.html",
                {
                    "patients": Patient.objects.all(),
                    "error": (
                        "Report generation time must be "
                        "at or after the scheduled time."
                    ),
                },
            )

        patientID = request.POST.get("patientID")
        testReport = request.FILES.get("testReport")

        Test.objects.create(
            testName=testName,
            scheduledTime=scheduledTime,
            reportGenerationTime=reportGenerationTime,
            testReport=testReport,
            patientID_id=patientID,
        )

        return redirect("test_list")

    patients = Patient.objects.all()

    return render(
        request,
        "mainApp/test_create.html",
        {"patients": patients},
    )


@role_required(["ADMIN", "FRONT_DESK", "DATA_ENTRY"])
def test_edit(request, test_id):
    test = Test.objects.get(id=test_id)

    if request.method == "POST":
        test.testName = request.POST.get("testName")
        test.scheduledTime = parse_local_datetime(request.POST.get("scheduledTime"))
        test.reportGenerationTime = parse_local_datetime(
            request.POST.get("reportGenerationTime")
        )

        if (
            test.scheduledTime is not None
            and test.reportGenerationTime is not None
            and test.reportGenerationTime < test.scheduledTime
        ):
            return render(
                request,
                "mainApp/test_edit.html",
                {
                    "test": test,
                    "patients": Patient.objects.all(),
                    "error": (
                        "Report generation time must be "
                        "at or after the scheduled time."
                    ),
                },
            )

        test.patientID_id = request.POST.get("patientID")

        testReport = request.FILES.get("testReport")

        if testReport:
            test.testReport = testReport

        test.save()

        return redirect("test_list")

    patients = Patient.objects.all()

    return render(
        request,
        "mainApp/test_edit.html",
        {
            "test": test,
            "patients": patients,
        },
    )


@role_required(["ADMIN", "FRONT_DESK", "DATA_ENTRY"])
def test_delete(request, test_id):
    test = Test.objects.get(id=test_id)

    if request.method == "POST":
        test.delete()
        return redirect("test_list")

    return render(request, "mainApp/test_delete.html", {"test": test})


@role_required(["ADMIN", "DOCTOR"])
def operation_list(request):
    operations = Operation.objects.all()

    return render(request, "mainApp/operation_list.html", {"operations": operations})


@role_required(["ADMIN"])
def operation_create(request):
    if request.method == "POST":
        opName = request.POST.get("opName")
        startTime = parse_local_datetime(request.POST.get("startTime"))
        endTime = parse_local_datetime(request.POST.get("endTime"))

        if startTime is not None and endTime is not None and endTime < startTime:
            return render(
                request,
                "mainApp/operation_create.html",
                {
                    "patients": Patient.objects.all(),
                    "rooms": Room.objects.all(),
                    "doctors": Doctor.objects.all(),
                    "error": ("Operation end time must be after " "the start time."),
                },
            )

        reportGenerationTime = parse_local_datetime(
            request.POST.get("reportGenerationTime")
        )
        patientID = request.POST.get("patientID")
        opTheatre = request.POST.get("opTheatre")
        doctorIDs = request.POST.getlist("doctorID")
        operationReport = request.FILES.get("operationReport")

        operation = Operation.objects.create(
            opName=opName,
            startTime=startTime,
            endTime=endTime,
            reportGenerationTime=reportGenerationTime,
            patientID_id=patientID,
            opTheatre_id=opTheatre,
            operationReport=operationReport,
        )

        operation.doctorID.set(doctorIDs)

        return redirect("operation_list")

    patients = Patient.objects.all()
    rooms = Room.objects.all()
    doctors = Doctor.objects.all()

    return render(
        request,
        "mainApp/operation_create.html",
        {
            "patients": patients,
            "rooms": rooms,
            "doctors": doctors,
        },
    )


@role_required(["ADMIN"])
def operation_edit(request, operation_id):
    operation = Operation.objects.get(id=operation_id)

    if request.method == "POST":
        startTime = parse_local_datetime(request.POST.get("startTime"))
        endTime = parse_local_datetime(request.POST.get("endTime"))
        reportGenerationTime = parse_local_datetime(
            request.POST.get("reportGenerationTime")
        )

        if startTime is not None and endTime is not None and endTime < startTime:
            return render(
                request,
                "mainApp/operation_edit.html",
                {
                    "operation": operation,
                    "patients": Patient.objects.all(),
                    "rooms": Room.objects.all(),
                    "doctors": Doctor.objects.all(),
                    "error": ("Operation end time must be after " "the start time."),
                },
            )

        operation.opName = request.POST.get("opName")
        operation.startTime = startTime
        operation.endTime = endTime
        operation.reportGenerationTime = reportGenerationTime
        operation.patientID_id = request.POST.get("patientID")
        operation.opTheatre_id = request.POST.get("opTheatre")

        doctorIDs = request.POST.getlist("doctorID")
        operationReport = request.FILES.get("operationReport")

        if operationReport:
            operation.operationReport = operationReport

        operation.save()
        operation.doctorID.set(doctorIDs)

        return redirect("operation_list")

    patients = Patient.objects.all()
    rooms = Room.objects.all()
    doctors = Doctor.objects.all()

    return render(
        request,
        "mainApp/operation_edit.html",
        {
            "operation": operation,
            "patients": patients,
            "rooms": rooms,
            "doctors": doctors,
        },
    )


@role_required(["ADMIN"])
def operation_delete(request, operation_id):
    operation = Operation.objects.get(id=operation_id)

    if request.method == "POST":
        operation.delete()
        return redirect("operation_list")

    return render(request, "mainApp/operation_delete.html", {"operation": operation})


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def room_list(request):
    rooms = list(Room.objects.all())

    for room in rooms:
        update_room_availability(room)

    return render(request, "mainApp/room_list.html", {"rooms": rooms})


@role_required(["ADMIN"])
def room_create(request):
    if request.method == "POST":
        room_type = request.POST.get("type")

        Room.objects.create(type=room_type, available=True)

        return redirect("room_list")

    return render(request, "mainApp/room_create.html")


@role_required(["ADMIN"])
def room_edit(request, room_id):
    room = Room.objects.get(id=room_id)

    if request.method == "POST":
        room.type = request.POST.get("type")
        room.save()

        update_room_availability(room)

        return redirect("room_list")

    return render(request, "mainApp/room_edit.html", {"room": room})


@role_required(["ADMIN"])
def room_delete(request, room_id):
    room = Room.objects.get(id=room_id)

    if request.method == "POST":
        has_admissions = Admission.objects.filter(roomID=room).exists()
        has_operations = Operation.objects.filter(opTheatre=room).exists()

        if has_admissions or has_operations:
            return render(
                request,
                "mainApp/room_delete.html",
                {
                    "room": room,
                    "error": (
                        "This room is linked to an admission or operation "
                        "and cannot be deleted."
                    ),
                },
            )

        room.delete()
        return redirect("room_list")

    return render(request, "mainApp/room_delete.html", {"room": room})


@role_required(["ADMIN", "FRONT_DESK", "DOCTOR"])
def doctor_list(request):
    doctors = Doctor.objects.all()

    return render(request, "mainApp/doctor_list.html", {"doctors": doctors})


@role_required(["ADMIN"])
def doctor_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        department = request.POST.get("department")
        officeNumber = request.POST.get("officeNumber")
        address = request.POST.get("address") or None
        phoneNumber = request.POST.get("phoneNumber") or None
        email = request.POST.get("email") or None

        Doctor.objects.create(
            name=name,
            department=department,
            officeNumber=officeNumber,
            address=address,
            phoneNumber=phoneNumber,
            email=email,
        )

        return redirect("doctor_list")

    return render(request, "mainApp/doctor_create.html")


@role_required(["ADMIN"])
def doctor_edit(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == "POST":
        doctor.name = request.POST.get("name")
        doctor.department = request.POST.get("department")
        doctor.officeNumber = request.POST.get("officeNumber")
        doctor.address = request.POST.get("address") or None
        doctor.phoneNumber = request.POST.get("phoneNumber") or None
        doctor.email = request.POST.get("email") or None

        doctor.save()

        return redirect("doctor_list")

    return render(request, "mainApp/doctor_edit.html", {"doctor": doctor})


@role_required(["ADMIN"])
def doctor_delete(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == "POST":
        has_appointments = Appointment.objects.filter(doctorID=doctor).exists()

        has_operations = Operation.objects.filter(doctorID=doctor).exists()

        if has_appointments or has_operations:
            return render(
                request,
                "mainApp/doctor_delete.html",
                {
                    "doctor": doctor,
                    "error": (
                        "This doctor is linked to an appointment or "
                        "operation and cannot be deleted."
                    ),
                },
            )

        doctor.delete()
        return redirect("doctor_list")

    return render(request, "mainApp/doctor_delete.html", {"doctor": doctor})
