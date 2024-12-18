from django.db import models
from django.contrib.auth import get_user_model
from .utils import do_something_handy
from uuid import uuid4
from django.utils import timezone

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    share_id = models.UUIDField(default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(get_user_model(), related_name='teams')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_share_url(self):
        from django.urls import reverse
        return reverse('team_join', kwargs={'share_id': self.share_id})

class Goal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Principle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='principles')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Decision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='decisions')
    name = models.CharField(max_length=255)
    background = models.TextField(blank=True)
    problem_statement = models.TextField()
    selected_option = models.ForeignKey('Option', null=True, blank=True, on_delete=models.SET_NULL, related_name='selected_for')
    outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Option(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    decision = models.ForeignKey(Decision, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Pro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='pros')
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description[:50]

class Con(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='cons')
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description[:50]
