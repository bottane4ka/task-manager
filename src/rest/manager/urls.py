from django.conf.urls import url, include
from rest.utils.routers import CustomRouter

from manager import views

router = CustomRouter()
router.register(r"task-status", views.TaskStatusViewSet, basename="task-status")

urlpatterns = [
    url(r"^", include(router.urls))
]
