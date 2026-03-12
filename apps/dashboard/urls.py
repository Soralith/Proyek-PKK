from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('progress/<slug:course_slug>/', views.progress_report, name='progress_report'),
]
