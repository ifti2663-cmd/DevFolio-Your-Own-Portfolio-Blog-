from django.contrib.auth import password_validation
from django.db.models import Count
from rest_framework import serializers
from .models import Category, Comment, ContactMessage, Education, Experience, Post, Project, Profile, Skill, Tag


def absolute_url(request, value):
    return request.build_absolute_uri(value.url) if request and value else None


def validate_upload(file, extensions, max_bytes, label):
    if not file:
        return file
    if file.size > max_bytes:
        raise serializers.ValidationError(f"{label} must be no larger than {max_bytes // 1024 // 1024} MB.")
    extension = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
    if extension not in extensions:
        raise serializers.ValidationError(f"{label} must be one of: {', '.join(sorted(extensions))}.")
    return file


class AbsoluteMediaMixin:
    def media_url(self, obj, field): return absolute_url(self.context.get("request"), getattr(obj, field))
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        for field in getattr(self, "absolute_media_fields", ()):
            value = getattr(instance, field)
            if value:
                data[field] = absolute_url(request, value)
        return data


class ProfileSerializer(AbsoluteMediaMixin, serializers.ModelSerializer):
    absolute_media_fields = ("avatar", "resume")
    avatar_url = serializers.SerializerMethodField(); resume_url = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")
    def get_avatar_url(self, obj): return self.media_url(obj, "avatar")
    def get_resume_url(self, obj): return self.media_url(obj, "resume")
    def validate_avatar(self, value): return validate_upload(value, {"jpg", "jpeg", "png", "webp"}, 2 * 1024 * 1024, "Avatar")
    def validate_resume(self, value): return validate_upload(value, {"pdf"}, 5 * 1024 * 1024, "Resume")


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill; fields = "__all__"; read_only_fields = ("created_at", "updated_at")
    def validate_proficiency(self, value):
        if not 1 <= value <= 100: raise serializers.ValidationError("Proficiency must be between 1 and 100.")
        return value


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience; fields = "__all__"; read_only_fields = ("created_at", "updated_at")
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        value = lambda field: attrs.get(field, getattr(instance, field, None))
        from django.utils.timezone import localdate
        if value("start_date") and value("start_date") > localdate():
            raise serializers.ValidationError({"start_date": "Start date cannot be in the future."})
        if value("is_current") and value("end_date"):
            raise serializers.ValidationError({"end_date": "Current roles cannot have an end date."})
        if not value("is_current") and not value("end_date"):
            raise serializers.ValidationError({"end_date": "End date is required unless this is your current role."})
        if value("end_date") and value("start_date") and value("end_date") <= value("start_date"):
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        return attrs


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education; fields = "__all__"; read_only_fields = ("created_at", "updated_at")


class ProjectSerializer(AbsoluteMediaMixin, serializers.ModelSerializer):
    absolute_media_fields = ("cover_image",)
    cover_image_url = serializers.SerializerMethodField()
    tech_stack_details = SkillSerializer(source="tech_stack", many=True, read_only=True)
    class Meta:
        model = Project; fields = "__all__"; read_only_fields = ("slug", "created_at", "updated_at")
    def get_cover_image_url(self, obj): return self.media_url(obj, "cover_image")
    def validate_cover_image(self, value): return validate_upload(value, {"jpg", "jpeg", "png", "webp"}, 2 * 1024 * 1024, "Cover image")
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        live = attrs.get("live_url", getattr(instance, "live_url", ""))
        github = attrs.get("github_url", getattr(instance, "github_url", ""))
        if not live and not github: raise serializers.ValidationError("Provide at least one of live_url or github_url.")
        return attrs


class TaxonomySerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category; fields = ("id", "name", "slug", "description", "posts_count", "created_at", "updated_at")
        read_only_fields = ("slug", "posts_count", "created_at", "updated_at")


class TagSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Tag; fields = ("id", "name", "slug", "posts_count", "created_at", "updated_at")
        read_only_fields = ("slug", "posts_count", "created_at", "updated_at")


