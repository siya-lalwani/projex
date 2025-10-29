from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('add/', views.add_project, name='add_project'),
    path('overview/<int:project_id>/', views.project_overview, name='project_overview'),
]
