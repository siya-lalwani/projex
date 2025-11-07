from django.shortcuts import render, redirect
from .models import Project
import requests, markdown2, re, textwrap, random
import os
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def project_list(request):
    if Project.objects.count() == 0:
        return redirect('add_project')
    projects = Project.objects.all().order_by('-created')

    fallback_graphs = [
        "https://images.ctfassets.net/w6r2i5d8q73s/2AV45NpN8eiZ0lOWHxL5bk/e43cee85fa84a174beb34a42a2536216/graphs_bar_chart_product_image_EN_big_3_2.png?fm=webp&q=75",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHYmng3U5_7H26__GVHikd9ZIsdNocj0KbuGOIt3tcIJrxoz9iap45eYmFS1dReAnNk28&usqp=CAU",
        "https://images.ctfassets.net/w6r2i5d8q73s/AYozbMBpRTsrTZAn6xavI/827fdfca0526529aa53be9fbf70c7c83/graphs_product_image_EN_standard_3_2.png",
        "https://images.ctfassets.net/w6r2i5d8q73s/7onNn71dsozT70enDLpnpS/93a52b96926ee45e0c75688c076785a9/graphs_product_image_EN_standard_3_2.png"
    ]

    for p in projects:
        # Clean text for preview
        plain_text = re.sub(r'[#*_>`\[\]\(\)\-\!]', '', p.overview)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        p.rendered_preview = textwrap.shorten(plain_text, width=250, placeholder=" …")

       # Try to find graph image from repo
        p.graph_image = None
        try:
            username, repo = p.github_link.split("github.com/")[1].split("/")[:2]
            api_url = f"https://api.github.com/repos/{username}/{repo}/contents/graphs"
            res = requests.get(api_url)
            if res.status_code == 200:
                files = res.json()
                imgs = [f["download_url"] for f in files if f["name"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if imgs:
                    p.graph_image = random.choice(imgs)
        except Exception:
            pass

        # If nothing found, assign fallback
        if not p.graph_image:
            p.graph_image = random.choice(fallback_graphs)

        # Quick guess for libraries (basic keyword detection)
        libs = []
        for lib in ["pandas", "numpy", "matplotlib", "seaborn", "sklearn", "tensorflow", "keras", "plotly"]:
            if lib.lower() in p.overview.lower():
                libs.append(lib)
        p.libraries = libs

    return render(request, 'projexapp/project_list.html', {'projects': projects})

def add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        github_link = request.POST.get('github_link')

        overview_text = "No README found or couldn't fetch it."
        try:
            username, repo = github_link.split("github.com/")[1].split("/")[:2]
            readme_url = f"https://raw.githubusercontent.com/{username}/{repo}/main/README.md"
            response = requests.get(readme_url)
            if response.status_code != 200:
                readme_url = f"https://raw.githubusercontent.com/{username}/{repo}/master/README.md"
                response = requests.get(readme_url)
            if response.status_code == 200:
                overview_text = response.text
        except Exception as e:
            overview_text = f"Error fetching README: {e}"

        Project.objects.create(title=title, github_link=github_link, overview=overview_text)
        return redirect('project_list')

    return render(request, 'projexapp/add_project.html')

def project_overview(request, project_id):
    project = Project.objects.get(id=project_id)
    rendered_html = markdown2.markdown(project.overview)
    return render(request, 'projexapp/project_overview.html', {
        'project': project,
        'rendered_html': rendered_html
    })
