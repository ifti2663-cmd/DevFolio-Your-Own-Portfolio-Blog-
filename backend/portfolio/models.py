from math import ceil
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimestampedModel):
    full_name = models.CharField(max_length=120)
    headline = models.CharField(max_length=160)
    bio = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="profile/", blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_available_for_hire = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and Profile.objects.exists():
            raise ValidationError("Only one profile may exist.")
        return super().save(*args, **kwargs)

    def __str__(self): return self.full_name


class Skill(TimestampedModel):
    class Category(models.TextChoices):
        FRONTEND = "FRONTEND", "Frontend"; BACKEND = "BACKEND", "Backend"; DATABASE = "DATABASE", "Database"
        DEVOPS = "DEVOPS", "DevOps"; TOOLS = "TOOLS", "Tools"; SOFT_SKILL = "SOFT_SKILL", "Soft skill"
    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=20, choices=Category)
    proficiency = models.PositiveSmallIntegerField()
    icon = models.CharField(max_length=120, blank=True)
    display_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta: ordering = ("display_order", "name")
    def __str__(self): return self.name


class Experience(TimestampedModel):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full time"; PART_TIME = "PART_TIME", "Part time"; INTERNSHIP = "INTERNSHIP", "Internship"
        FREELANCE = "FREELANCE", "Freelance"; CONTRACT = "CONTRACT", "Contract"
    company = models.CharField(max_length=150); role = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=20, choices=EmploymentType)
    location = models.CharField(max_length=120); start_date = models.DateField(); end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False); description = models.TextField(); company_url = models.URLField(blank=True)
    display_order = models.IntegerField(default=0)
    class Meta: ordering = ("-start_date",)
    def __str__(self): return f"{self.role} at {self.company}"


class Education(TimestampedModel):
    institution = models.CharField(max_length=160); degree = models.CharField(max_length=160); field_of_study = models.CharField(max_length=160)
    start_year = models.PositiveIntegerField(); end_year = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=40, blank=True); description = models.TextField(blank=True)
    class Meta: ordering = ("-start_year",)
    def __str__(self): return f"{self.degree} - {self.institution}"


class Project(TimestampedModel):
    class Category(models.TextChoices):
        WEB = "WEB", "Web"; MOBILE = "MOBILE", "Mobile"; API = "API", "API"; ML = "ML", "Machine learning"; OTHER = "OTHER", "Other"
    title = models.CharField(max_length=180, unique=True); slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=200); description = models.TextField(); cover_image = models.ImageField(upload_to="projects/")
    tech_stack = models.ManyToManyField(Skill, related_name="projects")
    category = models.CharField(max_length=10, choices=Category); live_url = models.URLField(blank=True); github_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False); completed_date = models.DateField(); display_order = models.IntegerField(default=0)
    class Meta: ordering = ("display_order", "-completed_date")
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    def __str__(self): return self.title


class Category(TimestampedModel):
    name = models.CharField(max_length=80, unique=True); slug = models.SlugField(unique=True, blank=True); description = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    def __str__(self): return self.name


class Tag(TimestampedModel):
    name = models.CharField(max_length=80, unique=True); slug = models.SlugField(unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    def __str__(self): return self.name


class Post(TimestampedModel):
    class Status(models.TextChoices): DRAFT = "DRAFT", "Draft"; PUBLISHED = "PUBLISHED", "Published"
    title = models.CharField(max_length=200); slug = models.SlugField(unique=True, blank=True)
    excerpt = models.CharField(max_length=300); content = models.TextField(); cover_image = models.ImageField(upload_to="posts/")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="posts")
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts")
    status = models.CharField(max_length=10, choices=Status, default=Status.DRAFT); published_at = models.DateTimeField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0); reading_time = models.PositiveSmallIntegerField(default=1)
    is_featured = models.BooleanField(default=False)
    class Meta: ordering = ("-published_at",)
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        self.reading_time = max(1, ceil(len(self.content.split()) / 200))
        if self.status == self.Status.PUBLISHED and not self.published_at: self.published_at = timezone.now()
        return super().save(*args, **kwargs)
    def __str__(self): return self.title


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    visitor_id = models.CharField(max_length=64); ip_address = models.GenericIPAddressField(null=True, blank=True); created_at = models.DateTimeField(auto_now_add=True)
    class Meta: constraints = [models.UniqueConstraint(fields=("post", "visitor_id"), name="unique_post_visitor_like")]


class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="view_visitors")
    visitor_id = models.CharField(max_length=64); last_viewed_at = models.DateTimeField(auto_now=True)
    class Meta: constraints = [models.UniqueConstraint(fields=("post", "visitor_id"), name="unique_post_visitor_view")]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=120); email = models.EmailField(); website = models.URLField(blank=True)
    content = models.TextField(); parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    is_approved = models.BooleanField(default=False); created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("-created_at",)


class ContactMessage(models.Model):
    name = models.CharField(max_length=120); email = models.EmailField(); subject = models.CharField(max_length=200); message = models.TextField()
    is_read = models.BooleanField(default=False); created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("-created_at",)
