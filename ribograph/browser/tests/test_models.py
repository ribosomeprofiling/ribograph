from django.test import TestCase
from browser.models import Project, Experiment
from datetime import date
from django.contrib.auth.models import User
from django.test import Client
from django.core.exceptions import ValidationError
from browser.forms import ProjectForm
from django.urls import reverse

#####################################################################
USERNAME = "test-user"
PASSWORD = "p[assword"
#####################################################################
def _my_login():
    u = User.objects.create(username=USERNAME)
    u.set_password(PASSWORD)
    u.save()
    c = Client()
    c.login(username=USERNAME, password=PASSWORD)
    return u


#####################################################################
#### More tests need to be added here
class ProjectTestCase(TestCase):
    def setUp(self):
        self.user = _my_login()
        Project.objects.create(name="First_Project", owner=self.user)

    def test_basic_model_creation(self):
        """
        Check the very basics of Study creation
        """

        all_projects = Project.objects.all()
        self.assertEqual(
            len(all_projects), 1, msg="There has to be exactly one project"
        )

        self.assertEqual(all_projects[0].name, "First_Project")


class ProjectFormTestCase(TestCase):
    def setUp(self):
        self.user = _my_login()
        self.c = Client()
        self.c.login(username=USERNAME, password=PASSWORD)

    def test_add_basic_project(self):
        """
        Test adding Project
        """

        response = self.c.post(
            reverse("browser:add_project"), {"name": "Pink", "public": False}
        )

        content = str(response.content, "utf-8")
        project_query_result = Project.objects.filter(name="Pink")
        self.assertTrue(project_query_result)

        project_query_result_2 = Project.objects.filter(name="Pink2")
        self.assertTrue(not project_query_result_2)

    def test_project_uniqueness(self):
        """
        Test adding Project
        """

        response = self.c.post(
            reverse("browser:add_project"), {"name": "Blue", "public": False}
        )

        response = self.c.post(
            reverse("browser:add_project"), {"name": "Blue", "public": False}
        )

        project_query_result = Project.objects.filter(name="Blue")

        self.assertEqual(len(project_query_result), 1)


class ProjectFormNameTestCase(TestCase):
    def setUp(self):
        self.user = _my_login()
        self.c = Client()
        self.c.login(username=USERNAME, password=PASSWORD)

    def test_wrong_project_name(self):
        # "&" is not allowed in names:
        response = self.c.post(
            reverse("browser:add_project"), {"name": "P&nk", "public": False}
        )

        self.assertEqual(len(Project.objects.all()), 0)


class ProjectFormEmptyNameTestCase(TestCase):
    def setUp(self):
        self.user = _my_login()
        self.c = Client()
        self.c.login(username=USERNAME, password=PASSWORD)

    def test_empty_name(self):
        response = self.c.post(
            reverse("browser:add_project"), {"name": "", "public": False}
        )

        self.assertEqual(len(Project.objects.all()), 0)
