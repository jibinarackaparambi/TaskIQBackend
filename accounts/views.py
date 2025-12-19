from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from oauth2_provider.models import Application
from rest_framework import viewsets

from accounts.serializers import ApplicationSerializer, RegisterSerializer
from accounts.models import Task
from accounts.serializers import TaskSerializer

User = get_user_model()


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ClientDetails(generics.GenericAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]
    def get_object(self):
        return Application.objects.first()
    
    def get(self, request, *args, **kwargs):
        app = self.get_object()
        if app is None:
            return Response({"detail": "No application configured"}, status=404)
        serializer = self.get_serializer(app)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
