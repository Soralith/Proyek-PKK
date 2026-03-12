from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.courses.models import Course, Enrollment
from .models import Quiz, Question, Answer, QuizAttempt, StudentAnswer
from .forms import QuizForm, QuestionForm, AnswerFormSet


@login_required
def quiz_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.user.is_student:
        get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
        quizzes = course.quizzes.filter(is_published=True)
    else:
        quizzes = course.quizzes.all()

    attempt_map = {}
    if request.user.is_student:
        for attempt in QuizAttempt.objects.filter(student=request.user, quiz__course=course):
            if attempt.quiz_id not in attempt_map:
                attempt_map[attempt.quiz_id] = []
            attempt_map[attempt.quiz_id].append(attempt)

    return render(request, 'quizzes/quiz_list.html', {
        'course': course,
        'quizzes': quizzes,
        'attempt_map': attempt_map,
    })


@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    course = quiz.course
    attempts = []

    if request.user.is_student:
        get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
        attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz)

    questions_with_answers = None
    if not request.user.is_student:
        questions_with_answers = quiz.questions.prefetch_related('answers').all()

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'course': course,
        'attempts': attempts,
        'questions_with_answers': questions_with_answers,
    })


@login_required
def quiz_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=course_slug)

    form = QuizForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        quiz = form.save(commit=False)
        quiz.course = course
        quiz.save()
        messages.success(request, 'Kuis berhasil dibuat! Tambahkan pertanyaan sekarang.')
        return redirect('quizzes:question_create', quiz_pk=quiz.pk)

    return render(request, 'quizzes/quiz_form.html', {'form': form, 'course': course, 'action': 'Buat'})


@login_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if not (request.user == quiz.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = QuizForm(request.POST or None, instance=quiz)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Kuis berhasil diperbarui!')
        return redirect('quizzes:quiz_detail', pk=pk)

    return render(request, 'quizzes/quiz_form.html', {
        'form': form, 'course': quiz.course, 'quiz': quiz, 'action': 'Edit'
    })


@login_required
def question_create(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    if not (request.user == quiz.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = QuestionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.order = quiz.questions.count() + 1
        question.save()

        # Save answers for multiple choice / true-false
        if question.question_type in ('multiple_choice', 'true_false'):
            answer_texts = request.POST.getlist('answer_text')
            correct_index = request.POST.get('correct_answer', '0')
            for i, text in enumerate(answer_texts):
                if text.strip():
                    Answer.objects.create(
                        question=question,
                        text=text.strip(),
                        is_correct=(str(i) == correct_index),
                        order=i
                    )

        messages.success(request, 'Pertanyaan berhasil ditambahkan!')
        if 'add_more' in request.POST:
            return redirect('quizzes:question_create', quiz_pk=quiz_pk)
        return redirect('quizzes:quiz_detail', pk=quiz_pk)

    return render(request, 'quizzes/question_form.html', {
        'form': form, 'quiz': quiz, 'action': 'Tambah'
    })


@login_required
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    quiz = question.quiz
    if not (request.user == quiz.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = QuestionForm(request.POST or None, instance=question)
    if request.method == 'POST' and form.is_valid():
        form.save()

        # Update jawaban jika tipe pilihan ganda / benar-salah
        if question.question_type in ('multiple_choice', 'true_false'):
            answer_texts = request.POST.getlist('answer_text')
            correct_index = request.POST.get('correct_answer', '0')

            # Hapus jawaban lama, buat ulang
            question.answers.all().delete()
            for i, text in enumerate(answer_texts):
                if text.strip():
                    Answer.objects.create(
                        question=question,
                        text=text.strip(),
                        is_correct=(str(i) == correct_index),
                        order=i
                    )

        messages.success(request, 'Soal berhasil diperbarui!')
        return redirect('quizzes:quiz_detail', pk=quiz.pk)

    # Kirim jawaban existing ke template
    existing_answers = list(question.answers.order_by('order').values('text', 'is_correct'))
    correct_index = next((str(i) for i, a in enumerate(existing_answers) if a['is_correct']), '0')

    return render(request, 'quizzes/question_edit.html', {
        'form': form,
        'quiz': quiz,
        'question': question,
        'existing_answers': existing_answers,
        'correct_index': correct_index,
    })


@login_required
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    quiz = question.quiz
    if not (request.user == quiz.course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        quiz_pk = quiz.pk
        question.delete()
        # Reorder soal yang tersisa
        for i, q in enumerate(quiz.questions.order_by('order'), start=1):
            q.order = i
            q.save()
        messages.success(request, 'Soal berhasil dihapus.')
        return redirect('quizzes:quiz_detail', pk=quiz_pk)

    return render(request, 'quizzes/question_confirm_delete.html', {
        'question': question, 'quiz': quiz
    })


@login_required
def start_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    course = quiz.course
    get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)

    # Check attempt limit
    attempt_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz, status='completed').count()
    if quiz.max_attempts > 0 and attempt_count >= quiz.max_attempts:
        messages.error(request, f'Anda sudah mencapai batas maksimal percobaan ({quiz.max_attempts}x).')
        return redirect('quizzes:quiz_detail', pk=pk)

    # Create new attempt
    attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)
    return redirect('quizzes:take_quiz', attempt_pk=attempt.pk)


@login_required
def take_quiz(request, attempt_pk):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk, student=request.user, status='in_progress')
    quiz = attempt.quiz

    questions = list(quiz.questions.prefetch_related('answers').all())
    if quiz.shuffle_questions:
        import random
        random.shuffle(questions)

    if request.method == 'POST':
        total_points = 0
        earned_points = 0

        for question in quiz.questions.all():
            total_points += question.points
            answer_id = request.POST.get(f'question_{question.pk}')
            text_ans = request.POST.get(f'text_{question.pk}', '')

            student_answer = StudentAnswer(attempt=attempt, question=question)

            if question.question_type in ('multiple_choice', 'true_false') and answer_id:
                try:
                    selected = Answer.objects.get(pk=answer_id, question=question)
                    student_answer.selected_answer = selected
                    student_answer.is_correct = selected.is_correct
                    if selected.is_correct:
                        student_answer.points_earned = question.points
                        earned_points += question.points
                except Answer.DoesNotExist:
                    pass
            elif question.question_type in ('short_answer', 'essay'):
                student_answer.text_answer = text_ans

            student_answer.save()

        # Calculate score
        if total_points > 0:
            percentage = (earned_points / total_points) * 100
        else:
            percentage = 0

        attempt.score = earned_points
        attempt.percentage = round(percentage, 2)
        attempt.status = 'completed'
        attempt.completed_at = timezone.now()
        attempt.save()

        messages.success(request, 'Kuis berhasil dikumpulkan!')
        return redirect('quizzes:quiz_result', attempt_pk=attempt.pk)

    return render(request, 'quizzes/take_quiz.html', {
        'attempt': attempt,
        'quiz': quiz,
        'questions': questions,
    })


@login_required
def quiz_result(request, attempt_pk):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_pk)
    if request.user.is_student and attempt.student != request.user:
        messages.error(request, 'Akses ditolak.')
        return redirect('dashboard:index')

    student_answers = attempt.student_answers.select_related(
        'question', 'selected_answer'
    ).prefetch_related('question__answers').all()

    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'student_answers': student_answers,
        'course': attempt.quiz.course,
    })
