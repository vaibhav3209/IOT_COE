# --------- Utility libraries ---------
import random, requests

# --------    Django  ------------------
import django
from pathlib import Path

# -------     System ---------------------
import os,sys
from dotenv import load_dotenv



# ------ Configurations -------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teststudy.settings")
django.setup()

# ------ Load  .env file ---------------
load_dotenv(BASE_DIR / "config" / ".env.simulated")


# ------- Cache imports(only Pycharm error, site works fine) ----------------
from final.views import (
    get_all_categories,
    component_in_category_x,
    get_all_available_projects,
    bot_usernames
)


# ----------------   MAIN URL  --------------------------------
BASE_URL = os.getenv("RENDER_APP_URL", "http://127.0.0.1:8000")

class Bot:
    """
    One instance = one bot = one requests.Session for its whole lifetime.

    Usage pattern:
        bot = BotClient()
        bot.register(...)          # once, when the bot is created
        for _ in range(n_cycles):
            bot.login(username, password)
            ...                     # do request as students / Approve as teachers
            bot.logout(role="student")
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.login_url = f"{self.base_url}/login/"
        self.student_logout_url = f"{self.base_url}/student/logout/"
        self.teacher_logout_url = f"{self.base_url}/teacher/logout/"
        self.submit_request_url = f"{self.base_url}/student/submit_request/"

        self.session = requests.Session()
        self._csrf_valid = False  # tracks whether our cached token is still usable

        self.projects = get_all_available_projects()
        self.categories = get_all_categories()



    # ---------- internal helpers ----------
    def _ensure_csrf(self, url: str) -> str:
        """
        Return a usable CSRF token, fetching a fresh one only if we don't
        already have a valid one cached for this session.
        """
        if self._csrf_valid:
            token = self.session.cookies.get("csrftoken")
            if token:
                return token

        resp = self.session.get(url)
        if resp.status_code != 200:
            raise Exception(f"Unable to load page for CSRF: {url}")

        token = self.session.cookies.get("csrftoken")
        if not token:
            raise Exception("CSRF token not found.")

        self._csrf_valid = True
        return token



    def _post(self, url: str, data: dict, referer: str = None, use_header_token: bool = False):
        """
        Shared POST logic: attaches CSRF (either as form field or header),
        sets Referer, and posts through the single session.
        """
        csrf = self._ensure_csrf(referer or url)
        headers = {"Referer": referer or url}

        if use_header_token:
            headers["X-CSRFToken"] = csrf
        else:
            data["csrfmiddlewaretoken"] = csrf

        return self.session.post(url, data=data, headers=headers)



    def _invalidate_csrf(self):
        self._csrf_valid = False



    # ---------- one-time ------------
    def register(self, number_to_english, roll_number, email, password, std_year: str):
        payload = {
            "form_type": "user_signup",
            "first_name": "bot",
            "last_name": f"{number_to_english}",
            "roll_number": f"{roll_number}",
            "college_email": f"{email}",
            "password": password,
            "phone_number": f"98{random.randint(70000000, 99999999)}",
            "std_year": f"{std_year}",
        }

        resp = self._post(self.login_url, payload)

        if resp.status_code == 200:
            print(f"Registered successful for bot{number_to_english}")
            return True

        print("Registration unsuccessful")
        return False



    # ---------- Everyday use -----------
    def login(self, username, password):
        payload = {
            "form_type": "user_login",
            "username": username,
            "password": password,
        }

        resp = self._post(self.login_url, payload)

        if resp.url.endswith("/student/"):
            print(f"{username} login successful ({resp.status_code})")
            return True

        if resp.url.endswith("/dashboard/"):
            print(f"Teacher login successful ({resp.status_code})")
            return True

        print(f"Login failed for {username} ({resp.status_code})")
        return False



    def logout(self, role: str):
        if role == "student":
            url = self.student_logout_url
        elif role == "teacher":
            url = self.teacher_logout_url
        else:
            raise ValueError("role must be 'student' or 'teacher'")

        resp = self._post(url, data={}, referer=url, use_header_token=True)
        self._invalidate_csrf()  # next login must fetch a fresh token

        if resp.status_code == 200:
            print(f"{role.capitalize()} logged out")
            return True

        print("Logout failed")
        return False



    def submit_request(self):
        """Pick a random project + up to 3 components from a random category, submit."""
        random_project = random.choice(self.projects)
        random_category = random.choice(self.categories)
        random_components = component_in_category_x(random_category)
        selected_components = random.sample(random_components, min(2, len(random_components)))

        # ------ NOTE: Personally, keeping every qty = 1 ----------------
        payload = {
            "project_id": [str(random_project.id)],
            "component_ids[]": [str(i) for i in selected_components],
            "quantities[]": ["1" for _ in selected_components],
        }

        resp = self._post(self.submit_request_url, payload, use_header_token=True)

        if resp.status_code == 200:
            print("Request submitted successfully")
            return True

        print("Unsuccessful request submission")
        print(resp.text)
        return False



class StudentSimulator:
    """
    Usage:
            objectname = Student()
            objectname.issue()

    - Automatically for random(4,8) students
        Login -->> Submit_request -->> Logout
    """

    def __init__(self):
        self.password = os.getenv("BOT_PASSWORD")



    def issue(self):
        bot_student_list = bot_usernames()          # ....... List of dictionary hai. ..............

        # ...... Selcting 1, 2 students to keep project alive only ............
        cohort = random.sample(bot_student_list, k=random.randint(1,2))

        for student in cohort:
            bot = Bot()
            try:
                # ------- if he logged in, then only we will submit request else directly logout
                if bot.login(student["std_roll_number"], self.password):
                    bot.submit_request()
            except Exception as e:
                print(f"[FAIL] {student['std_roll_number']}: {e}")
                continue
            finally:
                bot.logout('student')



class TeacherSimulator:
    """
        Usage:
    """

    def __init__(self):
        self.bot = Bot()
        self.username = os.getenv('TEACHER')
        self.password = os.getenv('TEACHER_PASS')
        self.pending_url = f"{BASE_URL}/teacher/pendingissues/"
        self.to_return_url = f"{BASE_URL}/teacher/to_return/"
        self.update_status_url = f"{BASE_URL}/teacher/update-status/"



    def _get_json(self, url):
        resp = self.bot.session.get(url)
        try:
            return resp.json()
        except ValueError:
            print(f"Couldn't fetch {url} (status {resp.status_code}, not JSON)")
            return []


    def _update_status(self, item, status):


        payload = {
            "log_id": item["id"],
            "status_to_update": status

        }
        resp = self.bot._post(self.update_status_url, payload)
        if resp.status_code != 200:
            print(f"[FAIL] {status} {item['student__std_roll_number']}: {resp.status_code}")
        return resp.status_code == 200



    def run_daily_review(self, approve_pct=(0.5, 0.6), return_pct=(0.3, 0.4)):
        """ NOTE: We are approving 50, 60 percent of request and returning 30-40%"""
        if not self.bot.login(self.username, self.password):
            print("Teacher not logged in")
            return

        try:
            # ........... IMPORTANT NOTE ...........
            # 1. While Approving "Issue_date" is nuLL in the response
            pending = self._get_json(self.pending_url)
            # print(pending)
            if pending:
                pct = random.uniform(*approve_pct)
                k = round(len(pending) * pct)
                to_approve = random.sample(pending, k)
                for item in to_approve:
                    self._update_status(item, "approve")

            # ........... IMPORTANT NOTE ...........
            # 1. While returning "Issue_date" is not nuLL in the response
            returnable = self._get_json(self.to_return_url)
            # print(returnable)
            if returnable:
                pct = random.uniform(*return_pct)
                k = round(len(returnable) * pct)
                to_return_batch = random.sample(returnable, k)
                for item in to_return_batch:
                    self._update_status(item, "return")
        finally:
            self.bot.logout(role="teacher")