from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django import forms
from django.db.models import Q
from .models import Protein, ExperimentalProteinInteraction, PredictedProteinInteraction, PredictedComplex
import json
import logging
from itertools import chain
from collections import defaultdict

LIMITS = {
    "MAX_GRAPH_SIZE":20,
    "MIN_QUALITY":95,
}


logger = logging.getLogger(__name__)

TOOLTIPS = {
	'interaction': 'Interactions supported by experimental evidence published in peer-reviewed articles.',
	'sibling-interaction': 'Sibling experimental interactions are those who could have been the source of this interaction. This is, if evidence was not available, this would have been an interolog.',
	'interolog': 'Inferred interactions based on the similarity of the proteins with existent interactions. Please go to <a href="https://www.ncbi.nlm.nih.gov/pubmed/15173116">Yu et al., 2004 <i class="fa fa-external-link"></i></a> for further details.',
	'complex': 'Inferred protein complexes. Computed using The <a href="http://www.paccanarolab.org/cluster-one/">ClusterONE <i class="fa fa-external-link"></i></a> algorithm.',
	'evidence': 'Published articles that back up the experimental interaction.',
	'source-interaction': 'The experimental interaction that was used to infer this interolog.'
}

def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

# Create your views here.
class HomePageForm(forms.Form):
    protein_accession = forms.CharField(required=True)

def home(request):
    context = {}
    if request.method == "POST":
        home_page_form = HomePageForm(request.POST)
        if home_page_form.is_valid():
            url = f"protein/{home_page_form.cleaned_data['protein_accession']}/"
            return redirect(url)
        else:
            logger.warning("this is NOT valid")
    return render(request, "home.html", context) 

def downloads(request):
    data = {
        'active':'downloads',
        'title':'ICRep | Downloads'
    }
    return render(request, "downloads.html", data)

def about(request):
    data = {
        'active':'about',
        'title':'ICRep | About'
    }
    return render(request, "about.html", data)

def protein(request, protein_accession):
    protein = get_object_or_404(Protein, accession=protein_accession)
    logger.warning(protein.id)
    experimental_interaction_list = []
    inferred_interolog_list = []
    context = dict()
    context['tooltips'] = TOOLTIPS
    experimental_interaction_list = ExperimentalProteinInteraction.objects.filter(Q(first=protein) | Q(second=protein))[:10]
    context['interaction_count'] = ExperimentalProteinInteraction.objects.filter(Q(first=protein) | Q(second=protein)).count()
    context['load_more_interactions'] = context['interaction_count'] > 10
    inferred_interolog_list = PredictedProteinInteraction.objects.filter((Q(first=protein) | Q(second=protein))).order_by('-quality')[:10]
    context['interolog_count'] = PredictedProteinInteraction.objects.filter((Q(first=protein) | Q(second=protein))).count()
    context['load_more_interologs'] = context['interolog_count'] > 10

    predicted_complex_list = []
    predicted_complex_set = protein.predictedcomplex_set.filter(size__lte=80)[:10]
    context['complex_count'] = protein.predictedcomplex_set.filter(size__lte=80).count()
    context['load_more_complexes'] = context['complex_count'] > 10
    for predicted_complex in predicted_complex_set:
        predicted_complex_protein_set = predicted_complex.proteins.all()
        predicted_complex_protein_list = list(predicted_complex_protein_set)
        predicted_complex_list.append([predicted_complex.id, predicted_complex_protein_list, predicted_complex.size])
    go_term_set = protein.goa_assigned_goterms.all()[:10]
    go_term_list = list(go_term_set)
    context['goterm_count'] = protein.goa_assigned_goterms.count()
    context['load_more_goterms'] = context['goterm_count'] > 10
    context["protein"] =  protein
    context["experimental_interaction_list"] = experimental_interaction_list
    context["inferred_interolog_list"] = inferred_interolog_list
    context["predicted_complex_list"] = predicted_complex_list
    context["go_term_list"] =  go_term_list
    context["activity"] = 'protein'
    return render(request, "protein.html", context)

def organism(request, organism_taxon_id):
    return render(request, "home.html") 

def interaction(request, first_accession, second_accession):
    return render(request, "home.html") 

