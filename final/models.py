# --------- Libraries -----------

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator

# ----- For complex queries in django ORM --------
from django.db.models import Q


# ---------- Validators ----------
name_validator = RegexValidator(
    regex=r'^[A-Za-z]{2,30}$',
    message="Only letters allowed (2–30 characters)"
)

roll_validator = RegexValidator(
    regex=r'^[2-9][0-9][eE][sS][kK][a-zA-Z]{2}[0-9]{3}$',
    message="Roll number must be exactly 10 digits"
)

phone_validator = RegexValidator(
    regex=r'^[6-9][0-9]{9}$',
    message="Enter a valid Indian mobile number"
)

college_email_validator = RegexValidator(
    regex=r'^[b][2-9][0-9]{5}',         #not storing @skit.ac.in
    message="Use your official college email"
)
# ------------------------------------------------------------


class ComponentCategory(models.Model):
    comp_cate_category_name = models.CharField(max_length=30,unique=True,null=False)

    def __str__(self):
        return f"{self.comp_cate_category_name}"



class Branches(models.Model):
    # ========================
    #     1. No need to add `db_index = True` in fields where `unique = True`
    # ========================

    branches_branch_name =models.CharField(max_length=30,unique=True,null=False)
    branches_branch_code =models.CharField(max_length=3,unique=True,null=False)
    branches_rollno_code = models.CharField(max_length=3,unique=True,null=False)

    def __str__(self):
        return f"{self.branches_branch_code}"



class Faculty(models.Model):
    # ========================
    # 1. `faculty_dept` will set to NULL when we delete any Branch.
    # ========================

    faculty_name = models.CharField(max_length=100,null=False)

    faculty_dept = models.ForeignKey(
        Branches,
        null=True,
        on_delete=models.SET_NULL,
        related_name='faculties_inthis_dept')



class Component(models.Model):
    comp_name = models.CharField(max_length=100,null=False)
    comp_quantity_available = models.PositiveIntegerField(default=0,null=False)
    comp_category = models.ForeignKey(
        ComponentCategory,
        on_delete=models.PROTECT,
        related_name="components_inthis_category")

    comp_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.comp_name}"



class Student(models.Model):
    YEAR_CHOICES = [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
    ]

    std_id = models.BigAutoField(primary_key=True)

    std_first_name = models.CharField(max_length=30,null=False,validators=[name_validator])
    std_last_name = models.CharField(max_length=30,null=False,validators=[name_validator])

    std_branch=models.ForeignKey(
        Branches,
        on_delete=models.PROTECT,
        related_name="students_inthis_branch"
    )
    std_year=models.PositiveSmallIntegerField(choices=YEAR_CHOICES,null=False)

    std_roll_number = models.CharField(max_length=10,null=False,unique=True, validators=[
        roll_validator])
    std_college_email = models.CharField(max_length=7,null=False,unique=True,validators=[
        college_email_validator])

    std_phone_number = models.CharField(max_length=10,unique=True, null=False,validators=[
        phone_validator])

    std_password = models.CharField(max_length=128,null=False)

    std_joined_at = models.DateField(auto_now_add=True,null=False,db_index=True)

    # Don't remove `blank = True` from this due to validators
    std_deactivated_at = models.DateField(null=True,blank=True)


    def set_password(self, raw_password):
        self.std_password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.std_password)

    @property
    def std_full_name(self):
        return f"{self.std_first_name} {self.std_last_name}"

    def save(self, *args, **kwargs):
        ''' Defining explicitly to run validations before saving into students table '''
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.std_full_name} ({self.std_roll_number}) "


    class Meta:
        indexes = [
            models.Index(fields=[ "std_branch","std_year",]),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(std_roll_number__regex=r'^[2-9][0-9][eE][sS][kK][a-zA-Z]{2}[0-9]{3}$'),
                name="roll_number_10_digits"
            ),

            models.CheckConstraint(
                check=Q(std_phone_number__regex=r'^[6-9][0-9]{9}$'),
                name="phone_number_india"
            ),

            models.CheckConstraint(
                check=Q(std_college_email__regex=r'^[b][2-9][0-9]{5}$'),
                name="college_email_domain"
            ),

            models.CheckConstraint(
                check=~Q(std_first_name=models.F('std_last_name')),
                name="first_last_name_not_same"
            ),

        ]



class AvailableProjects(models.Model):
    avail_proj_project_name = models.CharField(max_length=100,null=False)
    avail_proj_faculty_associated = models.ForeignKey(
        Faculty,
        null=True,
        on_delete=models.SET_NULL,
        related_name='projects_ofthis_faculty')

    def __str__(self):
        return f"{self.avail_proj_project_name}"



class StudentIssueLog(models.Model):
    # ========================
    # 1. issue_date is only indexed date. So use queries involving issue_date only,
    #         to properly utilise indexes.
    # ========================

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="std_issue_logs",
    )
    component = models.ForeignKey(
        Component,
        on_delete=models.PROTECT,
        related_name="comp_issue_logs"
    )

    project = models.ForeignKey(
        AvailableProjects,
        on_delete=models.PROTECT,
        related_name="project_info")

    std_issue_quantity_issued = models.PositiveIntegerField(null=False)

    std_issue_form_date = models.DateField(null=False,blank=True)
    std_issue_issue_date = models.DateField(null=True,db_index=True,blank=True)
    std_issue_return_date = models.DateField(null=True,blank=True)

    def __str__(self):
        return f"{self.student.std_full_name}->{self.component.comp_name}"




