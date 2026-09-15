from functools import wraps
from django.shortcuts import redirect
from .models import Student

def student_login_required(view_func):
    ''' Used to check whether a student is logged in or not to prevent unauthorised logins.'''

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        student_id = request.session.get('student_id')
        if not student_id:
            return redirect('final:login')

        try:
            request.student = Student.objects.get(std_id=student_id)
        except Student.DoesNotExist:
            return redirect('final:login')

        return view_func(request, *args, **kwargs)
    return wrapper

def admin_login_required(view_func):
    ''' Used to check whether admin is logged in or not to prevent unauthorised logins.'''

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("final:login")
        return view_func(request, *args, **kwargs)
    return wrapper
