from rest_framework import serializers

from .models import (
    ContactMessage,
    Education,
    Profile,
    ProfileFocus,
    Project,
    ProjectArchitecture,
    ProjectFeature,
    Technology,
)


class ProjectFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFeature
        fields = ['id', 'text', 'order']


class ProjectArchitectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectArchitecture
        fields = ['id', 'text', 'order']


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'category', 'slug', 'description', 'order']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'label', 'title', 'description', 'order']


class ProfileFocusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFocus
        fields = ['id', 'label', 'value', 'order']


class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, read_only=True)
    features = ProjectFeatureSerializer(many=True, read_only=True)
    architecture = ProjectArchitectureSerializer(
        many=True,
        read_only=True,
        source='architecture_items',
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'subtitle',
            'slug',
            'short_description',
            'full_description',
            'category',
            'status',
            'featured',
            'order',
            'github_url',
            'live_url',
            'api_url',
            'overview',
            'technologies',
            'features',
            'architecture',
            'created_at',
            'updated_at',
        ]


class ProfileSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, read_only=True)
    focus_items = ProfileFocusSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'name',
            'role',
            'introduction',
            'philosophy',
            'career_goal',
            'current_focus',
            'what_i_build',
            'education',
            'focus_items',
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField(max_length=254, trim_whitespace=True)
    subject = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default='',
        trim_whitespace=True,
    )
    message = serializers.CharField(max_length=5000, trim_whitespace=True)

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def validate_name(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Name cannot be empty or whitespace only.")
        return stripped

    def validate_email(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Email cannot be empty or whitespace only.")
        return stripped

    def validate_subject(self, value: str) -> str:
        return value.strip() if value else ''

    def validate_message(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Message cannot be empty or whitespace only.")
        return stripped
