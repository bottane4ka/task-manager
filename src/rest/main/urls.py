from django.urls import path, include

urlpatterns = [
    path("manager/", include("manager.urls")),
]
