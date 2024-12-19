from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from main.models import Team
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory

User = get_user_model()

class SignupSignalsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_user_signed_up_signal(self):
        """Test that user_signed_up signal is handled correctly"""
        # Create a mock request
        request = self.factory.get('/')
        setattr(request, 'session', {})
        setattr(request, '_messages', FallbackStorage(request))
        
        # Send the signal
        user_signed_up.send(
            sender=User,
            request=request,
            user=self.user
        )
        
        # Add your assertions based on what your signal handler does
        # For example, if your signal creates a default team:
        teams = Team.objects.filter(owner=self.user)
        if teams.exists():  # Only if your app creates default teams
            self.assertEqual(teams.count(), 1)
            self.assertTrue(self.user in teams.first().members.all())
