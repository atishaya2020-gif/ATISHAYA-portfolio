from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, Project, Technology
from .serializers import (
    ContactMessageSerializer,
    ProfileSerializer,
    ProjectSerializer,
    TechnologySerializer,
)
from .services.contact_email import send_contact_notification_email


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok'})


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = (
            Project.objects
            .prefetch_related('technologies', 'features', 'architecture_items')
            .order_by('order', 'title')
        )
        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(featured=featured.lower() == 'true')
        return queryset


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    lookup_field = 'slug'

    def get_object(self):
        return get_object_or_404(
            Project.objects.prefetch_related('technologies', 'features', 'architecture_items'),
            slug=self.kwargs['slug'],
        )


class TechnologyListView(generics.ListAPIView):
    serializer_class = TechnologySerializer
    queryset = Technology.objects.all().order_by('category', 'order', 'name')


class ContactSubmissionThrottle(throttling.AnonRateThrottle):
    scope = 'contact_submission'


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ContactSubmissionThrottle]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_message = serializer.save()
        try:
            send_contact_notification_email(contact_message)
        except Exception:
            pass
        return Response(
            {'status': 'ok', 'message': 'Your message has been received.'},
            status=status.HTTP_201_CREATED,
        )


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        profile = (
            Profile.objects
            .prefetch_related('education', 'focus_items')
            .order_by('id')
            .first()
        )
        if profile is None:
            raise Http404('No Profile found.')
        return profile
