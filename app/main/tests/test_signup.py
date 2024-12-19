from django.test import TestCase, Client, override_settings, modify_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.models import Team
import uuid

User = get_user_model()

@modify_settings(INSTALLED_APPS={'append': 'allauth.account'})
@override_settings(
    ACCOUNT_ADAPTER='main.tests.test_adapter.TestAccountAdapter',
    ACCOUNT_EMAIL_REQUIRED=True,
    ACCOUNT_EMAIL_VERIFICATION='none',  # Email verification disabled for now
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ACCOUNT_UNIQUE_EMAIL=True,
    SITE_ID=1
)
class SignupTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('account_signup')
        self.login_url = reverse('account_login')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        # Create a team and set share_id in session to allow signup
        self.team = Team.objects.create(
            name='Test Team',
            owner=User.objects.create_user(
                username='owner',
                email='owner@example.com',
                password='pass'
            ),
            share_id=uuid.uuid4()
        )
        session = self.client.session
        session['team_share_id'] = str(self.team.share_id)
        session.save()

    def test_signup_page_loads(self):
        """Test that signup page loads correctly with valid team share ID"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_successful_signup(self):
        """Test successful user registration with valid team share ID"""
        response = self.client.post(self.signup_url, self.valid_user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # For future when email verification is enabled:
        # # Check email verification was sent
        # self.assertEqual(len(mail.outbox), 1)
        # self.assertIn('Please Confirm Your Email Address', mail.outbox[0].subject)

    def test_invalid_signup_data(self):
        """Test signup validation with valid team share ID"""
        # Test missing fields
        response = self.client.post(self.signup_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        form = response.context['form']
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)

        # Test invalid email
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', form.errors['email'][0])

        # Test password mismatch
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.signup_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('password2', form.errors)
        self.assertIn('You must type the same password each time', form.errors['password2'][0])

    def test_duplicate_email_signup(self):
        """Test that users cannot sign up with an existing email"""
        # Create first user
        response = self.client.post(self.signup_url, self.valid_user_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful signup
        
        # Log out and set team share ID again
        self.client.logout()
        session = self.client.session
        session['team_share_id'] = str(self.team.share_id)
        session.save()
        
        # Try to create second user with same email
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'testuser2'
        response = self.client.post(self.signup_url, duplicate_data)
        self.assertEqual(response.status_code, 200)  # Should stay on signup page with error
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertContains(response, 'A user is already registered with this email address')
        
        # Check that second user was not created
        self.assertFalse(User.objects.filter(username='testuser2').exists())

@modify_settings(INSTALLED_APPS={'append': 'allauth.account'})
@override_settings(
    ACCOUNT_ADAPTER='main.tests.test_adapter.TestAccountAdapter',
    ACCOUNT_EMAIL_REQUIRED=True,
    ACCOUNT_EMAIL_VERIFICATION='none',  # Email verification disabled for now
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ACCOUNT_UNIQUE_EMAIL=True,
    SITE_ID=1
)
class TeamJoinTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an owner for the team
        self.owner = User.objects.create_user(
            username='teamowner',
            email='owner@example.com',
            password='OwnerPass123!'
        )
        self.team = Team.objects.create(
            name='Test Team',
            owner=self.owner,
            share_id=uuid.uuid4()
        )
        self.team_join_signup_url = reverse('team_join_signup', kwargs={'share_id': self.team.share_id})
        self.team_join_login_url = reverse('team_join_login', kwargs={'share_id': self.team.share_id})
        self.team_join_page_url = reverse('team_join_page', kwargs={'share_id': self.team.share_id})
        self.team_join_action_url = reverse('team_join_action', kwargs={'share_id': self.team.share_id})
        self.signup_url = reverse('account_signup')
        self.login_url = reverse('account_login')
        self.valid_user_data = {
            'username': 'teamuser',
            'email': 'team@example.com',
            'password1': 'TeamPass123!',
            'password2': 'TeamPass123!'
        }

    def test_signup_closed_without_session(self):
        """Test that signup is closed without team_share_id in session"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup_closed.html')

    def test_signup_open_with_session(self):
        """Test that signup is open with team_share_id in session"""
        # First POST to team_join_signup to set session
        response = self.client.post(self.team_join_signup_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.signup_url)
        
        # Now check signup page is open
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_successful_team_join_signup(self):
        """Test successful signup and team join flow"""
        # 1. POST to team_join_signup
        response = self.client.post(self.team_join_signup_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.signup_url)
        
        # 2. POST to account_signup
        response = self.client.post(self.signup_url, self.valid_user_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.team_join_page_url)
        
        # Check user was created and logged in
        user = User.objects.get(username='teamuser')
        self.assertTrue(user.is_authenticated)
        
        # 3. POST to team_join_action
        response = self.client.post(self.team_join_action_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))
        
        # Check user was added to team
        self.assertTrue(user in self.team.members.all())
        
        # Check messages
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(f"You've been added to {self.team.name}!" in str(m) for m in messages))

    def test_successful_team_join_login(self):
        """Test successful login and team join flow"""
        # Create user first
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!'
        )
        
        # 1. POST to team_join_login
        response = self.client.post(self.team_join_login_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.login_url)
        
        # 2. POST to account_login
        login_data = {
            'login': 'existing@example.com',
            'password': 'ExistingPass123!'
        }
        response = self.client.post(self.login_url, login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.team_join_page_url)
        
        # 3. POST to team_join_action
        response = self.client.post(self.team_join_action_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))
        
        # Check user was added to team
        self.assertTrue(user in self.team.members.all())
        
        # Check messages
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(f"You've been added to {self.team.name}!" in str(m) for m in messages))

    def test_team_join_page_unauthenticated(self):
        """Test team join page when user is not logged in"""
        response = self.client.get(self.team_join_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/team_join.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertEqual(response.context['team'], self.team)

    def test_team_join_page_authenticated_not_member(self):
        """Test team join page when user is logged in but not a member"""
        user = User.objects.create_user(
            username='nonmember',
            email='nonmember@example.com',
            password='NonMemberPass123!'
        )
        self.client.force_login(user)
        
        response = self.client.get(self.team_join_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/team_join.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['team'], self.team)
        self.assertFalse(response.context['is_member'])

    def test_team_join_page_authenticated_member(self):
        """Test team join page when user is already a member"""
        user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='MemberPass123!'
        )
        self.team.members.add(user)
        self.client.force_login(user)
        
        response = self.client.get(self.team_join_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/team_join.html')
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['team'], self.team)
        self.assertTrue(response.context['is_member'])

    def test_team_detail_access(self):
        """Test that non-members cannot access team detail page"""
        user = User.objects.create_user(
            username='nonmember',
            email='nonmember@example.com',
            password='NonMemberPass123!'
        )
        self.client.force_login(user)
        
        response = self.client.get(reverse('team_detail', kwargs={'pk': self.team.pk}))
        self.assertEqual(response.status_code, 404)

    def test_invalid_team_share_id(self):
        """Test accessing pages with invalid team share ID"""
        invalid_share_id = uuid.uuid4()
        
        # Test team_join_page (GET)
        url = reverse('team_join_page', kwargs={'share_id': invalid_share_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
        # Test team_join_signup (POST)
        url = reverse('team_join_signup', kwargs={'share_id': invalid_share_id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        
        # Test team_join_login (POST)
        url = reverse('team_join_login', kwargs={'share_id': invalid_share_id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        
        # Test team_join_action (POST)
        url = reverse('team_join_action', kwargs={'share_id': invalid_share_id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_team_join_login_get(self):
        """Test that the team join login link works with GET request"""
        response = self.client.get(reverse('team_join_login', kwargs={'share_id': self.team.share_id}))
        self.assertEqual(response.status_code, 302)  # Should redirect to login page
        self.assertRedirects(response, reverse('account_login'))
        self.assertEqual(self.client.session['team_share_id'], str(self.team.share_id))

    def test_team_join_signup_get(self):
        """Test that the team join signup link works with GET request"""
        response = self.client.get(reverse('team_join_signup', kwargs={'share_id': self.team.share_id}))
        self.assertEqual(response.status_code, 302)  # Should redirect to signup page
        self.assertRedirects(response, reverse('account_signup'))
        self.assertEqual(self.client.session['team_share_id'], str(self.team.share_id))
