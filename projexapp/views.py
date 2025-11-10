from django.shortcuts import render, redirect
from .models import Project
import requests, markdown2, re, textwrap, random, os


#  GitHub API setup
# We try to get a GitHub token (if provided in the environment)
# Using a token increases the GitHub API request limit
# If no token is found, the header will remain empty

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


#  VIEW 1: project_list
# Purpose:
#   - Fetch all saved projects from the database
#   - Try to fetch a "graphs" image from each project's GitHub repo
#   - Generate a short preview text from the README
#   - Detect common Python libraries mentioned
#   - Render all this into the project list template

def project_list(request):

    # If no project exists yet, redirect user to add_project page
    if Project.objects.count() == 0:
        return redirect('add_project')

    # Get all projects ordered by most recently created
    projects = Project.objects.all().order_by('-created')

    # A few fallback graph images (used if no graph found in repo)
    fallback_graphs = [
        "https://images.ctfassets.net/w6r2i5d8q73s/2AV45NpN8eiZ0lOWHxL5bk/e43cee85fa84a174beb34a42a2536216/graphs_bar_chart_product_image_EN_big_3_2.png?fm=webp&q=75",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHYmng3U5_7H26__GVHikd9ZIsdNocj0KbuGOIt3tcIJrxoz9iap45eYmFS1dReAnNk28&usqp=CAU",
        "https://images.ctfassets.net/w6r2i5d8q73s/AYozbMBpRTsrTZAn6xavI/827fdfca0526529aa53be9fbf70c7c83/graphs_product_image_EN_standard_3_2.png",
        "https://images.ctfassets.net/w6r2i5d8q73s/7onNn71dsozT70enDLpnpS/93a52b96926ee45e0c75688c076785a9/graphs_product_image_EN_standard_3_2.png"
    ]

    # Loop through all projects
    for p in projects:

        #  STEP 1: Create a short preview of the README text
        # - Remove Markdown symbols (#, *, etc.)
        # - Clean extra spaces
        # - Shorten to 250 characters with "…" at the end

        plain_text = re.sub(r'[#*_>`\[\]\(\)\-\!]', '', p.overview)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        p.rendered_preview = textwrap.shorten(plain_text, width=250, placeholder=" …")

        #  STEP 2: Try fetching a graph image from GitHub repo
        # The function checks if there's a folder named "graphs"
        # inside the repo, and looks for image files there.
        # If found, one image is chosen randomly.
        p.graph_image = None  # Default to None first

        try:
            # Extract username and repository name from GitHub link
            username, repo = p.github_link.split("github.com/")[1].split("/")[:2]

            # GitHub API endpoint for listing files in the "graphs" folder
            api_url = f"https://api.github.com/repos/{username}/{repo}/contents/graphs"

            # Make the API request
            res = requests.get(api_url, headers=headers, timeout=10)

            # If successful, parse JSON response
            if res.status_code == 200:
                files = res.json()

                # Filter only image files (.png, .jpg, etc.)
                imgs = [f["download_url"] for f in files
                        if f["name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

                # Randomly choose one image if found
                if imgs:
                    p.graph_image = random.choice(imgs)

        except Exception:
            # If anything fails (invalid repo, timeout, etc.), skip quietly
            pass

        #  STEP 3: Assign fallback image if none was found
        if not p.graph_image:
            p.graph_image = random.choice(fallback_graphs)

        #  STEP 4: Detect common Python libraries used
        # Quick keyword search within the README text
        libs = []
        for lib in ["pandas", "numpy", "matplotlib", "seaborn",
                    "sklearn", "tensorflow", "keras", "plotly"]:
            if lib.lower() in p.overview.lower():
                libs.append(lib)
        p.libraries = libs

    #  STEP 5: Render the template with all processed data
    return render(request, 'projexapp/project_list.html', {'projects': projects})


#  VIEW 2: add_project
# Purpose:
#   - Handles the form submission for adding a new project
#   - Extracts README.md from the GitHub repository
#   - Saves project data into the database
def add_project(request):
    if request.method == 'POST':

        # Extract form fields
        title = request.POST.get('title')
        github_link = request.POST.get('github_link')

        # Default overview text (in case fetching fails)
        overview_text = "No README found or couldn't fetch it."

        try:
            # Split GitHub URL into username/repo
            username, repo = github_link.split("github.com/")[1].split("/")[:2]

            # Try to fetch README.md (first check 'main' branch)
            readme_url = f"https://raw.githubusercontent.com/{username}/{repo}/main/README.md"
            response = requests.get(readme_url)

            # If not found on main, try old 'master' branch
            if response.status_code != 200:
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo}/master/README.md"
                response = requests.get(readme_url)

            # If successful, save the README content
            if response.status_code == 200:
                overview_text = response.text

        except Exception as e:
            # If any error occurs, record the error message
            overview_text = f"Error fetching README: {e}"

        # Create and save the new Project object in the database
        Project.objects.create(title=title,
                               github_link=github_link,
                               overview=overview_text)

        # Redirect back to the project list page
        return redirect('project_list')

    # If GET request (page visit), just render the form template
    return render(request, 'projexapp/add_project.html')


#  VIEW 3: project_overview
# Purpose:
#   - Show a detailed project page with Markdown converted to HTML
def project_overview(request, project_id):

    # Fetch the project by its ID from the database
    project = Project.objects.get(id=project_id)

    # Convert Markdown text (from README) into safe HTML
    rendered_html = markdown2.markdown(project.overview)

    # Render the project overview template with both raw and HTML content
    return render(request, 'projexapp/project_overview.html', {
        'project': project,
        'rendered_html': rendered_html
    })
