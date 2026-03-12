from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('course/<slug:course_slug>/', views.assignment_list, name='assignment_list'),
    path('course/<slug:course_slug>/create/', views.assignment_create, name='assignment_create'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submission/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
]
