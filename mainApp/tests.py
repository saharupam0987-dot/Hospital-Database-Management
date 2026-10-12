
from django.test import TestCase
from django.utils import timezone

from .models import Admission, Patient, Room
from .views import update_room_availability

from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Profile



class RoomAvailabilityTests(TestCase):

    def test_room_without_active_admission_becomes_available(self):
        room = Room.objects.create(
            type='General',
            available=False
        )

        update_room_availability(room)

        room.refresh_from_db()
        self.assertTrue(room.available)

    def test_room_with_active_admission_becomes_occupied(self):
        # Create a test room.
        room = Room.objects.create(
            type='General',
            available=True
        )

        # Create a test patient.
        patient = Patient.objects.create(
            name='Test Patient'
        )

        # Create an active admission with no discharge time.
        Admission.objects.create(
            startTime=timezone.now(),
            endTime=None,
            patientID=patient,
            roomID=room
        )

        # Recalculate room availability.
        update_room_availability(room)

        # Verify that the room is marked as occupied.
        room.refresh_from_db()
        self.assertFalse(room.available)
    
    def test_discharged_admission_makes_room_available(self):
        room = Room.objects.create(
            type='General',
            available=False
        )

        patient = Patient.objects.create(
            name='Discharged Test Patient'
        )

        Admission.objects.create(
            startTime=timezone.now(),
            endTime=timezone.now(),
            patientID=patient,
            roomID=room
        )

        update_room_availability(room)

        room.refresh_from_db()
        self.assertTrue(room.available)
    
    def test_room_stays_occupied_if_another_active_admission_remains(self):
        room = Room.objects.create(
            type='General',
            available=True
        )

        patient1 = Patient.objects.create(name='Active Test Patient')
        patient2 = Patient.objects.create(name='Discharged Test Patient')

        now = timezone.now()

        # This patient still has an active admission.
        Admission.objects.create(
            startTime=now,
            endTime=None,
            patientID=patient1,
            roomID=room
        )

        # This patient has already been discharged.
        Admission.objects.create(
            startTime=now,
            endTime=now,
            patientID=patient2,
            roomID=room
        )

        update_room_availability(room)

        room.refresh_from_db()
        self.assertFalse(room.available)


class AdmissionCreateViewTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='test_admin',
            password='test-password-123'
        )

        Profile.objects.create(
            user=self.user,
            role='ADMIN'
        )

        self.client.force_login(self.user)

        self.patient = Patient.objects.create(
            name='Test Patient'
        )

    def test_cannot_assign_occupied_room(self):
        # Create a room that is already occupied.
        room = Room.objects.create(
            type='General',
            available=False
        )

        # Create an existing active admission.
        existing_patient = Patient.objects.create(
            name='Existing Patient'
        )

        Admission.objects.create(
            startTime=timezone.now(),
            endTime=None,
            patientID=existing_patient,
            roomID=room
        )

        # Try to admit another patient to the same room.
        response = self.client.post(
            reverse('admission_create'),
            {
                'startTime': timezone.now().strftime(
                    '%Y-%m-%dT%H:%M'
                ),
                'endTime': '',
                'patientID': self.patient.id,
                'roomID': room.id,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(
            Admission.objects.filter(roomID=room).count(),
            1
        )

    def test_can_create_admission_for_available_room(self):
        # Create an available room.
        room = Room.objects.create(
            type='General',
            available=True
        )

        response = self.client.post(
            reverse('admission_create'),
            {
                'startTime': timezone.now().strftime(
                    '%Y-%m-%dT%H:%M'
                ),
                'endTime': '',
                'patientID': self.patient.id,
                'roomID': room.id,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('admission_list')
        )

        self.assertEqual(Admission.objects.count(), 1)

        room.refresh_from_db()
        self.assertFalse(room.available)


