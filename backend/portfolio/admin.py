from django.contrib import admin

from .models import (
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
