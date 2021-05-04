from django.conf.urls import url, include
from rest.utils.routers import CustomRouter

from manager import views

router = CustomRouter()
router.register(r"task_status", views.TaskStatusViewSet, basename="task_status")
router.register(r"base_task_log", views.BaseTaskLogViewSet, basename="base_task_log")
router.register(r"base_task", views.BaseTaskViewSet, basename="base_task")
router.register(r"task", views.TaskViewSet, basename="task")
router.register(r"task_sequence", views.TaskSequenceViewSet, basename="task_sequence")

urlpatterns = [
    url(r"^", include(router.urls))
]
