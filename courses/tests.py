from django.test import TestCase
from .models import Course, Enrollment
from django.contrib.auth.models import User

# Тестирование модели курса
class CourseModelTest(TestCase):
    def test_course_creation(self):
        course = Course.objects.create(title="Тестовый курс", description="Просто тестовый курс", start_date="2023-01-01", end_date="2023-12-31")
        self.assertEqual(course.title, "Тестовый курс")

# Тестирование модели регистрации на курс
class EnrollmentModelTest(TestCase):
    def test_enrollment_creation(self):
        user = User.objects.create(username="testuser")
        course = Course.objects.create(title="Тестовый курс", description="Просто тестовый курс", start_date="2023-01-01", end_date="2023-12-31")
        enrollment = Enrollment.objects.create(user=user, course=course)
        self.assertEqual(enrollment.user.username, "testuser")
        self.assertEqual(enrollment.course.title, "Тестовый курс"exit
