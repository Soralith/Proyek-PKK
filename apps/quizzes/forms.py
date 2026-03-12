from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title', 'description', 'time_limit', 'passing_score',
                  'max_attempts', 'shuffle_questions', 'show_results', 'is_published',
                  'start_date', 'end_date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control'}),
            'shuffle_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_results': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text', 'question_type', 'points', 'explanation')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'question_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_question_type'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


AnswerFormSet = inlineformset_factory(
    Question, Answer,
    fields=('text', 'is_correct', 'order'),
    extra=4,
    can_delete=True,
    widgets={
        'text': forms.TextInput(attrs={'class': 'form-control'}),
        'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'}),
    }
)
