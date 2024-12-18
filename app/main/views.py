from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Team, Decision, Option, Pro, Con, Goal, Principle
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db import transaction
from collections import defaultdict
from django.http import HttpResponseRedirect
from django.urls import reverse
from .ai_helpers import call_openai
import logging
from urllib.parse import urlencode

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def team_list(request):
    teams = Team.objects.filter(members=request.user)
    return render(request, 'main/team_list.html', {'teams': teams})

@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk, members=request.user)
    return render(request, 'main/team_detail.html', {
        'team': team,
        'goals': team.goals.all(),
        'principles': team.principles.all(),
        'decisions': team.decisions.all()
    })

@login_required
def team_create(request):
    if request.method == 'POST':
        team = Team.objects.create(
            name=request.POST['name'],
            owner=request.user
        )
        team.members.add(request.user)
        messages.success(request, "Team created successfully!")
        return redirect('team_detail', pk=team.pk)
    return render(request, 'main/team_form.html', {})

@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            team.name = name
            team.save()
            messages.success(request, 'Team updated successfully!')
            return redirect('team_detail', pk=team.pk)
    
    return render(request, 'main/team_edit.html', {'team': team})

@login_required
def decision_list(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decisions = team.decisions.all().order_by('-created_at')
    return render(request, 'main/decision_list.html', {'team': team, 'decisions': decisions})

@login_required
def decision_detail(request, team_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=pk, team=team)
    options = decision.options.all()
    return render(request, 'main/decision_detail.html', {
        'team': team,
        'decision': decision,
        'options': options
    })

@login_required
def decision_create(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    if request.method == 'POST':
        # Form handling will be added later
        decision = Decision.objects.create(
            team=team,
            name=request.POST['name'],
            background=request.POST['background'],
            problem_statement=request.POST['problem_statement']
        )
        messages.success(request, "Decision created successfully!")
        return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)
    return render(request, 'main/decision_form.html', {'team': team})

@login_required
def option_create(request, team_pk, decision_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    if request.method == 'POST':
        # Form handling will be added later
        option = Option.objects.create(
            decision=decision,
            name=request.POST['name'],
            description=request.POST['description']
        )
        # Handle pros and cons
        for pro in request.POST.getlist('pros'):
            Pro.objects.create(option=option, description=pro)
        for con in request.POST.getlist('cons'):
            Con.objects.create(option=option, description=con)
        messages.success(request, "Option added successfully!")
        return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)
    return render(request, 'main/option_form.html', {'team': team, 'decision': decision})

@login_required
def option_edit(request, team_pk, decision_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=pk, decision=decision)
    
    if request.method == 'POST':
        with transaction.atomic():
            option.name = request.POST['name']
            option.description = request.POST['description']
            option.save()
            
            # Clear existing pros and cons
            option.pros.all().delete()
            option.cons.all().delete()
            
            # Add new pros and cons
            for pro in request.POST.getlist('pros'):
                if pro.strip():  # Only add non-empty pros
                    Pro.objects.create(option=option, description=pro)
            for con in request.POST.getlist('cons'):
                if con.strip():  # Only add non-empty cons
                    Con.objects.create(option=option, description=con)
            
            messages.success(request, "Option updated successfully!")
        return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)
    
    return render(request, 'main/option_form.html', {
        'team': team,
        'decision': decision,
        'option': option,
        'pros': [pro.description for pro in option.pros.all()],
        'cons': [con.description for con in option.cons.all()]
    })

