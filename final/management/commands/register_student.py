import os
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings
from django.core.management.base import BaseCommand
from simulation.simulation_service.services import Bot

load_dotenv(Path(settings.BASE_DIR) / "config" / ".env.simulated")


class Command(BaseCommand):
    help = "One-time registration of students via the bot's registration form."

    students = [
        # Section 1 - CX
        { "number_to_english": "one", "roll_number": "25ESKCX001","email": "b250001", "std_year": "1",},
        {"number_to_english": "two", "roll_number": "25ESKCX002", "email": "b250002", "std_year": "1",},
        {"number_to_english": "three", "roll_number": "25ESKCX003", "email": "b250003", "std_year": "1",},
        {"number_to_english": "four", "roll_number": "25ESKCX004", "email": "b250004", "std_year": "1",},
        {"number_to_english": "five", "roll_number": "25ESKCX005", "email": "b250005", "std_year": "1",},
        {"number_to_english": "six", "roll_number": "25ESKCX006", "email": "b250006", "std_year": "1",},
        {"number_to_english": "seven", "roll_number": "25ESKCX007", "email": "b250007", "std_year": "1",},
        {"number_to_english": "eight", "roll_number": "25ESKCX008", "email": "b250008", "std_year": "1",},
        {"number_to_english": "nine", "roll_number": "25ESKCX009", "email": "b250009", "std_year": "1",},
        {"number_to_english": "ten", "roll_number": "25ESKCX010", "email": "b250010", "std_year": "1",},
        {"number_to_english": "eleven", "roll_number": "25ESKCX011", "email": "b250011", "std_year": "1",},
        {"number_to_english": "twelve", "roll_number": "25ESKCX012", "email": "b250012", "std_year": "1",},
        {"number_to_english": "thirteen", "roll_number": "25ESKCX013", "email": "b250013", "std_year": "1",},
        {"number_to_english": "fourteen", "roll_number": "25ESKCX014", "email": "b250014", "std_year": "1",},
        {"number_to_english": "fifteen", "roll_number": "25ESKCX015", "email": "b250015", "std_year": "1",},
        {"number_to_english": "sixteen", "roll_number": "25ESKCX016", "email": "b250016", "std_year": "1",},
        {"number_to_english": "seventeen", "roll_number": "25ESKCX017", "email": "b250017", "std_year": "1",},
        {"number_to_english": "eighteen", "roll_number": "25ESKCX018", "email": "b250018", "std_year": "1",},
        {"number_to_english": "nineteen", "roll_number": "25ESKCX019", "email": "b250019", "std_year": "1",},
        {"number_to_english": "twenty", "roll_number": "25ESKCX020", "email": "b250020", "std_year": "1",},

        # Section 2 - CY
        {"number_to_english": "twenty_one", "roll_number": "25ESKCY001", "email": "b250021", "std_year": "1",},
        {"number_to_english": "twenty_two", "roll_number": "25ESKCY002", "email": "b250022", "std_year": "1",},
        {"number_to_english": "twenty_three", "roll_number": "25ESKCY003", "email": "b250023", "std_year": "1",},
        {"number_to_english": "twenty_four", "roll_number": "25ESKCY004", "email": "b250024", "std_year": "1",},
        {"number_to_english": "twenty_five", "roll_number": "25ESKCY005", "email": "b250025", "std_year": "1",},
        {"number_to_english": "twenty_six", "roll_number": "25ESKCY006", "email": "b250026", "std_year": "1",},
        {"number_to_english": "twenty_seven", "roll_number": "25ESKCY007", "email": "b250027", "std_year": "1",},
        {"number_to_english": "twenty_eight", "roll_number": "25ESKCY008", "email": "b250028", "std_year": "1",},
        {"number_to_english": "twenty_nine", "roll_number": "25ESKCY009", "email": "b250029", "std_year": "1",},
        {"number_to_english": "thirty", "roll_number": "25ESKCY010", "email": "b250030", "std_year": "1",},
        {"number_to_english": "thirty_one", "roll_number": "25ESKCY011", "email": "b250031", "std_year": "1",},
        {"number_to_english": "thirty_two", "roll_number": "25ESKCY012", "email": "b250032", "std_year": "1",},
        {"number_to_english": "thirty_three", "roll_number": "25ESKCY013", "email": "b250033", "std_year": "1",},
        {"number_to_english": "thirty_four", "roll_number": "25ESKCY014", "email": "b250034", "std_year": "1",},
        {"number_to_english": "thirty_five", "roll_number": "25ESKCY015", "email": "b250035", "std_year": "1",},
        {"number_to_english": "thirty_six", "roll_number": "25ESKCY016", "email": "b250036", "std_year": "1",},
        {"number_to_english": "thirty_seven", "roll_number": "25ESKCY017", "email": "b250037", "std_year": "1",},
        {"number_to_english": "thirty_eight", "roll_number": "25ESKCY018", "email": "b250038", "std_year": "1",},
        {"number_to_english": "thirty_nine", "roll_number": "25ESKCY019", "email": "b250039", "std_year": "1",},
        {"number_to_english": "forty", "roll_number": "25ESKCY020", "email": "b250040", "std_year": "1",},

        # Section 3 - CS
        {"number_to_english": "forty_one", "roll_number": "23ESKCS001", "email": "b250041", "std_year": "1",},
        {"number_to_english": "forty_two", "roll_number": "23ESKCS002", "email": "b250042", "std_year": "1",},
        {"number_to_english": "forty_three", "roll_number": "23ESKCS003", "email": "b250043", "std_year": "1",},
        {"number_to_english": "forty_four", "roll_number": "23ESKCS004", "email": "b250044", "std_year": "1",},
        {"number_to_english": "forty_five", "roll_number": "23ESKCS005", "email": "b250045", "std_year": "1",},
        {"number_to_english": "forty_six", "roll_number": "23ESKCS006", "email": "b250046", "std_year": "1",},
        {"number_to_english": "forty_seven", "roll_number": "23ESKCS007", "email": "b250047", "std_year": "1",},
        {"number_to_english": "forty_eight", "roll_number": "23ESKCS008", "email": "b250048", "std_year": "1",},
        {"number_to_english": "forty_nine", "roll_number": "23ESKCS009", "email": "b250049", "std_year": "1",},
        {"number_to_english": "fifty", "roll_number": "23ESKCS010", "email": "b250050", "std_year": "1",},
        {"number_to_english": "fifty_one", "roll_number": "23ESKCS011", "email": "b250051", "std_year": "1",},
        {"number_to_english": "fifty_two", "roll_number": "23ESKCS012", "email": "b250052", "std_year": "1",},
        {"number_to_english": "fifty_three", "roll_number": "23ESKCS013", "email": "b250053", "std_year": "1",},
        {"number_to_english": "fifty_four", "roll_number": "23ESKCS014", "email": "b250054", "std_year": "1",},
        {"number_to_english": "fifty_five", "roll_number": "23ESKCS015", "email": "b250055", "std_year": "1",},
        {"number_to_english": "fifty_six", "roll_number": "23ESKCS016", "email": "b250056", "std_year": "1",},
        {"number_to_english": "fifty_seven", "roll_number": "23ESKCS017", "email": "b250057", "std_year": "1",},
        {"number_to_english": "fifty_eight", "roll_number": "23ESKCS018", "email": "b250058", "std_year": "1",},
        {"number_to_english": "fifty_nine", "roll_number": "23ESKCS019", "email": "b250059", "std_year": "1",},
        {"number_to_english": "sixty", "roll_number": "23ESKCS020", "email": "b250060", "std_year": "1",}
    ]
    def handle(self, *args, **options):
        bot = Bot()

        self.stdout.write(f"Registering students ...")
        for student in self.students:
            ok = bot.register(
                number_to_english=student["number_to_english"],
                roll_number=student["roll_number"],
                email=student["email"],
                password=os.environ.get("BOT_PASSWORD"),
                std_year=student["std_year"],
            )
            if ok:
                pass
            else:
                self.stderr.write(self.style.ERROR("failed"))
        self.stdout.write(f"Register complete ...")