from django.urls import path,include
from rest_framework.routers import DefaultRouter

from .views import RegisterView,CustomLoginView,ClientDetails,TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    # path("login/", CustomLoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="custom-register"),
    path("auth/client_details/", ClientDetails.as_view(), name="client_details"),
    path("", include(router.urls)),
]
