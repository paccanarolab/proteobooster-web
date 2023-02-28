from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("downloads/", views.downloads, name="downloads"),
    path("organism/<int:organism_taxon_id>/", views.organism, name="organism"),
    path("protein/<str:protein_accession>/", views.protein, name="protein"),
    path("interaction/<str:first_accession>/<str:second_accession>/", views.interaction, name="interaction"),
    path("interolog/<str:first_accession>/<str:second_accession>/", views.interolog, name="interolog"),
    path("complex/<int:predicted_complex_id>/", views.complex, name="complex"),
    path("go_term/<str:go_term_goid>/", views.home, name="go_term"),
    #API
    path("api/proteins", views.get_proteins, name="get_proteins"),
    path("api/complex/<int:complex_id>", views.get_complex_graph, name='api_complex_graph'),
    path("api/protein/<str:protein_accession>", views.get_protein_graph, name='api_protein_graph'),
]
