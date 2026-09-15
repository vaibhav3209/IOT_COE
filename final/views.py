# ------------- Standard Library ---------------
from datetime import datetime, timedelta, date
from collections import defaultdict


# ------------- Django Core ---------------
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, QueryDict, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.cache import cache


# ------------- Django Authentication & Messages ---------------
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages


# ------------- Third-Party Libraries ---------------


# ------------- Local Imports ---------------
from .decorators import student_login_required, admin_login_required
from .models import (Student, StudentIssueLog, ComponentCategory,
                     Component, Branches,AvailableProjects,Faculty
                     )


# ------------- API ---------------
from .serializers import StudentIssueLogSerializer
from rest_framework import generics, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination


# ------------- Global Cache ---------------
def get_all_available_projects():
    """
        - Below Print statements are used to see the effect of cache hit on Database or not.
        - Usage in following functions:
            1. request_components()
            2. category_items()
            3. add_new_project() { to show after/ before deletion}
        - Delete and refresh instances from:
            1. add_new_project() { refresh after deletion }

        NOTE: We are setting `objects` directly to cache not names, ids etc.
    """


    cache_key = "cached_all_available_projects"
    all_projects = cache.get(cache_key)

    if all_projects is None:
        all_projects = list(
            AvailableProjects.objects.select_related(
                'avail_proj_faculty_associated'
            )
        )
        cache.set(cache_key, all_projects, timeout=None)
        # print("All available projects cached -> 1 DB hit")

    # print("Retrieved all available projects from cache -> no DB hit")
    return all_projects



def get_all_branches():
    """
        - Usage in following functions:
            1. add_new_faculty()
         - Delete and refresh instances from:
            1.
    """
    cache_key = "cached_all_branches"
    branches = cache.get(cache_key)

    if branches is None:
        branches = list(Branches.objects.all())
        cache.set(cache_key, branches, None)

    return branches



def get_all_categories():
    """
        - Usage in following functions:
            1. inventory()
            2. inventory_items()
        - Delete and refresh instances from:
            1.
    """
    cache_key = "cached_all_categories"
    categories = cache.get(cache_key)

    if categories is None:
        categories = list(ComponentCategory.objects.all())
        cache.set(cache_key,categories,None)

    return categories



def get_all_faculty():
    """
        - Usage in following functions:
            1. add_new_project()
            2. add_new_faculty {after deletion to set again}

        - Delete and refresh instances from:
            1. add_new_faculty()
    """
    cache_key = "cached_all_faculty"
    faculty = cache.get(cache_key)

    if faculty is None:
        faculty = list(Faculty.objects.select_related("faculty_dept"))
        cache.set(cache_key, faculty, None)

    return faculty



# ----------- CACHE for SIMULATION ------------------
def bot_usernames():
    """
        - Usage:
            1. simulation->Services.py->class Student
        - Deletion:
            1. When a new student Register
    """
    cache_key = 'bot_usernames'
    bot_usernames = cache.get(cache_key)

    if bot_usernames is None:
        bot_usernames = list(Student.objects
                             .filter(std_deactivated_at__isnull = True)
                             .values('std_roll_number')
                             )
    return bot_usernames



def component_in_category_x(category_obj):
    """
        - Used in simulation->services.py->submit_request()
        - Delete when:
            1. add_component()
    """
    cache_key = f"components_in_{category_obj.comp_cate_category_name}"
    components = cache.get(cache_key)

    if components is None:

        components = list(Component
                          .objects
                          .filter(comp_category_id=category_obj.id,
                                  comp_status=True)
                          .values_list("id",flat = True)
                          )
        cache.set(cache_key,components,None)

    return components



#=======================================================================
# Caching for DATA GENERATION BOT  `
#======================================================================
def students_per_project(data_dict):
    cache_key = 'students_per_project'
    data = cache.get(cache_key)

    if data is None:
        data = data_dict
        cache.set(cache_key,data,timeout=None)

    # return a dictionary of projectid as key and list of students
    return data



