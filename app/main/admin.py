from django.contrib import admin
from django.utils.html import format_html
from .models import Team, Decision, Option, Pro, Con, Goal, Principle

class GoalInline(admin.TabularInline):
    model = Goal
    extra = 0
    fields = ('name', 'description')

class PrincipleInline(admin.TabularInline):
    model = Principle
    extra = 0
    fields = ('name', 'description')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'member_count', 'decision_count', 'created_at')
    list_filter = ('owner',)
    search_fields = ('name', 'owner__username')
    inlines = [GoalInline, PrincipleInline]
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    
    def decision_count(self, obj):
        return obj.decisions.count()
    decision_count.short_description = 'Decisions'

class ProInline(admin.TabularInline):
    model = Pro
    extra = 0
    fields = ('description',)

class ConInline(admin.TabularInline):
    model = Con
    extra = 0
    fields = ('description',)

class OptionInline(admin.StackedInline):
    model = Option
    extra = 0
    fields = ('name', 'description')
    show_change_link = True

@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_link', 'status', 'option_count', 'created_at')
    list_filter = ('team', 'created_at')
    search_fields = ('name', 'team__name', 'problem_statement')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'team')
        }),
        ('Details', {
            'fields': ('background', 'problem_statement'),
            'classes': ('collapse',)
        }),
        ('Outcome', {
            'fields': ('selected_option', 'outcome'),
            'classes': ('collapse',)
        })
    )
    
    def team_link(self, obj):
        url = f"/admin/main/team/{obj.team.id}"
        return format_html('<a href="{}">{}</a>', url, obj.team.name)
    team_link.short_description = 'Team'
    
    def status(self, obj):
        if obj.selected_option:
            return format_html(
                '<span style="color: green;">✓ Decided</span>'
            )
        return format_html(
            '<span style="color: orange;">⋯ In Progress</span>'
        )
    status.short_description = 'Status'
    
    def option_count(self, obj):
        return obj.options.count()
    option_count.short_description = 'Options'

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'decision_link', 'pro_count', 'con_count', 'is_selected')
    list_filter = ('decision__team', 'decision')
    search_fields = ('name', 'description', 'decision__name')
    inlines = [ProInline, ConInline]
    
    def decision_link(self, obj):
        url = f"/admin/main/decision/{obj.decision.id}"
        return format_html('<a href="{}">{}</a>', url, obj.decision.name)
    decision_link.short_description = 'Decision'
    
    def pro_count(self, obj):
        return obj.pros.count()
    pro_count.short_description = 'Pros'
    
    def con_count(self, obj):
        return obj.cons.count()
    con_count.short_description = 'Cons'
    
    def is_selected(self, obj):
        if obj.decision.selected_option == obj:
            return format_html(
                '<span style="color: green;">✓ Selected</span>'
            )
        return format_html(
            '<span style="color: gray;">-</span>'
        )
    is_selected.short_description = 'Status'

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_link', 'created_at')
    list_filter = ('team',)
    search_fields = ('name', 'description', 'team__name')
    
    def team_link(self, obj):
        url = f"/admin/main/team/{obj.team.id}"
        return format_html('<a href="{}">{}</a>', url, obj.team.name)
    team_link.short_description = 'Team'

@admin.register(Principle)
class PrincipleAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_link', 'created_at')
    list_filter = ('team',)
    search_fields = ('name', 'description', 'team__name')
    
    def team_link(self, obj):
        url = f"/admin/main/team/{obj.team.id}"
        return format_html('<a href="{}">{}</a>', url, obj.team.name)
    team_link.short_description = 'Team'
