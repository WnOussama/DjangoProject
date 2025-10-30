from django.test import TestCase, Client
from django.urls import reverse
from apps.app_users.models import User, Profile
from apps.app_home.models import Posts

class UserBasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass123')

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        print("✅ User creation test passed!")
    
    def test_user_has_profile(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        print("✅ User profile test passed!")

    def test_login_page_loads(self):
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
        print("✅ Login page test passed!")

    def test_user_can_login(self):
        logged_in = self.client.login(email='test@test.com', password='testpass123')
        self.assertTrue(logged_in)
        print("✅ User login test passed!")

    def test_homepage_requires_login(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 302)  # Should redirect unauthenticated users
        print("✅ Homepage authentication test passed!")

class PostTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass123')
        self.client = Client()
        self.client.login(email='test@test.com', password='testpass123')
        self.profile = self.user.profile

    def test_create_post(self):
        post = Posts.objects.create(author=self.profile, content='This is a test post!')
        self.assertEqual(Posts.objects.count(), 1)
        self.assertEqual(post.content, 'This is a test post!')
        print("✅ Post creation test passed!")

    def test_post_update(self):
        post = Posts.objects.create(author=self.profile, content='To update')
        post.content = 'Updated!'
        post.save()
        updated = Posts.objects.get(pk=post.pk)
        self.assertEqual(updated.content, 'Updated!')
        print("✅ Post update test passed!")

    def test_post_delete(self):
        post = Posts.objects.create(author=self.profile, content='To delete')
        post_pk = post.pk
        post.delete()
        self.assertFalse(Posts.objects.filter(pk=post_pk).exists())
        print("✅ Post delete test passed!")
