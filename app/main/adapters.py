from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from .models import Team

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Check if there's a team share_id in the session
        share_id = request.session.get('team_share_id')
        if share_id:
            # Clear the session variable
            del request.session['team_share_id']
            
            # Try to find and join the team
            try:
                team = Team.objects.get(share_id=share_id)
                if request.user not in team.members.all():
                    team.members.add(request.user)
                return reverse('team_detail', kwargs={'pk': team.pk})
            except Team.DoesNotExist:
                pass
        
        # Default redirect
        return reverse('team_list')
