from django.urls import path

from .views import (
    HealthView,
    ProfileDetailView,
    ProjectDetailView,
    ProjectListView,
    TechnologyListView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<slug:slug>/', ProjectDetailView.as_view(), name='project-detail'),
    path('technologies/', TechnologyListView.as_view(), name='technology-list'),
    path('profile/', ProfileDetailView.as_view(), name='profile-detail'),
]
