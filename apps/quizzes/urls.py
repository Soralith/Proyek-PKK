from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('course/<slug:course_slug>/', views.quiz_list, name='quiz_list'),
    path('course/<slug:course_slug>/create/', views.quiz_create, name='quiz_create'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<int:pk>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_pk>/take/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_pk>/result/', views.quiz_result, name='quiz_result'),
    path('<int:quiz_pk>/question/create/', views.question_create, name='question_create'),
    path('question/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('question/<int:pk>/delete/', views.question_delete, name='question_delete'),
]
