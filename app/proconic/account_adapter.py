from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from main.models import Team
from urllib.parse import urlencode

class InviteOnlyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Check both session and query params for share_id
        share_id = request.session.get('team_share_id') or request.GET.get('share_id')
        if not share_id:
            return False
            
        # Verify the share_id exists
        try:
            Team.objects.get(share_id=share_id)
            return True
        except (Team.DoesNotExist, ValueError):
            return False

    def get_signup_redirect_url(self, request):
        # Get share_id from session or query params
        share_id = request.session.get('team_share_id') or request.GET.get('share_id')
        
        if share_id:
            try:
                team = Team.objects.get(share_id=share_id)
                # Add user to team
                team.members.add(request.user)
                # Redirect to team page
                return reverse('team_detail', kwargs={'pk': team.id})
            except (Team.DoesNotExist, ValueError):
                pass
                
        return super().get_signup_redirect_url(request)