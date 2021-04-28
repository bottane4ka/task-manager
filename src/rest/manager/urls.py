from django.conf.urls import url, include
from rest_framework import routers

from manager import views

router = routers.DefaultRouter()
router.register(r"task-status", views.TaskStatusViewSet, basename="task-status")

urlpatterns = [
    url(r"^", include(router.urls))
]
