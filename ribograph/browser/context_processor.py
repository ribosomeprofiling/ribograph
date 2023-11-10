from .models import Project, Experiment
import os

def get_user_projects(request):
    """
    Find the list of projects the user should have access to depending on
    if they're logged in, and experiments for each of them
    """
    if request.user.is_authenticated:
        # projects = Project.objects.filter(owner=request.user)
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(public=True)

    projects_experiments = {
        project: Experiment.objects.filter(project=project) for project in projects
    }
    return {"projects": projects_experiments, "project": {}, "experiment": {}}


def debug_mode(request):
    """
    Controls whether or not the debug vue server is used, or built static assets
    """
    return {
        "DEBUG": request.META["DEBUG"]
        and (
            request.META["HTTP_HOST"].split(":")[0]
            in request.META["DJANGO_ALLOWED_HOSTS"]
        ),
        "RUN_VUE_SERVER": os.getenv('RUN_VUE_SERVER')
    }
