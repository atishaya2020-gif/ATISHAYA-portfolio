from django.urls import path

from .views import PageViewCreateView

urlpatterns = [
    path('track/', PageViewCreateView.as_view(), name='analytics-track'),
]