# ------------- Main functions ---------------
def user_login(request):
    # ====== LOGIN  ======
    if request.method == 'POST'and request.POST.get("form_type") == "user_login":
            username = request.POST.get('username')
            password = request.POST.get('password')

            if username.endswith("admin"):
                admin_user = authenticate(request,username=username,password=password)

                if admin_user and admin_user.is_staff:
                    login(request, admin_user)
                    return redirect('final:admin_dashboard')
            try:
                student = Student.objects.get(std_roll_number=username.upper())

            except Student.DoesNotExist:
                # ......... Message Tags ............
                # 1. Used to display message on respective pages
                # 2. Easier to debug
                messages.error(request, "Invalid email or password",extra_tags='login_error')
                return render(request, 'final/login.html')

            if check_password(password, student.std_password):
                request.session['student_id'] = student.std_id          # custom session
                request.session["student_name"] = student.std_full_name
                return redirect('final:student_dashboard')

            messages.error(request, "Invalid email or password.",extra_tags='login_error')

    # ====== Signup  ======
    if request.method == 'POST' and request.POST.get("form_type") == "user_signup":
        first_name = request.POST.get("first_name").strip().lower()
        last_name = request.POST.get("last_name").strip().lower()
        roll_number = request.POST.get("roll_number").upper()
        email = request.POST.get("college_email")[:7].lower()
        password = request.POST.get("password")
        phone_number=request.POST.get("phone_number")

        branch = roll_number[5:7]
        std_year = request.POST.get("std_year")

        # ......... Validation ...........
        # - Based on only these 2 fields as They are only defining Primary keys
        if Student.objects.filter(std_roll_number=roll_number).exists():
            messages.error(request, "Roll number already exists",extra_tags='login_error')
            return render(request, "final/login.html")

        if Student.objects.filter(std_college_email=email).exists():
            messages.error(request, "Email already registered",extra_tags='login_error')
            return render(request, "final/login.html")

        std_branch = get_object_or_404(Branches,branches_rollno_code=branch)

        try:
            Student.objects.create(
                std_first_name=first_name,
                std_last_name=last_name,
                std_roll_number=roll_number,
                std_college_email=email,
                std_password=make_password(password),
                std_phone_number=phone_number,
                std_branch=std_branch,
                std_year = std_year
            )

        except ValidationError as e:
            messages.error(request, "Cannot create user. Validation Checks Failed.", extra_tags='signup_error')
            return render(request, "final/login.html")

        except IntegrityError:
            messages.error(request, "data violates constraints.",extra_tags='signup_error')
            return render(request, "final/login.html")


        messages.success(request, "Registration successful. Please login.",extra_tags='login_success')
        return redirect("final:login")

    # ==== load initial login page ====
    return render(request, 'final/login.html')



@student_login_required
def student_dashboard(request):
    student = request.student

    return render(request,"final/student/student_dashboard.html",
                  {"student": student})



@require_POST
def student_logout(request):
    ''' Decorator `student_login_required` not used here as in broken session or unlogged user can also access this. '''
    request.session.flush()
    return redirect('final:login')



@require_POST
def admin_logout(request):
    ''' This is Django based logout '''
    logout(request)
    return redirect("final:login")



@student_login_required
def issued_items(request):
    if not request.GET:
        # ------- No DB hit. ----------
        return render(request,"final/student/issued_items.html")

    # print("db hit happens")
    student_id = request.session.get('student_id')
    issue_status = request.GET.get("issue_status")  # current / returned / None
    date_range = request.GET.get("date_range")  # 7d / 1m / 3m / all
    selected_categories = request.GET.getlist("category")



    qs = (
        StudentIssueLog.objects
        .filter(student_id=student_id)
        .select_related("component", "project")
    )


    if issue_status == "current":
        qs = qs.filter(std_issue_return_date__isnull=True)

    elif issue_status == "returned":
        qs = qs.filter(std_issue_return_date__isnull=False)


    if selected_categories:
        qs = qs.filter(
            component__comp_category__comp_cate_category_name__in=selected_categories
        )


    today = now().date()

    if date_range == "7":
        qs = qs.filter(std_issue_issue_date__gte=today - timedelta(days=7))

    elif date_range == "15":
        qs = qs.filter(std_issue_issue_date__gte=today - timedelta(days=15))

    elif date_range == "30":
        qs = qs.filter(std_issue_issue_date__gte=today - timedelta(days=30))


    elif date_range == "90":
        qs = qs.filter(std_issue_issue_date__gte=today - timedelta(days=90))

    # "all" → no filter applied (intentionally)

    return render(
        request,
        "final/student/issued_items.html",
        {
            "issued_items": qs,
            "issue_status": issue_status,
            "date_range": date_range,
            "selected_categories": selected_categories,
        }
    )



