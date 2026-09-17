# ------------- Django Core ---------------
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, QueryDict, JsonResponse

# ------------- Local Imports ---------------
''' NOTE: These are only pycharm errors, website works fine. '''
from final.decorators import admin_login_required
from final.models import StudentIssueLog


# ------------- API ---------------
from rest_framework.renderers import JSONRenderer



@admin_login_required
def pending_issue_requests(request):
    """ Used in TeacherSimulation class  """
    requests_qs = (
        StudentIssueLog.objects
        .filter(
            std_issue_issue_date__isnull=True
        )
        .values(
            "id",
            "component__comp_quantity_available",
            "std_issue_quantity_issued",
            "std_issue_form_date",
            "component__comp_name",
            "student__std_roll_number"
        )
    )

    return JsonResponse(list(requests_qs), safe=False)
    # return requests_qs


@admin_login_required
def to_return(request):
    """ Used in TeacherSimulation class """
    to_return  = (
        StudentIssueLog.objects
        .filter(std_issue_return_date__isnull = True)
        .values("id",
            "component__comp_quantity_available",
            "std_issue_quantity_issued",
            "std_issue_form_date",
            "std_issue_issue_date",
            "component__comp_name",
            "student__std_roll_number")
    )

    return JsonResponse(list(to_return), safe=False)