# ========================
# Libraries and Import Models
# ========================
from django.contrib import admin
from .models import (Student, Component, StudentIssueLog, ComponentCategory, Branches,
                     AvailableProjects,Faculty)


# ========================
# Register Models
# ========================
admin.register(ComponentCategory)
admin.register(Branches)
admin.register(AvailableProjects)
admin.register(Faculty)



# ========================
# - These are special fields which will be used
#   when we use admin panel of django

#  *** NOTE::***
#  - If anything is foreign key aur usko yha likhte to
#     vo print hota JO __STR()__ MEIN LIKHA HOGA

# ========================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("std_roll_number", "std_first_name", "std_last_name")
    search_fields = ("std_roll_number", "std_first_name", "std_last_name")
    list_filter = ("std_year","std_branch")


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("comp_name", "comp_category", "comp_quantity_available")
    search_fields = ("comp_name",)
    list_filter = ("comp_category",)


@admin.register(StudentIssueLog)
class IssueLogAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "component",
        "std_issue_quantity_issued",
        "std_issue_issue_date",
        "std_issue_return_date",
    )
    list_filter = ("std_issue_issue_date", "std_issue_return_date")
    search_fields = ("student__std_roll_number", "component__comp_name")