from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from apps.accounts.models import User
from apps.courses.models import Course, Enrollment
from apps.assignments.models import Assignment, Submission
from apps.quizzes.models import Quiz, QuizAttempt


@login_required
def index(request):
    user = request.user

    if user.is_admin:
        return admin_dashboard(request)
    elif user.is_teacher:
        return teacher_dashboard(request)
    else:
        return student_dashboard(request)


def admin_dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': Course.objects.count(),
        'active_courses': Course.objects.filter(status='active').count(),
        'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'pending_submissions': Submission.objects.filter(status='submitted').count(),
    }
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_courses = Course.objects.order_by('-created_at')[:5]

    return render(request, 'dashboard/admin_dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
    })


def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user)
    stats = {
        'total_courses': courses.count(),
        'active_courses': courses.filter(status='active').count(),
        'total_students': Enrollment.objects.filter(
            course__teacher=request.user, is_active=True
        ).values('student').distinct().count(),
        'pending_grades': Submission.objects.filter(
            assignment__course__teacher=request.user,
            status='submitted'
        ).count(),
    }

    recent_submissions = Submission.objects.filter(
        assignment__course__teacher=request.user,
        status='submitted'
    ).select_related('student', 'assignment').order_by('-submitted_at')[:5]

    return render(request, 'dashboard/teacher_dashboard.html', {
        'courses': courses[:6],
        'stats': stats,
        'recent_submissions': recent_submissions,
    })


def student_dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related('course').order_by('-enrolled_at')

    upcoming_assignments = Assignment.objects.filter(
        course__enrollments__student=request.user,
        course__enrollments__is_active=True,
        is_published=True
    ).exclude(
        submissions__student=request.user
    ).order_by('due_date')[:5]

    recent_scores = Submission.objects.filter(
        student=request.user,
        status='graded'
    ).select_related('assignment').order_by('-graded_at')[:5]

    stats = {
        'enrolled_courses': enrollments.count(),
        'completed_courses': enrollments.filter(progress=100).count(),
        'pending_assignments': upcoming_assignments.count(),
        'avg_score': recent_scores.aggregate(avg=Avg('score'))['avg'] or 0,
    }

    return render(request, 'dashboard/student_dashboard.html', {
        'enrollments': enrollments[:6],
        'upcoming_assignments': upcoming_assignments,
        'recent_scores': recent_scores,
        'stats': stats,
    })


@login_required
def progress_report(request, course_slug):
    from apps.courses.models import Course, MaterialProgress, Material
    from django.shortcuts import get_object_or_404

    course = get_object_or_404(Course, slug=course_slug)

    if request.user.is_student:
        enrollment = Enrollment.objects.filter(
            student=request.user, course=course, is_active=True
        ).first()
        if not enrollment:
            from django.contrib import messages
            messages.error(request, 'Anda tidak terdaftar di kelas ini.')
            return redirect('dashboard:index')

        materials = Material.objects.filter(module__course=course, is_published=True)
        completed = MaterialProgress.objects.filter(
            student=request.user,
            material__module__course=course,
            is_completed=True
        ).values_list('material_id', flat=True)

        quiz_attempts = QuizAttempt.objects.filter(
            student=request.user,
            quiz__course=course,
            status='completed'
        )

        submissions = Submission.objects.filter(
            student=request.user,
            assignment__course=course
        )

        return render(request, 'dashboard/student_progress.html', {
            'course': course,
            'enrollment': enrollment,
            'materials': materials,
            'completed_materials': list(completed),
            'quiz_attempts': quiz_attempts,
            'submissions': submissions,
        })

    # Teacher / admin view - all students progress
    enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related('student')
    return render(request, 'dashboard/course_progress.html', {
        'course': course,
        'enrollments': enrollments,
    })
