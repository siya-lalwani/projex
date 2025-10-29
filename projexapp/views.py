from django.shortcuts import render, redirect
from .models import Project
import requests, markdown2, re, textwrap

def project_list(request):
    if Project.objects.count() == 0:
        return redirect('add_project')
    projects = Project.objects.all().order_by('-created')
    for p in projects:
        plain_text = re.sub(r'[#*_>`\[\]\(\)\-\!]', '', p.overview)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        short_preview = textwrap.shorten(plain_text, width=300, placeholder=" …")
        p.rendered_preview = short_preview
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
