from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("downloads/", views.downloads, name="downloads"),
    path("downloads/organism/<int:organism_taxon_id>/interactions/", views.organism_download_interactions, name='organism_download_interactions'),
    path("downloads/organism/<int:organism_taxon_id>/interologs/", views.organism_download_interologs, name='organism_download_interologs'),
    path("downloads/organism/<int:organism_taxon_id>/complexes/", views.organism_download_complexes, name='organism_download_complexes'),
    path("organism/<int:organism_taxon_id>/", views.organism, name="organism"),
    path("organism/all/", views.organisms, name="organisms"),
    path("protein/<str:protein_accession>/", views.protein, name="protein"),
    path("proteins/<int:organism_taxon_id>", views.proteins, name="all_proteins"),
    path("interaction/<str:first_accession>/<str:second_accession>/", views.interaction, name="interaction"),
    path("interolog/<str:first_accession>/<str:second_accession>/", views.interolog, name="interolog"),
    path("complex/<int:predicted_complex_id>/", views.complex, name="complex"),
    path("complex/all/", views.complexes, name="complexes"),
    path("go_term/<str:go_term_goid>/", views.go_term, name="go_term"),
    #API
    path("api/proteins", views.get_proteins, name="get_proteins"),
    path("api/complex/<int:complex_id>", views.get_complex_graph, name='api_complex_graph'),
    path("api/protein/<str:protein_accession>", views.get_protein_graph, name='api_protein_graph'),
    path("api/lm/complex/", views.api_lm_complex, name='api_lm_complex'),
    path("api/lm/interolog/", views.api_lm_interolog, name='api_lm_interolog'),
    path("api/lm/protein/", views.api_lm_protein, name='api_lm_protein'),
    path("api/lm/interaction/", views.api_lm_interaction, name='api_lm_interaction'),
    path("api/lm/goterm/", views.api_lm_goterm, name='api_lm_goterm'),
    path("api/lm/evidence/", views.api_lm_evidence, name='api_lm_evidence'),
]