def interolog(request, first_accession, second_accession):
    data = dict()
    data['tooltips'] = TOOLTIPS
    first = get_object_or_404(Protein, accession=first_accession)
    second = get_object_or_404(Protein, accession=second_accession)
    inferred_interolog = get_object_or_404(PredictedProteinInteraction, 
        (Q(first=first) & Q(second=second)) |
        (Q(second=first) & Q(first=second)) 
    )    
    source_experimental_interaction_list = []
    sibling_inferred_interolog_list = []

    inferred_interolog_with_same_interactors_set = PredictedProteinInteraction.objects.filter(
        (Q(first=inferred_interolog.first) & Q(second=inferred_interolog.second)) |
        (Q(second=inferred_interolog.first) & Q(first=inferred_interolog.second))
        ).order_by('-quality')[:10]

    data['interaction_count'] = PredictedProteinInteraction.objects.filter( (Q(first=inferred_interolog.first) & Q(second=inferred_interolog.second)) | (Q(second=inferred_interolog.first) & Q(first=inferred_interolog.second))).count()
    data['load_more_interactions'] = data['interaction_count'] > 10

    # TODO: ask Alfonso whether sibling interologs are interesting 
    for inferred_interolog_with_same_interactors in inferred_interolog_with_same_interactors_set:
        source_experimental_interaction = inferred_interolog_with_same_interactors.origin_experimental
        source_experimental_interaction_list.append([
            source_experimental_interaction,
            inferred_interolog_with_same_interactors.quality])
        #sibling_inferred_interolog_set = source_experimental_interaction.predictedproteininteraction_set.all()
        #for sibling_inferred_interolog in sibling_inferred_interolog_set:
        #    sibling_inferred_interolog_list.append(sibling_inferred_interolog)
    predicted_complex_list = []
    predicted_complex_set = inferred_interolog.predictedcomplex_set.all()[:10]
    data['complex_count'] = inferred_interolog.predictedcomplex_set.count()
    data['load_more_complexes'] = data['complex_count'] > 10
    for predicted_complex in predicted_complex_set:
        predicted_complex_protein_set = predicted_complex.proteins.all()[:10]
        predicted_complex_protein_list = list(predicted_complex_protein_set)
        predicted_complex_list.append([predicted_complex.id, predicted_complex_protein_list, predicted_complex.size])
    data["inferred_interolog"] = inferred_interolog
    data["source_experimental_interaction_list"] = source_experimental_interaction_list
    #data["sibling_inferred_interolog_list"] = sibling_inferred_interolog_list[:10]
    data["predicted_complex_list"] = predicted_complex_list
    return render(request, "interolog.html", data)

def complex(request, predicted_complex_id):
    predicted_complex = get_object_or_404(PredictedComplex, pk=predicted_complex_id)
    protein_set = predicted_complex.proteins.all()
    protein_list = list(protein_set)
    context = dict()
    context['tooltips'] = TOOLTIPS
    experimental_interaction_set = predicted_complex.exp_interactions.all()
    inferred_interolog_set = predicted_complex.pred_interactions.all()
    experimental_interaction_and_inferred_interolog_set = chain(experimental_interaction_set, inferred_interolog_set)
    experimental_interaction_and_inferred_interolog_list = list(experimental_interaction_and_inferred_interolog_set)
    # TODO: verify that this is correct with Alfonso
    similar_predicted_complex_list = []
    #similar_predicted_complex_set = PredictedComplex.objects.all()[:10]
    #for similar_predicted_complex in similar_predicted_complex_set:
    #    predicted_complex_protein_set = similar_predicted_complex.proteins.all()[:10]
    #    predicted_complex_protein_list = list(predicted_complex_protein_set)
    #    similar_predicted_complex_list.append([1, similar_predicted_complex.id, predicted_complex_protein_list])
    complex_functional_assignment_set = predicted_complex.complexfunctionalassignment_set.all()[:10]
    complex_functional_assignment_list = list(complex_functional_assignment_set)
    context["predicted_complex"] = predicted_complex
    context["protein_list"] = protein_list
    context["experimental_interaction_list"] = list(experimental_interaction_set)
    context["interaction_count"] = len(context["experimental_interaction_list"])
    context["inferred_interolog_list"] = list(inferred_interolog_set)
    context['interolog_count'] = len(context["inferred_interolog_list"])
    context["experimental_interaction_and_inferred_interolog_list"] = experimental_interaction_and_inferred_interolog_list
    context["similar_predicted_complex_list"] = similar_predicted_complex_list
    context["complex_functional_assignment_list"] = complex_functional_assignment_list
    return render(request, "predicted_complex.html", context)

def go_term(request, go_term_goid):
    return render(request, "home.html") 


