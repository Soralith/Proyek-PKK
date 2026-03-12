from django import forms
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'attachment', 'due_date', 'max_score', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('file', 'text_answer')
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'text_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 6,
                                                  'placeholder': 'Tulis jawaban Anda di sini...'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('score', 'feedback')
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                               'placeholder': 'Tulis komentar/feedback untuk siswa...'}),
        }
