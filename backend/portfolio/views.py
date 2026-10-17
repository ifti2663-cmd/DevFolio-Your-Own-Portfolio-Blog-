from datetime import timedelta
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Count, F, Sum
from django.db.models.deletion import ProtectedError
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Comment, ContactMessage, Education, Experience, Post, PostLike, PostView, Profile, Project, Skill, Tag
from .permissions import IsOwnerOrReadOnly
from .serializers import (Category, ChangePasswordSerializer, CommentCreateSerializer, ContactMessageSerializer, EducationSerializer,
    ExperienceSerializer, OwnerCommentSerializer, PostSerializer, PostSummarySerializer, ProfileSerializer, ProjectSerializer,
    PublicCommentSerializer, SkillSerializer, TagSerializer, TaxonomySerializer)
from .throttles import CommentThrottle, ContactThrottle, LikeThrottle


def is_owner(user): return bool(user and user.is_authenticated and user.is_superuser)


class PageSize10(PageNumberPagination): page_size = 10
class PostsPagination(PageNumberPagination): page_size = 6
class ProjectsPagination(PageNumberPagination): page_size = 9


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username, password = request.data.get("username", ""), request.data.get("password", "")
        user = authenticate(request, username=username, password=password)
        if not user or not user.is_superuser:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh), "user": {"id": user.id, "username": user.username, "email": user.email}})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not is_owner(request.user): raise PermissionDenied()
        try:
            RefreshToken(request.data["refresh"]).blacklist()
        except (KeyError, Exception):
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not is_owner(request.user): raise PermissionDenied()
        return Response({"id": request.user.id, "username": request.user.username, "email": request.user.email})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if not is_owner(request.user): raise PermissionDenied()
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request}); serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"]); request.user.save()
        return Response({"detail": "Password updated."})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer; permission_classes = [IsOwnerOrReadOnly]
    def get_object(self): return get_object_or_404(Profile.objects.all(), pk=Profile.objects.values_list("pk", flat=True).first())


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all(); serializer_class = SkillSerializer; permission_classes = [IsOwnerOrReadOnly]
    filterset_fields = ("category", "is_featured"); search_fields = ("name",); ordering_fields = ("display_order", "proficiency", "name")


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all(); serializer_class = ExperienceSerializer; permission_classes = [IsOwnerOrReadOnly]


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all(); serializer_class = EducationSerializer; permission_classes = [IsOwnerOrReadOnly]


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer; permission_classes = [IsOwnerOrReadOnly]; pagination_class = ProjectsPagination
    lookup_field = "slug"; search_fields = ("title", "summary", "description"); ordering_fields = ("completed_date", "display_order", "title")
    def get_queryset(self):
        qs = Project.objects.prefetch_related("tech_stack").all()
        category, featured, tech = self.request.query_params.get("category"), self.request.query_params.get("is_featured"), self.request.query_params.get("tech")
        if category: qs = qs.filter(category=category)
        if featured in ("true", "false"): qs = qs.filter(is_featured=featured == "true")
        if tech: qs = qs.filter(tech_stack__id=tech) if tech.isdigit() else qs.filter(tech_stack__name__iexact=tech)
        return qs.distinct()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TaxonomySerializer; permission_classes = [IsOwnerOrReadOnly]; lookup_field = "slug"
    def get_queryset(self): return Category.objects.annotate(posts_count=Count("posts", filter=__import__("django.db.models", fromlist=["Q"]).Q(posts__status=Post.Status.PUBLISHED))).order_by("name")
    def destroy(self, request, *args, **kwargs):
        try: return super().destroy(request, *args, **kwargs)
        except ProtectedError: return Response({"detail": "This category is used by a post and cannot be deleted."}, status=400)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer; permission_classes = [IsOwnerOrReadOnly]; lookup_field = "slug"
    def get_queryset(self): return Tag.objects.annotate(posts_count=Count("posts", filter=__import__("django.db.models", fromlist=["Q"]).Q(posts__status=Post.Status.PUBLISHED))).order_by("name")


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer; permission_classes = [IsOwnerOrReadOnly]; pagination_class = PostsPagination; lookup_field = "slug"
    search_fields = ("title", "excerpt", "content"); ordering_fields = ("published_at", "views_count", "likes_count", "title")
    def get_queryset(self):
        qs = Post.objects.select_related("category", "author").prefetch_related("tags").annotate(likes_count=Count("likes", distinct=True), comments_count=Count("comments", filter=__import__("django.db.models", fromlist=["Q"]).Q(comments__is_approved=True), distinct=True))
        if not is_owner(self.request.user): qs = qs.filter(status=Post.Status.PUBLISHED)
        else:
            requested_status = self.request.query_params.get("status")
            if requested_status in (Post.Status.DRAFT, Post.Status.PUBLISHED): qs = qs.filter(status=requested_status)
        category, tag, featured = self.request.query_params.get("category"), self.request.query_params.get("tag"), self.request.query_params.get("is_featured")
        if category: qs = qs.filter(category__slug=category)
        if tag: qs = qs.filter(tags__slug=tag)
        if featured in ("true", "false"): qs = qs.filter(is_featured=featured == "true")
        return qs.distinct()
    def get_serializer_class(self): return PostSummarySerializer if self.action == "list" else PostSerializer
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object(); visitor_id = request.headers.get("X-Visitor-Id")
        if visitor_id:
            record, created = PostView.objects.get_or_create(post=post, visitor_id=visitor_id)
            if created or record.last_viewed_at < timezone.now() - timedelta(hours=1):
                if not created: PostView.objects.filter(pk=record.pk).update(last_viewed_at=timezone.now())
                Post.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1); post.refresh_from_db()
        return Response(self.get_serializer(post).data)
    @action(detail=True, methods=["post"], permission_classes=[AllowAny], throttle_classes=[LikeThrottle])
    def like(self, request, slug=None):
        visitor_id = request.headers.get("X-Visitor-Id")
        if not visitor_id: return Response({"detail": "X-Visitor-Id header is required."}, status=400)
        post = self.get_object(); like, created = PostLike.objects.get_or_create(post=post, visitor_id=visitor_id, defaults={"ip_address": request.META.get("REMOTE_ADDR")})
        if not created: like.delete()
        return Response({"liked": created, "likes_count": post.likes.count()})
    @action(detail=True, methods=["get", "post"], permission_classes=[AllowAny], throttle_classes=[CommentThrottle])
    def comments(self, request, slug=None):
        post = self.get_object()
        if request.method == "GET":
            comments = post.comments.filter(is_approved=True, parent__isnull=True).prefetch_related("replies")
            return Response(PublicCommentSerializer(comments, many=True).data)
        serializer = CommentCreateSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        parent = serializer.validated_data.get("parent")
        if parent and parent.post_id != post.id: return Response({"parent": ["Reply must belong to this post."]}, status=400)
        Comment.objects.create(post=post, **serializer.validated_data)
        return Response({"detail": "Your comment is awaiting approval."}, status=201)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("post", "parent"); serializer_class = OwnerCommentSerializer; permission_classes = [IsAuthenticated]; pagination_class = PageSize10
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not is_owner(request.user): raise PermissionDenied()
    def get_queryset(self):
        qs = super().get_queryset(); approved, post = self.request.query_params.get("is_approved"), self.request.query_params.get("post")
        if approved in ("true", "false"): qs = qs.filter(is_approved=approved == "true")
        if post: qs = qs.filter(post__slug=post)
        return qs
    def create(self, request, *args, **kwargs): return Response({"detail": "Comments are created through a post endpoint."}, status=405)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer; pagination_class = PageSize10
    def get_permissions(self): return [AllowAny()] if self.action == "create" else [IsAuthenticated()]
    def get_throttles(self): return [ContactThrottle()] if self.action == "create" else []
    def get_queryset(self):
        if not is_owner(self.request.user): return ContactMessage.objects.none()
        qs = ContactMessage.objects.all(); unread = self.request.query_params.get("is_read")
        if unread in ("true", "false"): qs = qs.filter(is_read=unread == "true")
        return qs
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.action != "create" and not is_owner(request.user): raise PermissionDenied()
    def update(self, request, *args, **kwargs):
        instance = self.get_object(); instance.is_read = request.data.get("is_read", instance.is_read); instance.save(update_fields=["is_read"])
        return Response(self.get_serializer(instance).data)


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not is_owner(request.user): raise PermissionDenied()
        posts = Post.objects.all()
        return Response({
            "total_posts": posts.count(), "published_posts": posts.filter(status=Post.Status.PUBLISHED).count(), "draft_posts": posts.filter(status=Post.Status.DRAFT).count(),
            "total_projects": Project.objects.count(), "total_skills": Skill.objects.count(), "total_comments": Comment.objects.count(),
            "pending_comments": Comment.objects.filter(is_approved=False).count(), "total_likes": PostLike.objects.count(),
            "total_views": posts.aggregate(total=Sum("views_count"))["total"] or 0, "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
            "top_posts": list(posts.annotate(likes=Count("likes"), views=F("views_count")).order_by("-views_count")[:5].values("title", "slug", "views", "likes")),
            "recent_comments": OwnerCommentSerializer(Comment.objects.select_related("post")[:5], many=True).data,
            "posts_per_month": list(posts.filter(published_at__gte=timezone.now() - timedelta(days=183)).annotate(month=TruncMonth("published_at")).values("month").annotate(count=Count("id")).order_by("month")),
        })