@login_required
@require_POST
def option_delete(request, team_pk, decision_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=pk, decision=decision)
    option.delete()
    messages.success(request, "Option deleted successfully!")
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def option_select(request, team_pk, decision_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=pk, decision=decision)
    
    try:
        outcome = request.POST.get('outcome')
        if not outcome:
            messages.error(request, "Please provide an outcome explanation.")
            return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)
            
        decision.selected_option = option
        decision.outcome = outcome
        decision.save()
        
        messages.success(request, f"'{option.name}' selected as the final option!")
        return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)
    except Exception as e:
        messages.error(request, f"Failed to select option: {str(e)}")
        return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def clear_selected_option(request, team_pk, decision_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    
    decision.selected_option = None
    decision.outcome = ""
    decision.save()
    
    messages.success(request, "Selection cleared. The decision is now open again.")
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def pro_create(request, team_pk, decision_pk, option_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=option_pk, decision=decision)
    
    description = request.POST.get('description', '').strip()
    if description:
        Pro.objects.create(option=option, description=description)
        messages.success(request, "Pro added successfully!")
    
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def pro_delete(request, team_pk, decision_pk, option_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=option_pk, decision=decision)
    pro = get_object_or_404(Pro, pk=pk, option=option)
    pro.delete()
    messages.success(request, "Pro deleted successfully!")
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def con_create(request, team_pk, decision_pk, option_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=option_pk, decision=decision)
    
    description = request.POST.get('description', '').strip()
    if description:
        Con.objects.create(option=option, description=description)
        messages.success(request, "Con added successfully!")
    
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
@require_POST
def con_delete(request, team_pk, decision_pk, option_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    decision = get_object_or_404(Decision, pk=decision_pk, team=team)
    option = get_object_or_404(Option, pk=option_pk, decision=decision)
    con = get_object_or_404(Con, pk=pk, option=option)
    con.delete()
    messages.success(request, "Con deleted successfully!")
    return redirect('decision_detail', team_pk=team.pk, pk=decision.pk)

@login_required
def goal_create(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    if request.method == 'POST':
        goal = Goal.objects.create(
            team=team,
            name=request.POST['name'],
            description=request.POST['description']
        )
        messages.success(request, "Goal added successfully!")
        return redirect('team_detail', pk=team.pk)
    return redirect('team_detail', pk=team.pk)

@login_required
def goal_edit(request, team_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    goal_id = request.POST.get('goal_id', pk)
    goal = get_object_or_404(Goal, pk=goal_id, team=team)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            goal.name = name
            goal.description = description
            goal.save()
            messages.success(request, 'Goal updated successfully!')
        return redirect('team_detail', pk=team.pk)
    
    return render(request, 'main/goal_edit.html', {'team': team, 'goal': goal})

@login_required
@require_POST
def goal_delete(request, team_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    goal = get_object_or_404(Goal, pk=pk, team=team)
    goal.delete()
    messages.success(request, "Goal deleted successfully!")
    return redirect('team_detail', pk=team.pk)

@login_required
def principle_create(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    if request.method == 'POST':
        principle = Principle.objects.create(
            team=team,
            name=request.POST['name'],
            description=request.POST['description']
        )
        messages.success(request, "Principle added successfully!")
        return redirect('team_detail', pk=team.pk)
    return redirect('team_detail', pk=team.pk)

@login_required
def principle_edit(request, team_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    principle_id = request.POST.get('principle_id', pk)
    principle = get_object_or_404(Principle, pk=principle_id, team=team)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            principle.name = name
            principle.description = description
            principle.save()
            messages.success(request, 'Principle updated successfully!')
        return redirect('team_detail', pk=team.pk)
    
    return render(request, 'main/principle_edit.html', {'team': team, 'principle': principle})

@login_required
@require_POST
def principle_delete(request, team_pk, pk):
    team = get_object_or_404(Team, pk=team_pk, members=request.user)
    principle = get_object_or_404(Principle, pk=pk, team=team)
    principle.delete()
    messages.success(request, "Principle deleted successfully!")
    return redirect('team_detail', pk=team.pk)

def team_join(request, share_id):
    """Handle team joins via shareable link."""
    team = get_object_or_404(Team, share_id=share_id)
    
    # Store share_id in session
    request.session['team_share_id'] = str(share_id)
    
    if request.user.is_authenticated:
        # Check if user is already a member
        if request.user in team.members.all():
            messages.info(request, f"You're already a member of {team.name}")
        else:
            # Add user to team if they're not already a member
            team.members.add(request.user)
            messages.success(request, f"You've been added to {team.name}!")
        return redirect('team_detail', pk=team.id)
    
    # For unauthenticated users, show the join page
    next_param = urlencode({'next': request.path})
    context = {
        'team': team,
        'signup_url': f"{reverse('account_signup')}?{next_param}",
        'login_url': f"{reverse('account_login')}?{next_param}"
    }
    return render(request, 'main/team_join.html', context)
