from django.urls import path

from . import views
from .api import register_experiment_api, register_project_api

app_name = "browser"

apipatterns = [
    path(f"api/experiment/<int:experiment_id>/{endpoint}", func)
    for endpoint, func in register_experiment_api.all.items()
]

apipatterns += [
    path(f"api/project/<int:project_id>/{endpoint}", func)
    for endpoint, func in register_project_api.all.items()
]

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "<int:project_id>/gene_correlation",
        views.gene_correlation_redirect,
        name="gene_correlation",
    ),
    path(
        "<int:project_id>/gene_correlation/<str:reference_hash>",
        views.gene_correlation,
        name="gene_correlation",
    ),
    path(
        "<int:project_id>/compare_experiments",
        views.compare_experiments,
        name="compare_experiments",
    ),
    path("<int:experiment_id>/coverage", views.coverage, name="coverage"),
    path("<int:experiment_id>/offset", views.offset, name="offset"),
    path("references", views.references, name="references"),
    path(
        "<str:reference_hash>/record_reference",
        views.record_reference,
        name="record_reference",
    ),
    path("add_reference", views.add_reference, name="add_reference"),
    path("add_project", views.add_project, name="add_project"),
    path(
        "<int:project_id>/project_details",
        views.project_details,
        name="project_details",
    ),
    path(
        "<int:experiment_id>/experiment_details",
        views.experiment_details,
        name="experiment_details",
    ),
    path(
        "<int:experiment_id>/delete_experiment",
        views.delete_experiment,
        name="delete_experiment",
    ),
    path(
        "<int:experiment_id>/erase_experiment",
        views.erase_experiment,
        name="erase_experiment",
    ),
    path(
        "<int:experiment_id>/download_ribo", views.download_ribo, name="download_ribo"
    ),
    path(
        "<int:project_id>/<str:file_digest>/project_details",
        views.confirm_ribo_file,
        name="confirm_ribo_file",
    ),
    path(
        "<int:project_id>/delete_project", views.delete_project, name="delete_project"
    ),
    path("<int:project_id>/erase_project", views.erase_project, name="erase_project"),
    path("add_admin_user", views.add_admin_user, name="add_admin_user"),
    path(
        "<int:project_id>/edit_project_description",
        views.edit_project_description,
        name="edit_project_description",
    ),
    path(
        "<int:reference_id>/reference_details",
        views.reference_details,
        name="reference_details",
    ),
    path(
        "<int:reference_id>/download_reference",
        views.download_reference,
        name="download_reference",
    ),
    path(
        "<int:reference_id>/delete_reference",
        views.delete_reference,
        name="delete_reference",
    ),
    path(
        "<int:reference_id>/erase_reference",
        views.erase_reference,
        name="erase_reference",
    ),
    *apipatterns,
]