# API
def get_proteins(request):
    data = "fail"
    logger.warning(request.get_full_path())
    if request.method == "GET":
        query = request.GET.get("term", "")
        logger.warning(request.GET.get("term"))
        logger.warning(f"{request.GET}, {query}")
        proteins = Protein.objects.filter(Q(accession__istartswith=query.upper())).order_by("accession")[:20]
        proteins = proteins.values_list("accession")
        data = json.dumps([{"label":str(i[0]), "value":str(i[0])} for i in proteins])
    mimetype = "application/json"
    return HttpResponse(data, content_type=mimetype)

EXPERIMENTAL_INTERACTION_COLOUR = 'rgba(0,155,155,0.74)'
SECONDARY_INTERACTION_COLOUR = 'rgba(112,212,155,0.84)'
PREDICTED_INTERACTION_COLOUR = 'rgba(199, 74, 167, 0.84)'

def get_interactions_dict(interaction_set, colour):
    ''' 
    helper function to get a dictionary from an interaction set
    in order to feed the cytoscape js plotter
    '''
    return [
        {'data':
            {
                'id':inte.id, 
                'source':inte.first.accession, 
                'target':inte.second.accession,
                'c':colour
            }
        }
        for inte in interaction_set
    ]

def get_complex_graph(request, complex_id):
    predicted_complex = get_object_or_404(PredictedComplex, pk=complex_id)
    experimental_interaction_set = predicted_complex.exp_interactions.all()
    inferred_interolog_set = predicted_complex.pred_interactions.all()
    protein_set = predicted_complex.proteins.all()
    d3 = defaultdict(list)
    nodes = [{'data':{'id':prot.accession}} for prot in protein_set]
    edges = get_interactions_dict(inferred_interolog_set, PREDICTED_INTERACTION_COLOUR)

    edges.extend(
        get_interactions_dict(
            experimental_interaction_set, 
            EXPERIMENTAL_INTERACTION_COLOUR
        )
    )
    d3['nodes'] = nodes
    d3['edges'] = edges

    mimetype = 'application/json'
    return HttpResponse(json.dumps(d3), mimetype)


def get_interologs_for_protein_set(protein_set):
    interologs = []
    interologs.extend(
        list(
            PredictedProteinInteraction.objects
            .filter(first__in=protein_set) 
            .filter(second__in=protein_set) 
        )
    )
    return interologs

def get_interactions_for_protein_set(protein_set):
    interactions = []
    interactions.extend(
        list(
            ExperimentalProteinInteraction.objects
            .filter(first__in=protein_set) 
            .filter(second__in=protein_set) 
        )
    )
    return interactions

def get_protein_graph(request, protein_accession):
    '''
    returns the data required to draw a graph with the requested protein as a centre
    '''
    data = 'fail'
    mimetype = 'application/json'
    logger.warning(protein_accession)
    protein = get_object_or_404(Protein, accession=protein_accession)
    interactions = ExperimentalProteinInteraction.objects.filter(Q(first=protein) | Q(second=protein))
    protein_set = set()
    accession_set = set()
    protein_set.add(protein)
    accession_set.add(protein.accession)
    for interaction in interactions:
        protein_set.add(interaction.first)
        protein_set.add(interaction.second)
        accession_set.add(interaction.first.accession)
        accession_set.add(interaction.second.accession)
        if len(protein_set) >= LIMITS["MAX_GRAPH_SIZE"]:
            break

    # if we still have space, look for more nodes.
    remaining_nodes = LIMITS["MAX_GRAPH_SIZE"] - len(protein_set)
    if remaining_nodes >= 1:
        interologs = PredictedProteinInteraction.objects.filter(Q(first=protein) | Q(second=protein)).filter(quality__gte=LIMITS["MIN_QUALITY"]).order_by("quality")[:remaining_nodes]
        for interolog in interologs:
            protein_set.add(interolog.first)
            protein_set.add(interolog.second)
            accession_set.add(interolog.first.accession)
            accession_set.add(interolog.second.accession)
    nodes = [{'data':{'id':prot.accession}} for prot in protein_set]
    secondary_interactions = get_interactions_for_protein_set(protein_set)
    secondary_interologs = get_interologs_for_protein_set(protein_set)
    #print 'we have'. len(secondary_interactions), 'secondary interactions'
    data = defaultdict(list)
    data['nodes'] = nodes
    data['edges'] = get_interactions_dict(secondary_interactions, EXPERIMENTAL_INTERACTION_COLOUR)
    data['edges'].extend(get_interactions_dict(secondary_interologs, PREDICTED_INTERACTION_COLOUR))
    return HttpResponse(json.dumps(data), mimetype)
