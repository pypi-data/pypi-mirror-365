from django.urls import path
from .views import protected_view

urlpatterns = [
    path("", protected_view),
]
