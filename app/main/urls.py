from django.urls import path
from . import views

urlpatterns = [
    # Team management
    path('', views.team_list, name='team_list'),  # Changed default to team list
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<uuid:pk>/', views.team_detail, name='team_detail'),
    path('teams/<uuid:pk>/edit/', views.team_edit, name='team_edit'),
    path('teams/<uuid:pk>/delete/', views.team_delete, name='team_delete'),
    path('teams/<uuid:pk>/leave/', views.team_leave, name='team_leave'),
    path('teams/<uuid:pk>/members/<int:member_pk>/remove/', views.team_remove_member, name='team_remove_member'),
    
    # Team join
    path('teams/join/<uuid:share_id>/', views.team_join_page, name='team_join_page'),
    path('teams/join/<uuid:share_id>/action/', views.team_join_action, name='team_join_action'),
    path('teams/join/<uuid:share_id>/signup/', views.team_join_signup, name='team_join_signup'),
    path('teams/join/<uuid:share_id>/login/', views.team_join_login, name='team_join_login'),
    
    # Goals
    path('teams/<uuid:team_pk>/goals/create/', views.goal_create, name='goal_create'),
    path('teams/<uuid:team_pk>/goals/<uuid:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('teams/<uuid:team_pk>/goals/<uuid:pk>/delete/', views.goal_delete, name='goal_delete'),
    
    # Principles
    path('teams/<uuid:team_pk>/principles/create/', views.principle_create, name='principle_create'),
    path('teams/<uuid:team_pk>/principles/<uuid:pk>/edit/', views.principle_edit, name='principle_edit'),
    path('teams/<uuid:team_pk>/principles/<uuid:pk>/delete/', views.principle_delete, name='principle_delete'),
    
    # Decisions
    path('teams/<uuid:team_pk>/decisions/', views.decision_list, name='decision_list'),
    path('teams/<uuid:team_pk>/decisions/create/', views.decision_create, name='decision_create'),
    path('teams/<uuid:team_pk>/decisions/<uuid:pk>/', views.decision_detail, name='decision_detail'),
    
    # Option management
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/create/', views.option_create, name='option_create'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:pk>/edit/', views.option_edit, name='option_edit'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:pk>/delete/', views.option_delete, name='option_delete'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:pk>/select/', views.option_select, name='option_select'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/clear-selection/', views.clear_selected_option, name='clear_selected_option'),

    # Pros and Cons management
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:option_pk>/pros/create/', views.pro_create, name='pro_create'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:option_pk>/pros/<uuid:pk>/delete/', views.pro_delete, name='pro_delete'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:option_pk>/cons/create/', views.con_create, name='con_create'),
    path('teams/<uuid:team_pk>/decisions/<uuid:decision_pk>/options/<uuid:option_pk>/cons/<uuid:pk>/delete/', views.con_delete, name='con_delete'),
]