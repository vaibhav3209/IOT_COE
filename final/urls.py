# --------------- Libraries ---------------------
from django.urls import path
from django.conf import settings

# --------------- Redirecting ---------------------
from django.views.generic import RedirectView


# ---------------- API Usage--------------------
from . import views
from .views import StudentIssueLogAPI


# ------------------------------------
# Note: Same order of urls will be used in
#       `views.py` file for easier tracking
# ------------------------------------

app_name = "final"
urlpatterns = [
    # Empty path is necessary for home page ,but we directly start from login page
    # that's why we used `RedirectView`
    path('', RedirectView.as_view(pattern_name='final:login', permanent=False), name='home'),

    path('login/', views.user_login, name="login"),
    path('student/', views.student_dashboard, name="student_dashboard"),
    path('teacher/logout/', views.admin_logout, name='admin_logout'),
    path('student/logout/', views.student_logout, name='student_logout'),

    path('student/issued_items/', views.issued_items, name="issued_items"),
    path('student/request-components/', views.request_components, name="request_components"),
    path('student/request-components/<path:slug>/', views.category_items,name='category_items'),
    path('student/submit_request/', views.submit_request, name='submit_request'),

    path('teacher/dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('teacher/add-new-project',views.add_new_project,name='add_new_project'),
    path('teacher/add-new-faculty', views.add_new_faculty, name='add_new_faculty'),
    path('teacher/activity', views.activity, name='activity'),
    path('teacher/approved/', views.approved, name="approved"),
    path('teacher/inventory/', views.inventory, name='inventory'),
    path('teacher/inventory/add-component', views.add_component, name='add_component'),
    path('teacher/inventory-items/<path:slug>/', views.inventory_items, name='inventory_items'),
    path('teacher/update-status/', views.update_status, name='update_status'),
    path('teacher/all-students/', views.all_students, name='all_students'),
    path('teacher/all-students/<str:id>', views.student_details, name='student_details'),

    path(f"api/{settings.ADMIN_PATH}",StudentIssueLogAPI.as_view(),name="student-issue-logs"),


# bot calls
path( "teacher/api/pendingissues/",views.pending_issue_requests_api,name="pending_issues_api")
]