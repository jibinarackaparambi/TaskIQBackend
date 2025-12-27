from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from oauth2_provider.models import Application
from rest_framework import viewsets
from django.core.cache import cache


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

    # ✅ DRF expects this exact name
    cache_key = "client_details_app"
    cache_timeout = 300  # 5 minutes
    
    def get_object(self):
        return Application.objects.first()
    
    def get(self, request, *args, **kwargs):
        # Check Redis cache first
        cached_data = cache.get(self.cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        # Cache miss - fetch from DB
        app = self.get_object()
        if app is None:
            return Response({"detail": "No application configured"}, status=404)
        
        serializer = self.get_serializer(app)
        data = serializer.data
        
        # Cache the response for 5 mins
        cache.set(self.cache_key, data, self.cache_timeout)
        
        return Response(data)

class TaskViewSet(viewsets.ModelViewSet):
    # queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # print(self.request.user)
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # For POST
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # For PUT/PATCH
        serializer.save(user=self.request.user)
