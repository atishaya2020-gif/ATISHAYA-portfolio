from urllib.parse import quote

from django.contrib import admin
from django.utils.html import format_html

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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'status',
        'featured',
        'order',
        'updated_at',
    )
    list_filter = ('category', 'status', 'featured')
    search_fields = ('title', 'subtitle', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    ordering = ('order', 'title')


@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
    list_display = ('project', 'text', 'order')
    list_filter = ('project',)
    search_fields = ('text', 'project__title')


@admin.register(ProjectArchitecture)
class ProjectArchitectureAdmin(admin.ModelAdmin):
    list_display = ('project', 'order', 'text')
    list_filter = ('project',)
    search_fields = ('text', 'project__title')


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'title', 'order')


@admin.register(ProfileFocus)
class ProfileFocusAdmin(admin.ModelAdmin):
    list_display = ('profile', 'label', 'value', 'order')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'name',
        'email',
        'subject',
        'is_read',
        'is_replied',
        'reply_link',
    )
    list_filter = ('is_read', 'is_replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'reply_link')

    @admin.display(description='Reply')
    def reply_link(self, obj):
        if not obj.email:
            return '-'
        subject_text = f"Re: {obj.subject}" if obj.subject else "Re: Portfolio Contact"
        mailto_url = f"mailto:{obj.email}?subject={quote(subject_text)}"
        return format_html('<a href="{}" target="_blank">Reply via Email</a>', mailto_url)
