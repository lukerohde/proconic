from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Team, Goal, Principle, Decision, Option

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_team(sender, instance, created, **kwargs):
    """Create a default team for new users."""
    if created:
        team = Team.objects.create(
            name="My Team",
            owner=instance,
        )
        team.members.add(instance)
        
        # Add some default goals to help users get started
        team.goals.create(
            name="Make better decisions",
            description="Use this space to track and improve our decision-making process."
        )
        
        # Add some default principles
        team.principles.create(
            name="Data-Driven Decisions",
            description="Base decisions on evidence and data when possible."
        )
        team.principles.create(
            name="Collaborative Process",
            description="Include relevant stakeholders in important decisions."
        )

        # Create a sample decision to demonstrate the platform
        decision = Decision.objects.create(
            team=team,
            name="Choose Our Project Management Tool",
            background="Our team needs a project management tool to help us collaborate effectively.",
            problem_statement="Which project management tool should we adopt that best fits our team's needs while staying within budget?"
        )

        # Add sample options with pros and cons
        option1 = Option.objects.create(
            decision=decision,
            name="Jira",
            description="Enterprise-grade project management tool by Atlassian"
        )
        option1.pros.create(description="Powerful and feature-rich")
        option1.pros.create(description="Great for agile development")
        option1.cons.create(description="Can be complex to set up")
        option1.cons.create(description="More expensive than alternatives")

        option2 = Option.objects.create(
            decision=decision,
            name="Trello",
            description="Simple, visual project management tool"
        )
        option2.pros.create(description="Easy to use and intuitive")
        option2.pros.create(description="Free tier available")
        option2.cons.create(description="Limited features in free tier")
        option2.cons.create(description="May not scale well for large teams")

        option3 = Option.objects.create(
            decision=decision,
            name="ClickUp",
            description="Modern, all-in-one productivity platform"
        )
        option3.pros.create(description="Flexible and customizable")
        option3.pros.create(description="Good balance of features and usability")
        option3.cons.create(description="Newer platform, less established")
        option3.cons.create(description="Can be overwhelming with too many features")

        # Select the final option and add outcome
        decision.selected_option = option2
        decision.outcome = """After evaluating all options, we chose Trello because:
1. It's the easiest to get started with
2. The free tier meets our current needs
3. We can upgrade later if needed
4. The team is already familiar with it"""
        decision.save()
