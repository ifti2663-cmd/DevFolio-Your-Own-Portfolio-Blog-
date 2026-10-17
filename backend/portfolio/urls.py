from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (CategoryViewSet, ChangePasswordView, CommentViewSet, ContactViewSet, DashboardStatsView, EducationViewSet,
    ExperienceViewSet, LoginView, LogoutView, MeView, PostViewSet, ProfileView, ProjectViewSet, SkillViewSet, TagViewSet)

router = DefaultRouter()
router.register("skills", SkillViewSet, basename="skill"); router.register("experiences", ExperienceViewSet, basename="experience")
router.register("education", EducationViewSet, basename="education"); router.register("projects", ProjectViewSet, basename="project")
router.register("posts", PostViewSet, basename="post"); router.register("comments", CommentViewSet, basename="comment")
router.register("categories", CategoryViewSet, basename="category"); router.register("tags", TagViewSet, basename="tag")
router.register("contact", ContactViewSet, basename="contact")

urlpatterns = [
    path("auth/login/", LoginView.as_view()), path("auth/refresh/", TokenRefreshView.as_view()), path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()), path("auth/change-password/", ChangePasswordView.as_view()), path("profile/", ProfileView.as_view()),
    path("dashboard/stats/", DashboardStatsView.as_view()), path("", include(router.urls)),
]
