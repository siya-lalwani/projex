from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    github_link = models.URLField()
    overview = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