@student_login_required
def request_components(request):
    '''  Getting all projects from cache as it is needed in request sidebar  '''
    all_projects = get_all_available_projects()
    return render(request,
                  'final/student/request_components.html',
                  {'all_projects':all_projects})



@student_login_required
def category_items(request ,slug):
    category = get_object_or_404(
        ComponentCategory,
        comp_cate_category_name=slug
    )

    components = (
                Component.objects
                  .select_related('comp_category')
                  .filter(comp_category=category)
                  .order_by("-comp_name")
                  )

    all_projects = get_all_available_projects()

    # 1. Second argument is the number of items per page
    # 2. This is lazy query only till here!
    paginator = Paginator(components, 15)
    page_number = request.GET.get("page", 1)

    # ........ Here, it hits the DATABASE ...........
    page_obj = paginator.get_page(page_number)

    return render(request, 'final/student/category_items.html', {
        'category_name': category.comp_cate_category_name,
        "all_projects": all_projects,
        "page_obj":page_obj
    })



@student_login_required
def submit_request(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    component_ids = request.POST.getlist('component_ids[]')
    quantities = request.POST.getlist('quantities[]')
    project_id= request.POST.get("project_id")
    # print(request.POST)

    # .... Get the project object (direct id is not inserted) ....
    project = get_object_or_404(AvailableProjects,id=project_id)
    # print(component_ids,quantities)
    # print(project)

    if not component_ids or not quantities:
        messages.error(request, "No components selected",extra_tags='error_requestcomp')
        return redirect('final:request_components')

    if len(component_ids) != len(quantities):
        return HttpResponseBadRequest("Mismatched data")


    student = request.student
    # print(type(student))
    # print(student.std_full_name,student.std_roll_number)

    # ---- FETCH ALL COMPONENTS IN ONE QUERY (FAST) ----
    components_map = Component.objects.in_bulk(component_ids)

    issue_logs = []

    for comp_id, qty in zip(component_ids, quantities):
        component = components_map.get(int(comp_id))
        if not component:
            continue

        try:
            qty = int(qty)
            if qty <= 0:
                continue
        except ValueError:
            continue

        issue_logs.append(
            StudentIssueLog(
                student=student,
                component=component,
                project=project,
                std_issue_quantity_issued=qty,
                std_issue_form_date=datetime.now().date()
            )
        )

    if not issue_logs:
        messages.error(request, "Invalid component selection",extra_tags='error_requestcomp')
        return redirect('final:request_components')

    # ---- ATOMIC SAVE (SAFE) ----
    with transaction.atomic():
        StudentIssueLog.objects.bulk_create(issue_logs)

    messages.success(request, "Request submitted successfully",extra_tags='success_requestcomp')

    response = redirect('final:request_components')
    response.set_cookie('clearLocalStorage', 'true')  # frontend signal
    return response



@admin_login_required
def admin_dashboard(request):
    """ Load requests that have return date == NULL """
    requests_qs = (
        StudentIssueLog.objects
        .filter(std_issue_issue_date__isnull=True,
                std_issue_return_date__isnull=True)
        .values(
             'student__std_roll_number',
            'component__comp_name',
            'component__comp_category__comp_cate_category_name',
            'std_issue_form_date',
            'component__comp_quantity_available',
            'std_issue_quantity_issued'
        )
        .order_by('component__comp_category__comp_cate_category_name', '-std_issue_form_date')
    )

    grouped_requests = defaultdict(list)
    for r in requests_qs:
        grouped_requests[r['component__comp_category__comp_cate_category_name']].append(r)
    # print(grouped_requests)

    # ........ NOTE ...........
    # defaultdict is not loaded in html, so convert it in dictionary ONLY
    return render(
        request,
        'final/teacher/admin_dashboard.html',
        {'grouped_requests': dict(grouped_requests)}
    )



@admin_login_required
def add_new_project(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ...... EDIT EXISTING PROJECT .........
        if action == "edit":
            project_id = request.POST.get("project_id")

            project = get_object_or_404(AvailableProjects, id=project_id)
            project.avail_proj_project_name = request.POST.get("project_name")
            project.avail_proj_faculty_associated_id = request.POST.get("faculty")
            project.save()

        #  ........ ADD NEW PROJECT ...............
        else:
            AvailableProjects.objects.create(
                avail_proj_project_name=request.POST.get("project_name"),
                avail_proj_faculty_associated_id=request.POST.get("faculty"),
            )

        # ...... Invalidate Cache ............
        cache.delete("cached_all_available_projects")
        return redirect("final:add_new_project")

    # .......... From CACHE .............
    projects = get_all_available_projects()
    faculties = get_all_faculty()

    return render(
        request,
        "final/teacher/add_new_project.html",
        {"projects": projects,
         "faculties":faculties}
    )



@admin_login_required
def add_new_faculty(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "edit":
            faculty_id = request.POST.get("faculty_id")
            faculty_name = request.POST.get("faculty_name")
            branch_id = request.POST.get("branch")

            Faculty.objects.filter(id=faculty_id).update(
                faculty_name=faculty_name,
                faculty_dept_id=branch_id
            )

        else:
            faculty_name = request.POST.get("faculty_name")
            branch_id = request.POST.get("branch")

            Faculty.objects.create(
                faculty_name=faculty_name,
                faculty_dept_id=branch_id
            )

        # ..... Invalidate Cache ................
        cache.delete("cached_all_faculty")
        return redirect("final:add_new_faculty")


    faculties = get_all_faculty()
    branches = get_all_branches()
    return  render(request,"final/teacher/add_new_faculty.html",
                   {"faculties":faculties,
                    "branches":branches})



@admin_login_required
def activity(request):
    quick_range = request.GET.get("quick_range", "today")

    # .... Optional ......
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    issues = StudentIssueLog.objects.select_related(
        "component", "student", "project"
    ).order_by("-std_issue_issue_date")


    # -------- DATE FILTER --------
    today = date.today()

    if from_date and to_date:
        start_dt = date.fromisoformat(from_date)
        end_dt = date.fromisoformat(to_date)

        issues = issues.filter(
            std_issue_form_date__range=(start_dt, end_dt)
        )

    else:
        if quick_range == "today":
            issues = issues.filter(
                std_issue_issue_date=today
            )

        elif quick_range == "3":
            issues = issues.filter(
                std_issue_issue_date__gte=today - timedelta(days=3)
            )

        elif quick_range == "7":
            issues = issues.filter(
                std_issue_issue_date__gte=today - timedelta(days=7)
            )


    context = {
        "issues":issues,
        "days": quick_range,
        "from_date": from_date,
        "to_date": to_date,
    }
    return render(request,'final/teacher/activity.html',context)



@admin_login_required
def approved(request):
    ''' Records whose return_date == NULL are filtered here '''
    requests_approved = (StudentIssueLog.objects
                         .select_related("student", "component",
                                        "component__comp_category")
                         .filter(std_issue_issue_date__isnull=False,
                                 std_issue_return_date__isnull=True)
                         .values(
         'student__std_roll_number', 'std_issue_issue_date', 'component__comp_name',
        'component__comp_category__comp_cate_category_name', 'component__comp_quantity_available',
        'std_issue_quantity_issued').order_by('component__comp_category__comp_cate_category_name', '-std_issue_form_date'))

    grouped_requests = defaultdict(list)

    for req in requests_approved:
        grouped_requests[req['component__comp_category__comp_cate_category_name']].append(req)

    return render(request, 'final/teacher/approved.html', {
        'grouped_requests': dict(grouped_requests)})



@admin_login_required
def inventory(request):
    ''' Categories are taken from cache for add_component button'''
    categories = get_all_categories()
    return render(request,"final/teacher/inventory.html",{"categories":categories})



@require_POST
@admin_login_required
def add_component(request):
    new_component = request.POST.get("component_name","").strip()
    new_category = request.POST.get("component_category")

    try:
        new_quantity = int(request.POST.get("component_qty"))
    except (TypeError, ValueError):
        messages.error(request, "Invalid quantity")
        return redirect("final:inventory")


    # ..... DUPLICATE CHECK .......
    if Component.objects.filter(
        comp_name__iexact=new_component,
        comp_category=new_category
    ).exists():
        messages.warning(
            request,
            f"Component '{new_component}' already exists ."
        )
        return redirect("final:inventory")

    try:
        category = ComponentCategory.objects.get(comp_cate_category_name=new_category)
    except ComponentCategory.DoesNotExist:
        messages.error(request, "Category not found")
        return redirect("final:inventory")


    try:
        Component.objects.create(
            comp_name=new_component,
            comp_qunatity_available=new_quantity,
            comp_category=category
        )
        messages.success(
            request,
            f"Component '{new_component}' added in category {category}."
        )
    except Exception:
        messages.error(request, f"Failed to add component {new_component}")

    # -------- Invalidate Cache ------------------
    cache.delete(f"components_in_{category.comp_cate_category_name}")

    return  redirect('final:inventory')



@admin_login_required
def inventory_items(request, slug):
    category = get_object_or_404(
        ComponentCategory,
        comp_cate_category_name=slug
    )
    components = Component.objects.select_related('comp_category').filter(
        comp_category=category
    )

    # .... This will be used in edit Row ......
    categories = ComponentCategory.objects.all()

    if request.method == 'POST':
        component_id = request.POST.get("component_id")
        action = request.POST.get("action")
        change_category = get_object_or_404(ComponentCategory,id=request.POST.get("category_id"))
        component = get_object_or_404(Component, id=component_id)

        if action == "save":
            component.comp_name = request.POST.get("comp_name")
            component.comp_quantity_available =  request.POST.get("comp_quantity")
            component.comp_category = change_category
            component.save()

        elif action=="delete":
            # Soft delete 0 == deleted  1== working
            component.comp_status = 0
            component.save(update_fields=['comp_status'])

            messages.success(request, f"{component.comp_name} marked as deleted.")


    return render(request, 'final/teacher/inventory_items.html', {
        'components': components,
        'categories':categories,
        'category_name': category.comp_cate_category_name,
    })



@require_POST
@admin_login_required
def update_status(request):
    roll_number = request.POST.get("roll_number")
    form_date = request.POST.get("form_date")
    issue_date = request.POST.get("issue_date")
    component_name = request.POST.get("component_name")
    status_to_update = request.POST.get("status_to_update")
    # print("data is:", form_date, action, component_name, roll_number)


    if status_to_update in ("approve","reject"):
        logs = StudentIssueLog.objects.select_related("component", "student").filter(
            student__std_roll_number=roll_number,
            component__comp_name=component_name,
            std_issue_form_date=form_date
        )


    elif status_to_update == "return":
        logs = StudentIssueLog.objects.select_related("component", "student").filter(
            student__std_roll_number=roll_number,
            component__comp_name=component_name,
            std_issue_issue_date = issue_date,
            std_issue_return_date__isnull=True
        )

    else: return HttpResponse("Invalid action", status=400)

    if not logs.exists():
        return HttpResponse("Log not found", status=404)

    with transaction.atomic():
        if status_to_update == "reject":
            # Delete all matching logs
            deleted_count, _ = logs.delete()

            if deleted_count > 0:
                messages.success(request, "Log deleted successfully.")
            else:
                messages.error(request, "No matching log found.")

        else:
            for log in logs:
                component = Component.objects.select_for_update().get(
                    id=log.component_id
                )

                if status_to_update == "approve":
                    if component.comp_quantity_available < log.std_issue_quantity_issued:
                        return HttpResponse(
                            f"Not enough quantity available for {component.name}",
                            status=400
                        )

                    # Update log
                    log.std_issue_issue_date = now().date()

                    # Deduct stock
                    component.comp_quantity_available -= log.std_issue_quantity_issued


                    component.save()
                    log.save()

                elif status_to_update == "return":
                    log.std_issue_return_date = now().date()

                    component.comp_quantity_available += log.std_issue_quantity_issued
                    component.save()

                    log.save()
                    return redirect('final:approved')

    return redirect('final:admin_dashboard')



@admin_login_required
def all_students(request):
    """ Taking multiple items from filter that's why using getlist. """
    selected_branches = request.GET.getlist("branch")
    selected_years = request.GET.getlist("year")
    selected_active = request.GET.getlist("active")

    name_query = request.GET.get("name", "").strip().lower()
    name_mode = request.GET.get("name_mode", "startswith")

    # ...... NOTE: This doesn't hit DB directly, lazy evaluation ...............
    students = Student.objects.all()

    # ....... FILTERS ................
    students = students.filter(
        std_branch__branches_branch_code__in=selected_branches,
        std_year__in=selected_years
    )

    if set(selected_active) == {"1"}:
        students = students.filter(std_deactivated_at__isnull=True)
    elif set(selected_active) == {"0"}:
        students = students.filter(std_deactivated_at__isnull=False)

    if name_query:
        if name_mode == "startswith":
            students = students.filter(std_full_name__istartswith=name_query)
        else:
            students = students.filter(std_full_name__icontains=name_query)


    # ...... DB hit here ......................
    paginator = Paginator(students,15)  # 15 students per page
    page_number = request.GET.get("page",1)
    page_obj = paginator.get_page(page_number)

    #  BUILD FILTER-SAFE QUERY STRING (NO PAGE)
    querydict = request.GET.copy()
    querydict.pop("page", None)


    return render(request, "final/teacher/all_students.html", {
        "page_obj": page_obj,
        "branches_list":get_all_branches(),
    "selected_branches": selected_branches,
    "selected_years": selected_years,
    "selected_active": selected_active,
    "name_query": name_query,
    "name_mode": name_mode,
        "querystring": querydict.urlencode(),
    'remove_filter':remove_filter       # ..... Written below .......
    })



@admin_login_required
def student_details(request,id):
    student = get_object_or_404(
        Student,
        std_id=id
    )

    issued_components = (
        StudentIssueLog.objects
        .select_related("component",'student')
        .filter(student_id=student.std_id)
        .order_by("-std_issue_issue_date")
    )

    return render(request, "final/teacher/student_details.html", {
        "student": student,
        "issued_components": issued_components
    })



@admin_login_required
def remove_filter(request, key, value=None):
    q = request.GET.copy()
    if value:
        values = q.getlist(key)
        values.remove(value)
        q.setlist(key, values)
    else:
        q.pop(key, None)
    q.pop("page", None)
    return q.urlencode()



# ------------------------------------
# --------       API     -------------
class AdminIssuePagination(PageNumberPagination):
    page_size = 100          # Items per page
    page_size_query_param = None  # Not allow client to set page size
    max_page_size = 100     # Maximum allowed for safety


class StudentIssueLogAPI(generics.ListAPIView):
    queryset = StudentIssueLog.objects.select_related("student", "project","component").all()

    serializer_class = StudentIssueLogSerializer
    permission_classes = [permissions.IsAdminUser]          # Only admins
    pagination_class = AdminIssuePagination
    renderer_classes = [JSONRenderer]                       # Force JSON only

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request

        # ------------------- Basic filters -------------------
        category = request.GET.get("category")
        if category:
            qs = qs.filter(component__comp_category__comp_cate_category_name__icontains=category)

        branch = request.GET.get("branch")
        if branch:
            qs = qs.filter(student__std_branch__branches_branch_code__icontains=branch)

        year = request.GET.get("year")
        if year:
            qs = qs.filter(student__std_year=year)


        # ------------------- Date filters -------------------
        form_date_from = request.GET.get("form_date_from")
        form_date_to = request.GET.get("form_date_to")
        if form_date_from:
            qs = qs.filter(std_issue_issue_date__gte=form_date_from)
        if form_date_to:
            qs = qs.filter(std_issue_issue_date__lte=form_date_to)

        # Issue date range
        issue_date_from = request.GET.get("issue_date_from")
        issue_date_to = request.GET.get("issue_date_to")
        if issue_date_from:
            qs = qs.filter(std_issue_issue_date__gte=issue_date_from)
        if issue_date_to:
            qs = qs.filter(std_issue_issue_date__lte=issue_date_to)

        # Return date range
        return_date_from = request.GET.get("return_date_from")
        return_date_to = request.GET.get("return_date_to")
        if return_date_from:
            qs = qs.filter(std_issue_return_date__gte=return_date_from)
        if return_date_to:
            qs = qs.filter(std_issue_return_date__lte=return_date_to)

        # ------------------- Ordering -------------------
        ordering = request.GET.get("ordering", "-std_issue_form_date")
        qs = qs.order_by(ordering)

        return qs