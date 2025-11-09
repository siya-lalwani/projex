#  Projex — AI-Powered Project Overview Generator

**Live Demo:** [https://projex-i3o1.onrender.com](https://projex-i3o1.onrender.com)  
**Built with:** Django, Python, HTML/CSS, Markdown2, Requests  

---

##  Overview
**Projex** is a simple web app that allows users to **add their GitHub project link** and automatically generates a **beautiful overview card** for each repository.  

When a GitHub repo link is added, the app:
- Fetches the repository’s `README.md`
- Converts it into a clean plain-text overview
- Displays it as a card on the homepage
- Allows users to open the full overview or jump directly to the GitHub code

Perfect for quickly showcasing your **AI/ML**, **data science**, or **Python projects** in one elegant dashboard.

---

##  Features
-  **Automatic README fetch:** Just paste a GitHub repo link — no manual input required.  
-  **Smart Overview:** Markdown is parsed and formatted into clean plain text.  
-  **Multi-Project Support:** Add as many repos as you like; each gets its own project card.  
-  **Direct GitHub Redirects:** Each project overview links back to its original repository.  
-  **Minimal & Elegant UI:** Styled with basic HTML + CSS for a lightweight experience.  

---

##  Tech Stack
| Layer | Tools Used |
|-------|-------------|
| **Frontend** | HTML, CSS |
| **Backend** | Django , Python  |
| **Dependencies** | `markdown2`, `requests`, `whitenoise`, `gunicorn`, `dj-database-url` |
| **Hosting** | Render.com (Deployment) |

---

##  How It Works
1. Visit the live app at **[projex-i3o1.onrender.com](https://projex-i3o1.onrender.com)**
2. Click “Add Project”
3. Enter your project title and GitHub repository link *(ensure the repo has a README.md file)*
4. Projex automatically fetches, parses, and displays the overview as a card
5. Click the project card to see the full README or open the code on GitHub

---

##  Local Setup

Clone and run locally:

```bash
git clone https://github.com/siya-lalwani/projex.git
cd projex
python -m venv venv
venv\Scripts\activate  # (or source venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
