from django.core.management.base import BaseCommand

# -------- Only Pycharm errors -----------------
from simulation.simulation_service.services import StudentSimulator, TeacherSimulator

class Command(BaseCommand):
    help = "Runs daily student issue and teacher review jobs"

    def handle(self, *args, **options):
        student = StudentSimulator()
        student.issue()
        self.stdout.write(self.style.SUCCESS("student issue done"))

        teacher = TeacherSimulator()
        teacher.run_daily_review()
        self.stdout.write(self.style.SUCCESS("teacher review done"))