# --------------- Libraries ---------------------
from django.urls import path
from django.conf import settings

# ------- Import Simulation.views -------------
from . import views


# ------ All Urls used by BOT and different services ------------
app_name = 'simulation'
urlpatterns = [
    path("teacher/pendingissues/", views.pending_issue_requests,name="pending_issues"),
    path("teacher/to_return/", views.to_return, name="to_return"),
]
