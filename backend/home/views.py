from django.shortcuts import render
from students.models import Student


def home(request):
    """Home page view"""
    # Get some statistics for the home page
    total_students = Student.objects.count()
    recent_students = Student.objects.order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'recent_students': recent_students,
    }
    return render(request, 'home/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'home/about.html')


def contact(request):
    """Contact page view"""
    return render(request, 'home/contact.html')