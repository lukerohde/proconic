from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from main.models import Team

class InviteOnlyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return bool(request.session.get('team_share_id'))

    def get_login_redirect_url(self, request):
        """Return the login redirect URL."""
        # Check if there's a team share ID in the session
        team_share_id = request.session.get('team_share_id')
        if team_share_id:
            # Clear it from the session
            del request.session['team_share_id']
            # Redirect to the team join page
            return reverse('team_join_page', kwargs={'share_id': team_share_id})
        
        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request):
        share_id = request.session.get('team_share_id')
        if share_id:
            del request.session['team_share_id']
            return reverse('team_join_page', kwargs={'share_id': share_id})
        return super().get_signup_redirect_url(request)
