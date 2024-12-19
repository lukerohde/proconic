from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from django.contrib import messages
from .models import Team, Goal, Principle, Decision, Option

User = get_user_model()

@receiver(user_signed_up)
def create_default_team(sender, request, user, **kwargs):
    """Create a default team for new users."""
    team = Team.objects.create(
        name=f"{user.username}'s Team",
        owner=user
    )
    team.members.add(user)
    messages.success(request, f"Welcome! We've created {team.name} for you.")

    # Create default decision
    decision = Decision.objects.create(
        team=team,
        name="Example Decision",
        background="This is an example decision to help you get started. Feel free to edit or delete it!",
        problem_statement="What tool should we use for project management?"
    )

    decision.save()
