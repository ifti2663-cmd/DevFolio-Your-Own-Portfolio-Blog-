from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Category, Comment, Post, Skill


class SecurityAndVisibilityTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "owner-password")
        self.member = User.objects.create_user("member", "member@example.com", "member-password")
        self.category = Category.objects.create(name="Learning")
        self.draft = Post.objects.create(title="Private draft", excerpt="A draft", content="draft content", cover_image="post.png", category=self.category, author=self.owner)
        self.published = Post.objects.create(title="Public post", excerpt="A post", content="word " * 110, cover_image="post.png", category=self.category, author=self.owner, status=Post.Status.PUBLISHED)

    def test_visitor_cannot_write_posts(self):
        response = self.client.post("/api/posts/", {"title": "hack"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_non_superuser_cannot_write(self):
        self.client.force_authenticate(self.member)
        response = self.client.post("/api/skills/", {"name": "Python", "category": "BACKEND", "proficiency": 90}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_registration_route_does_not_exist(self):
        self.assertEqual(self.client.post("/api/auth/register/").status_code, 404)

    def test_draft_is_invisible_but_visible_to_owner(self):
        self.assertEqual(self.client.get(f"/api/posts/{self.draft.slug}/").status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get(f"/api/posts/{self.draft.slug}/").status_code, 200)

    def test_public_comment_response_hides_email(self):
        Comment.objects.create(post=self.published, name="Visitor", email="private@example.com", content="This is public feedback.", is_approved=True)
        response = self.client.get(f"/api/posts/{self.published.slug}/comments/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("email", response.data[0])
