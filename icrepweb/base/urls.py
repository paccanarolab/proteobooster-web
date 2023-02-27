from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.home, name="about"),
    path("organism/<int:organism_taxon_id>/", views.organism, name="organism"),
    path("protein/<str:protein_accession>/", views.protein, name="protein"),
    path("interaction/<str:first_accession>/<str:second_accession>/", views.interaction, name="interaction"),
    path("interolog/<str:first_accession>/<str:second_accession>/", views.interaction, name="interolog"),
    path("complex/<int:predicted_complex_id>/", views.home, name="complex"),
    path("go_term/<str:go_term_goid>/", views.home, name="go_term"),
    path("downloads/", views.home, name="downloads"),
    #API
    path("api/proteins/", views.get_proteins, name="get_proteins"),
]
