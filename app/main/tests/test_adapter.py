from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from main.models import Team
from django.http import Http404

class TestAccountAdapter(DefaultAccountAdapter):
    """Account adapter for testing that allows open signup only with team share ID."""
    def is_open_for_signup(self, request):
        """Only allow signup if there's a team share ID in the session."""
        team_share_id = request.session.get('team_share_id')
        if team_share_id:
            try:
                Team.objects.get(share_id=team_share_id)
                return True
            except Team.DoesNotExist:
                raise Http404("Team not found")
        return False

    def get_login_redirect_url(self, request):
        """Return the login redirect URL."""
        # Check if there's a team share ID in the session
        team_share_id = request.session.get('team_share_id')
        if team_share_id:
            try:
                team = Team.objects.get(share_id=team_share_id)
                # Clear it from the session
                del request.session['team_share_id']
                # Redirect to the team join page
                return reverse('team_join_page', kwargs={'share_id': team_share_id})
            except Team.DoesNotExist:
                raise Http404("Team not found")
        
        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request):
        """Return the signup redirect URL."""
        share_id = request.session.get('team_share_id')
        if share_id:
            try:
                team = Team.objects.get(share_id=share_id)
                del request.session['team_share_id']
                return reverse('team_join_page', kwargs={'share_id': share_id})
            except Team.DoesNotExist:
                raise Http404("Team not found")
        return super().get_signup_redirect_url(request)

    def pre_login(self, request, user, **kwargs):
        """Called before login. Verify team exists if share_id is in session."""
        team_share_id = request.session.get('team_share_id')
        if team_share_id:
            try:
                Team.objects.get(share_id=team_share_id)
            except Team.DoesNotExist:
                raise Http404("Team not found")
        return super().pre_login(request, user, **kwargs)

    def pre_signup(self, request, user, **kwargs):
        """Called before signup. Verify team exists if share_id is in session."""
        team_share_id = request.session.get('team_share_id')
        if team_share_id:
            try:
                Team.objects.get(share_id=team_share_id)
            except Team.DoesNotExist:
                raise Http404("Team not found")
        return super().pre_signup(request, user, **kwargs)

    # For future when email verification is enabled:
    # def send_confirmation_mail(self, request, emailconfirmation, signup):
    #     """Override to ensure email confirmation is sent."""
    #     super().send_confirmation_mail(request, emailconfirmation, signup)
    #     
    #     # For testing, auto-verify the email
    #     email_address = emailconfirmation.email_address
    #     email_address.verified = True
    #     email_address.save()
