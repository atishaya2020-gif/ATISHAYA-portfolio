from django.db import models


class Project(models.Model):
    class Category(models.TextChoices):
        FULLSTACK = 'fullstack', 'Fullstack'
        FRONTEND = 'frontend', 'Frontend'
        BACKEND = 'backend', 'Backend'
        TOOLING = 'tooling', 'Tooling'

    class Status(models.TextChoices):
        COMPLETED = 'completed', 'Completed'
        IN_PROGRESS = 'in_progress', 'In Progress'

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    api_url = models.URLField(blank=True)
    overview = models.TextField(blank=True)
    technologies = models.ManyToManyField(
        'Technology',
        blank=True,
        related_name='projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self) -> str:
        return self.title


class Technology(models.Model):
    class Category(models.TextChoices):
        BACKEND = 'backend', 'Backend'
        FRONTEND = 'frontend', 'Frontend'
        DATABASE = 'database', 'Database'
        CLOUD_DEPLOYMENT = 'cloud_deployment', 'Cloud / Deployment'
        TOOLS = 'tools', 'Tools'

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self) -> str:
        return self.name


class ProjectFeature(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='features',
    )
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['project', 'order']

    def __str__(self) -> str:
        return f'{self.project.title} — {self.text}'


class ProjectArchitecture(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='architecture_items',
    )
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['project', 'order']

    def __str__(self) -> str:
        return f'{self.project.title} — architecture item #{self.order}'


class Profile(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    introduction = models.TextField()
    philosophy = models.TextField(blank=True)
    career_goal = models.TextField(blank=True)
    current_focus = models.TextField(blank=True)
    what_i_build = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self) -> str:
        return f'{self.name} ({self.role})'


class Education(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='education',
    )
    label = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['profile', 'order']

    def __str__(self) -> str:
        return f'{self.profile.name} — {self.title}'


class ProfileFocus(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='focus_items',
    )
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['profile', 'order']

    def __str__(self) -> str:
        return f'{self.profile.name} — {self.label}: {self.value}'
