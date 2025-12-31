import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from accounts.models import User
from oauth2_provider.models import Application

from accounts.models import Task
from accounts.serializers import TaskSerializer  # Adjust import

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    user = User.objects.create_user(email='test@example.com', password='Test123$')
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()

    def application_creations(self):
        return Application.objects.create(name="Test Client", client_type="confidential", authorization_grant_type="password",hash_client_secret=False)
    
    def user_creation(self):
        return User.objects.create(email="test@gmail.com", password="Test123$")
    
    def test_get_client_details(self):
        self.application_creations()
        url = reverse('client_details')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_user_reg(self):
        application = self.application_creations()
        # user = self.user_creation()
        url = reverse('custom-register')
        url = reverse('custom-register')
        data = {
            'email': 'test@gmail.com',
            'password1': 'Test123$',
            'password2': 'Test123$',
            # Add if required:
            # 'username': 'testuser',
            # 'first_name': 'Test',
            # 'last_name': 'User',
            # 'confirm_password': 'Test123$',
        }
        response = self.client.post(url, data, format="json")
    
        # Debug first:
        print(response.status_code, response.data)  # Check errors
        
        assert response.status_code == 201
        assert User.objects.filter(email='test@gmail.com').exists()

    def test_list_tasks(self, authenticated_client, user):
        """GET /tasks/ - List user's tasks only."""
        Task.objects.create(title="Task 1", description="Desc 1", user=user)
        Task.objects.create(title="Task 2", description="Desc 2", user=user)
        # Other user's task shouldn't appear
        other_user = User.objects.create_user(email='other@example.com')
        Task.objects.create(title="Other Task", user=other_user)
        
        url = reverse('task-list')  # basename="task" generates task-list
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) == 2  # Only user's tasks
        assert response.data[0]['title'] == "Task 1"

    def test_create_task(self, authenticated_client, user):
        """POST /tasks/ - Create task for authenticated user."""
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'description': 'Task description',
            'status': 'TODO'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert Task.objects.filter(user=user, title='New Task').exists()
        assert response.data['status'] == 'TODO'
        assert response.data['user'] == user.id

    def test_retrieve_task(self, authenticated_client, user):
        """GET /tasks/{id}/ - Retrieve single task."""
        task = Task.objects.create(title="Test Task", description="Test", user=user)
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['title'] == 'Test Task'
        assert response.data['id'] == task.pk

    def test_update_task(self, authenticated_client, user):
        """PUT/PATCH /tasks/{id}/ - Update task."""
        task = Task.objects.create(title="Old Title", status="PENDING", user=user)
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'title': 'Updated Title', 'status': 'INPROGRES'}
        
        response = authenticated_client.patch(url, data, format='json')
        task.refresh_from_db()
        
        assert response.status_code == 200
        assert task.title == 'Updated Title'
        assert task.status == 'INPROGRES'

    def test_delete_task(self, authenticated_client, user):
        """DELETE /tasks/{id}/ - Delete task."""
        task = Task.objects.create(title="To Delete", user=user)
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.delete(url)
        
        assert response.status_code == 204
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_unauthenticated_access_denied(self, api_client, user):
        """Non-authenticated users can't access tasks."""
        Task.objects.create(title="Task", user=user)
        url = reverse('task-list')
        response = api_client.get(url)
        
        assert response.status_code == 401  # Unauthorized

    def test_foreign_task_access_denied(self, authenticated_client, user):
        """Users can't access other users' tasks."""
        other_user = User.objects.create_user(email='other@example.com')
        other_task = Task.objects.create(title="Other Task", user=other_user)
        url = reverse('task-detail', kwargs={'pk': other_task.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == 404  # Not found due to queryset 