class PostSummarySerializer(AbsoluteMediaMixin, serializers.ModelSerializer):
    absolute_media_fields = ("cover_image",)
    category = TaxonomySerializer(read_only=True); tags = TagSerializer(many=True, read_only=True)
    cover_image_url = serializers.SerializerMethodField(); likes_count = serializers.IntegerField(read_only=True); comments_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ("id", "title", "slug", "excerpt", "cover_image", "cover_image_url", "category", "tags", "status", "published_at", "views_count", "reading_time", "is_featured", "likes_count", "comments_count", "created_at", "updated_at")
    def get_cover_image_url(self, obj): return self.media_url(obj, "cover_image")


class PostSerializer(PostSummarySerializer):
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=Category.objects.all(), write_only=True, required=False)
    tag_ids = serializers.PrimaryKeyRelatedField(source="tags", queryset=Tag.objects.all(), many=True, write_only=True, required=False)
    content = serializers.CharField(); author = serializers.StringRelatedField(read_only=True)
    is_liked = serializers.SerializerMethodField(); related_posts = serializers.SerializerMethodField()
    class Meta(PostSummarySerializer.Meta):
        fields = PostSummarySerializer.Meta.fields + ("content", "author", "category_id", "tag_ids", "is_liked", "related_posts")
        read_only_fields = ("slug", "published_at", "views_count", "reading_time", "created_at", "updated_at")
    def get_is_liked(self, obj):
        visitor_id = self.context.get("request").headers.get("X-Visitor-Id") if self.context.get("request") else None
        return bool(visitor_id and obj.likes.filter(visitor_id=visitor_id).exists())
    def get_related_posts(self, obj):
        posts = Post.objects.filter(category=obj.category, status=Post.Status.PUBLISHED).exclude(pk=obj.pk).annotate(likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True))[:3]
        return PostSummarySerializer(posts, many=True, context=self.context).data
    def validate_cover_image(self, value): return validate_upload(value, {"jpg", "jpeg", "png", "webp"}, 2 * 1024 * 1024, "Cover image")
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        title = attrs.get("title", getattr(instance, "title", ""))
        content = attrs.get("content", getattr(instance, "content", ""))
        status = attrs.get("status", getattr(instance, "status", Post.Status.DRAFT))
        category = attrs.get("category", getattr(instance, "category", None))
        if len(title.strip()) < 5: raise serializers.ValidationError({"title": "Title must be at least 5 characters."})
        if status == Post.Status.PUBLISHED and len(content.split()) < 100:
            raise serializers.ValidationError({"content": "Published posts need at least 100 words."})
        if status == Post.Status.PUBLISHED and not category:
            raise serializers.ValidationError({"category_id": "A category is required to publish a post."})
        return attrs
    def create(self, validated_data):
        tags = validated_data.pop("tags", []); post = Post.objects.create(author=self.context["request"].user, **validated_data); post.tags.set(tags); return post
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for field, value in validated_data.items(): setattr(instance, field, value)
        instance.save()
        if tags is not None: instance.tags.set(tags)
        return instance


class PublicCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment; fields = ("id", "name", "website", "content", "parent", "created_at", "replies")
    def get_replies(self, obj):
        return PublicCommentSerializer(obj.replies.filter(is_approved=True), many=True).data


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment; fields = ("name", "email", "website", "content", "parent")
    def validate_name(self, value):
        if len(value.strip()) < 2: raise serializers.ValidationError("Name must be at least 2 characters.")
        return value
    def validate_content(self, value):
        if not 5 <= len(value.strip()) <= 1000: raise serializers.ValidationError("Comment must be between 5 and 1000 characters.")
        return value
    def validate_parent(self, value):
        if value and value.parent_id: raise serializers.ValidationError("Replies may be only one level deep.")
        return value


class OwnerCommentSerializer(serializers.ModelSerializer):
    post_slug = serializers.CharField(source="post.slug", read_only=True)
    class Meta:
        model = Comment; fields = "__all__"; read_only_fields = ("post", "created_at")


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage; fields = "__all__"; read_only_fields = ("is_read", "created_at")
    def validate_message(self, value):
        if not 10 <= len(value.strip()) <= 2000: raise serializers.ValidationError("Message must be between 10 and 2000 characters.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True); new_password = serializers.CharField(write_only=True)
    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value): raise serializers.ValidationError("Your current password is incorrect.")
        return value
    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context["request"].user)
        return value
