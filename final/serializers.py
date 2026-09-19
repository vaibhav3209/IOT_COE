# from rest_framework import serializers
# from .models import Student,StudentIssueLog,Component
#
# # ===============================
# # made different serializers to print data in a specific format
# # student,component will appear in separate dictionary and project is foreign key  but taken in only one line.
# # ===============================
#
# class StudentSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source="std_first_name")
#     last_name = serializers.CharField(source="std_last_name")
#     year = serializers.IntegerField(source="std_year")
#     branch = serializers.CharField(read_only=True,source="std_branch.branches_branch_code")
#     joined_at = serializers.DateField(source="std_joined_at")
#     deactivated_at = serializers.DateField(source="std_deactivated_at")
#
#     class Meta:
#         model = Student
#         fields = ['first_name','last_name','year','branch','joined_at','deactivated_at']
#
# class ComponentSerializer(serializers.ModelSerializer):
#     component_name = serializers.CharField(source='comp_name')
#     category = serializers.CharField(read_only=True,
#                                      source="comp_category.comp_cate_category_name")
#     popularity = serializers.IntegerField(source='comp_popularity')
#
#     class Meta:
#         model = Component
#         fields = ['component_name','category','popularity']
#
#
# class StudentIssueLogSerializer(serializers.ModelSerializer):
#     student = StudentSerializer(read_only=True)
#     component = ComponentSerializer(read_only=True)
#     quantity_issued = serializers.IntegerField(source="std_issue_quantity_issued")
#     related_project = serializers.CharField(read_only=True,source="project.avail_proj_project_name")
#     form_date = serializers.DateField(source="std_issue_form_date")
#     issue_date = serializers.DateField(source="std_issue_issue_date")
#     return_date = serializers.DateField(source="std_issue_return_date")
#
#
#     class Meta:
#         model = StudentIssueLog
#         fields = ['student','component','quantity_issued','related_project','form_date','issue_date','return_date']
#         # These are API tags and only expose these columns