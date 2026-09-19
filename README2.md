<div align="center">

<img src="Data/photo1.png" width="45%" alt="Screenshot 1" />
<img src="Data/photo2.png" width="45%" alt="Screenshot 2" />

# Inventory Management Website
<br>

![Repo Size](https://img.shields.io/github/repo-size/OWNER/REPO?color=blue&label=Repo%20Size)
[![GitHub](https://img.shields.io/badge/GitHub-OWNER-181717?style=flat&logo=github)](https://github.com/vaibhav3209)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/vaibhav3209)

<a href="#members">
  <img src="https://img.shields.io/badge/Contributors-View%20Team-blueviolet?style=flat&logo=github" />
</a>
</div>

<br>

## Table of Contents

- To be filled later with referneces 


## 🛠️ Installation (Direct Deployment)

### 1. Project Setup

```bash
# Create and enter parent folder
mkdir inventory-management
cd inventory-management

# Clone the repository
git clone https://github.com/IOT_COE.git .

# Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

> **Using PyCharm?** Go to *Settings → Project → Python Interpreter* and select the interpreter from the `venv` folder you just created.

Install dependencies:

```bash
# since requirements.txt file is in config folder
pip install -r config/requirements.txt
```

---

### 2. Environment Configuration

Inside the `config/` folder, create two files:
- config/.env
- config/.env.simulated

Populate `.env` with the following fields:

| Variable | Development                  | Production                                                                          |
|---|------------------------------|-------------------------------------------------------------------------------------|
| `DATABASE_URL` | Supabase connection string   | Supabase connection string                                                          |
| `SECRET_KEY` | Any generated key            | Strong, unique secret key (see [Generating a Secret Key](#generating-a-secret-key)) |
| `DEBUG` | `True`                       | `False`                                                                             |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1`        | Your Render app domain                                                              |
| `ADMIN_PATH` | Any custom path              | Custom, non-default path                                                            |
| `SESSION_COOKIE_SECURE` | `False`                      | `True`                                                                              |
| `CSRF_COOKIE_SECURE` | `False`                      | `True`                                                                              |
| `SESSION_COOKIE_AGE` | Longer (for convenience)     | Shorter, per security policy                                                        |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000`      | Your Render app URL                                                                 |
| `REDIS_URL` | Upstash string               | Upstash string                                                                      |
| `BOT_PASSWORD` | Test password                | Secure production password                                                          |
| `TEACHER` | Test teacher username        | Production teacher username                                                         |
| `TEACHER_PASS` | Test password                | Secure production password                                                          |
| `RENDER_APP_URL` | —                            | Your deployed Render app URL                                                        |

---

### 3. Database & Cache Setup

1. Create a [Supabase](https://supabase.com) account and project. Use the **session pooler** connection string for `DATABASE_URL`.
2. Create an [Upstash](https://upstash.com) account and connect it for `REDIS_URL`.
3. Generate and apply migrations to create the Supabase tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. For **data only** (never schema changes), run the provided SQL directly in the Supabase SQL editor.

```sql
/*
Insert first two then see the data inside tables. Then see the NOTE..
*/
-- 1. Fill table branches

-- insert into public.final_branches(branches_branch_name,branches_branch_code,branches_rollno_code)
-- values ('Artificial Intelligence','AI','CA'),
-- ('Civil','CE','CE'),
-- ('Computer Science','CS','CS'),
-- ('Data Science','DS','CX'), 
-- ('Electrical','EE','EE'),
-- ('Electronics','ECE','ECE'),
-- ('Internet of Things','IOT','CY'),
-- ('Information Technology','IT','IT'),
-- ('Mechanical','ME','ME');

-- 2. fill table componentcategory

-- INSERT INTO public.final_componentcategory(comp_cate_category_name)
-- VALUES ('Actuators'),
-- ('Displays'),
-- ('Electric Components'),
-- ('Microcontrollers / Boards'),
-- ('Miscellaneous'),
-- ('Sensors');

/*
NOTE: the integer id must be checked in the database exists or not as they are referencing record
*/
-- 3. Fill table final_faculty

-- INSERT INTO "public"."final_faculty" ("faculty_name", "faculty_dept_id") 
-- VALUES 
-- ('Deepak Chahar', 3),
-- ('Pandit Sharma', 3),
-- ('Greta Gupta', 5),
-- ('Bill Agarwal', 5),
-- ('Donald Sir', 7),
-- ('Albert Joshi', 7);


-- 4. Fill table final_availableprojects

-- insert into final_availableprojects(avail_proj_project_name,avail_proj_faculty_associated_id)
-- values 
-- ('Smart Attendance system',7),
-- ('Urban Congestion mgmt',7),
-- ('Phishing Detection system',8),
-- ('Animal Detection system',8),
-- ('Camera Parking system',8),
-- ('Offline Banking system',9),
-- ('Project Proposal system',9),
-- ('Mechanical Car',10),
-- ('XYZ project',10),
-- ('Hydraulic Switching machine',9),
-- ('Temperature Monitor',11);

/*
5. Insert Students from Python script
6. Insert Conmponents from Excel file
*/
```

---

### 4. Import Components

```bash
# Run in terminal
python manage.py import_components_excel Data/Components_List.xlsx
```

---

### 5. Create a Superuser

Create a Django superuser for teacher/admin access:

```bash
python manage.py createsuperuser
```

> ⚠️ The username **must end with `admin`** — this is required by the app's role-detection logic.

---

### 6. Version Control

Push to your own GitHub repository, or fork this one and update the remote:

```bash
git remote set-url origin https://github.com/IOT_COE.git
git push -u origin main
```

---

### 7. Deployment on Render

Deploy the project on [Render](https://render.com) using the following:

- **Build Command:** *pip install -r config/requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput*
- **Start Command:** *gunicorn teststudy.wsgi:application*

---

### 8. Register Students

Once deployed, register students via the terminal:

```bash
# run in terminal
Python manage.py register_students
```

If You followed till here you will have your website deployed at an instant!!!


### 👥 Team