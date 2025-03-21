from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django import forms
from django.db.models import Q, Count
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings 
from .models import (Organism, Protein, ExperimentalProteinInteraction,
                     PredictedProteinInteraction, PredictedComplex)
import json
import logging
from collections import defaultdict

LIMITS = {
    "MAX_GRAPH_SIZE": 20,
    "MIN_QUALITY": 95,
    "MAX_ITEMS_LOAD": 20,
    "COMPLEX_MAX_SIZE": 100,
}

DEFAULTS = {
    "include_trembl": True
}

INSTANCE_ORG_ID = settings.PROTEOBOOSTER_ORG_ID

logger = logging.getLogger(__name__)

TOOLTIPS = {
    'interaction': 'Interactions supported by experimental evidence published'
                   ' in peer-reviewed articles.',
    'sibling-interaction': 'Sibling experimental interactions are those who'
                           ' could have been the source of this interaction.'
                           ' This is, if evidence was not available, this'
                           ' would have been an interolog.',
    'interolog': 'Inferred interactions based on the similarity of the'
                 ' proteins with existent interactions. Please go to'
                 ' <a href="https://www.ncbi.nlm.nih.gov/pubmed/15173116">Yu'
                 ' et al., 2004 <i class="fa fa-external-link"></i></a> for'
                 ' further details.',
    'complex': 'Inferred protein complexes. Computed using The'
               ' <a href="http://www.paccanarolab.org/cluster-one/">ClusterONE'
               ' <i class="fa fa-external-link"></i></a> algorithm.',
    'evidence': 'Published papers that back up the experimental interaction.',
    'source-interaction': 'The experimental interaction that was used to infer'
                          ' this interolog.'
}


def batch_qs(qs, batch_size=2000):
    next = True
    start = 0
    n = 0
    while next:
        next = qs[start:start+batch_size].count() >= batch_size
        start += batch_size
        for item in qs[start:start+batch_size]:
            yield item
        n += 1


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# taken from https://docs.djangoproject.com/en/2.0/howto/outputting-csv/#streaming-large-csv-files
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


# Create your views here.
class HomePageForm(forms.Form):
    protein_accession = forms.CharField(required=True)
    protein_display = forms.CharField(required=True)


def home(request):
    context = {}
    include_trembl = request.GET.get('include_trembl', 'true') != 'false'
    context['include_trembl'] = include_trembl
    complex_qs = PredictedComplex.objects.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"])
    protein_qs = Protein.objects.filter(taxon_id=INSTANCE_ORG_ID)
    interactions_qs = ExperimentalProteinInteraction.objects.filter(
        taxon_id=INSTANCE_ORG_ID)
    interolog_qs = PredictedProteinInteraction.objects.filter(
        taxon_id=INSTANCE_ORG_ID)
    if not include_trembl:
        complex_qs = complex_qs.filter(proteins__database=0)
        protein_qs = protein_qs.filter(database=0)
        interactions_qs = interactions_qs.filter(first__database=0,
                                                 second__database=0)
        interolog_qs = interolog_qs.filter(first__database=0,
                                           second__database=0)
    context["count_complexes"] = complex_qs.count()
    context["count_proteins"] = protein_qs.count()
    context["count_interactions"] = interactions_qs.count()
    context["count_interologs"] = interolog_qs.count()
    context["organism"] = Organism.objects.get(pk=INSTANCE_ORG_ID)

    # source counts
    context["count_organisms"] = Organism.objects.count() - 1
    if include_trembl:
        context["count_source_proteins"] = Protein.objects.filter(
            ~Q(taxon_id=INSTANCE_ORG_ID)).count()
        context["count_source_interactions"] = (
            ExperimentalProteinInteraction.objects.filter(
                ~Q(taxon_id=INSTANCE_ORG_ID)).count())
    else:
        context["count_source_proteins"] = Protein.objects.filter(
            ~Q(taxon_id=INSTANCE_ORG_ID) & Q(database=0)).count()
        context["count_source_interactions"] = (
            ExperimentalProteinInteraction.objects
            .filter(
                ~Q(taxon_id=INSTANCE_ORG_ID),
                first__database=0,
                second__database=0)
            .count())

    if request.method == "POST":
        home_form = HomePageForm(request.POST)
        if home_form.is_valid():
            url = f"protein/{home_form.cleaned_data['protein_accession']}/"
            return redirect(url)
        else:
            logger.warning("this is NOT valid")
    return render(request, "home.html", context)


def downloads(request):
    data = {
        'active': 'downloads',
        'title': 'ProteoBooster | Downloads'
    }
    return render(request, "downloads.html", data)


def about(request):
    data = {
        'active': 'about',
        'title': 'ProteoBooster | About'
    }
    return render(request, "about.html", data)


def proteins(request, organism_taxon_id):
    n = LIMITS["MAX_ITEMS_LOAD"]
    context = {}
    include_trembl = request.GET.get('include_trembl', 'true') != 'false'
    context['include_trembl'] = include_trembl
    context["defaults"] = DEFAULTS
    protein_qs = Protein.objects
    if not include_trembl:
        protein_qs = protein_qs.filter(database=0)

    if organism_taxon_id == 0:
        context["organism"] = "all"
    else:
        organism = get_object_or_404(Organism, taxon_id=organism_taxon_id)
        protein_qs = protein_qs.filter(taxon_id=organism)
        context["organism"] = organism
    protein_counts = protein_qs.count()
    context["protein_counts"] = protein_counts
    context["proteins"] = protein_qs.order_by("accession")[:n]
    context["load_more_proteins"] = protein_counts > n
    return render(request, "all_proteins.html", context)


def protein(request, protein_accession):
    protein = get_object_or_404(Protein, accession=protein_accession)
    interaction_list = []
    interolog_list = []
    context = dict()
    context['tooltips'] = TOOLTIPS
    interaction_list = ExperimentalProteinInteraction.objects.filter(
        Q(first=protein) | Q(second=protein))[:LIMITS["MAX_ITEMS_LOAD"]]
    context['interaction_count'] = \
        ExperimentalProteinInteraction.objects.filter(
            Q(first=protein) | Q(second=protein)).count()
    context['load_more_interactions'] = \
        context['interaction_count'] > LIMITS["MAX_ITEMS_LOAD"]
    interolog_list = PredictedProteinInteraction.objects.filter(
        (Q(first=protein) | Q(second=protein))
    ).order_by('-quality')[:LIMITS["MAX_ITEMS_LOAD"]]
    context['interolog_count'] = PredictedProteinInteraction.objects.filter(
        (Q(first=protein) | Q(second=protein))).count()
    context['load_more_interologs'] = \
        context['interolog_count'] > LIMITS["MAX_ITEMS_LOAD"]

    predicted_complex_set = protein.predictedcomplex_set.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"]
    ).order_by("-quality")[:LIMITS["MAX_ITEMS_LOAD"]]
    context['complex_count'] = protein.predictedcomplex_set.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"]).count()
    context['load_more_complexes'] = \
        context['complex_count'] > LIMITS["MAX_ITEMS_LOAD"]
    go_term_set = protein.goa_assigned_goterms.all()[:LIMITS["MAX_ITEMS_LOAD"]]
    go_term_list = list(go_term_set)
    context['goterm_count'] = protein.goa_assigned_goterms.count()
    context['load_more_goterms'] = \
        context['goterm_count'] > LIMITS["MAX_ITEMS_LOAD"]
    context["protein"] = protein
    context["experimental_interaction_list"] = interaction_list
    context["inferred_interolog_list"] = interolog_list
    context["predicted_complex_list"] = predicted_complex_set
    context["go_term_list"] = go_term_list
    context["activity"] = 'protein'
    return render(request, "protein.html", context)


def organism_download_interactions(request, organism_taxon_id):
    include_trembl = request.GET.get('include_trembl', 'true') != 'false'
    if not include_trembl:
        return redirect(staticfiles_storage.url(f'downloads/interactions-{organism_taxon_id}-no-trembl.csv'))
    return redirect(staticfiles_storage.url(f'downloads/interactions-{organism_taxon_id}.csv'))


def organism_download_interologs(request, organism_taxon_id):
    include_trembl = request.GET.get('include_trembl', 'true') != 'false'
    if not include_trembl:
        return redirect(staticfiles_storage.url(f'downloads/inteorlogs-{organism_taxon_id}-no-trembl.csv'))
    return redirect(staticfiles_storage.url(f'downloads/inteorlogs-{organism_taxon_id}.csv'))


def organism_download_complexes(request, organism_taxon_id):
    include_trembl = request.GET.get('include_trembl', 'true') != 'false'
    if not include_trembl:
        return redirect(staticfiles_storage.url('downloads/complexes-no-trembl.csv'))
    return redirect(staticfiles_storage.url('downloads/complexes.csv'))


def organism(request, organism_taxon_id):
    organism = get_object_or_404(Organism, taxon_id=organism_taxon_id)
    data = dict()
    data['tooltips'] = TOOLTIPS
    data['include_trembl'] = include_trembl = request.GET.get(
        'include_trembl', 'true') != 'false'

    protein_qs = organism.protein_set.only("accession")
    if include_trembl:
        protein_qs = protein_qs.all()
    else:
        protein_qs = protein_qs.filter(database=0)
    data['protein_count'] = protein_qs.count()
    data['load_more_proteins'] = data['protein_count'] > LIMITS["MAX_ITEMS_LOAD"]
    data['organism'] = organism
    data['protein_list'] = protein_qs.order_by(
        "accession")[:LIMITS["MAX_ITEMS_LOAD"]]

    interactions_qs = (ExperimentalProteinInteraction.objects
                       .only('first__accession', 'second__accession')
                       .filter(taxon_id=organism))
    if not include_trembl:
        interactions_qs = interactions_qs.filter(
            first__database=0, second__database=0)
    data['interaction_count'] = interactions_qs.count()
    data['experimental_interaction_list'] = interactions_qs.order_by(
        "first__accession")[:LIMITS["MAX_ITEMS_LOAD"]]
    data['load_more_interactions'] = data['interaction_count'] > LIMITS["MAX_ITEMS_LOAD"]

    interolog_qs = PredictedProteinInteraction.objects.only(
        'first__accession', 'second__accession', 'quality').filter(taxon_id=organism)
    if not include_trembl:
        interolog_qs = interolog_qs.filter(
            taxon_id=organism, first__database=0, second__database=0)
    data["interolog_count"] = interolog_qs.count()
    data['inferred_interolog_list'] = interolog_qs.order_by(
        '-quality')[:LIMITS["MAX_ITEMS_LOAD"]]
    data['load_more_interologs'] = data['interolog_count'] > LIMITS["MAX_ITEMS_LOAD"]

    # complexes
    if organism.taxon_id == INSTANCE_ORG_ID:
        complex_qs = PredictedComplex.objects.filter(
            size__lte=LIMITS["COMPLEX_MAX_SIZE"])
        if not include_trembl:
            complex_qs = complex_qs.filter(proteins__database=0)
        data['complex_count'] = complex_qs.count()
        data["predicted_complexes"] = complex_qs.order_by(
            '-size')[:LIMITS["MAX_ITEMS_LOAD"]]
        data['load_more_complexes'] = data['complex_count'] > LIMITS["MAX_ITEMS_LOAD"]

    return render(request, "organism.html", data)


def organisms(request):
    context = {}
    context['include_trembl'] = request.GET.get(
        'include_trembl', 'true') != 'false'
    context["organisms"] = Organism.objects.filter(~Q(pk=INSTANCE_ORG_ID)).annotate(
        num_proteins=Count('protein')).order_by("-num_proteins").all()
    context["domain_dict"] = {k: v for k, v in Organism.DOMAINS}
    return render(request, "all_organisms.html", context)


def interaction(request, first_accession, second_accession):
    data = dict()
    data['tooltips'] = TOOLTIPS
    first = get_object_or_404(Protein, accession=first_accession)
    second = get_object_or_404(Protein, accession=second_accession)
    experimental_interaction = get_object_or_404(
        ExperimentalProteinInteraction, (Q(first=first) & Q(second=second)))
    evidence_set = experimental_interaction.evidence_set.all()[:10]
    evidence_list = list(evidence_set)
    data['evidence_count'] = experimental_interaction.evidence_set.count()
    data['load_more_evidence'] = data['evidence_count'] > 10

    experimental_interaction_inferred_interolog_set = experimental_interaction.predictedproteininteraction_set.all(
    ).order_by('-quality')[:10]
    experimental_interaction_inferred_interolog_list = list(
        experimental_interaction_inferred_interolog_set)
    data['interolog_count'] = experimental_interaction.predictedproteininteraction_set.count()
    data['load_more_interologs'] = data['interolog_count'] > 10

    interologs_with_same_interactors_set = PredictedProteinInteraction.objects.filter(
        (Q(first=experimental_interaction.first) & Q(second=experimental_interaction.second)) |
        (Q(second=experimental_interaction.first) &
         Q(first=experimental_interaction.second))
    )[:10]

    data['sibling_interaction_count'] = PredictedProteinInteraction.objects.filter(
        (Q(first=experimental_interaction.first) & Q(second=experimental_interaction.second)) |
        (Q(second=experimental_interaction.first) &
         Q(first=experimental_interaction.second))
    ).count()
    data['load_more_interactions'] = data['sibling_interaction_count'] > 10

    sibling_experimental_interaction_list = []
    for interolog_with_same_interactor in interologs_with_same_interactors_set:
        sibling_experimental_interaction_list.append(
            interolog_with_same_interactor.origin_experimental)

    predicted_complex_list = []
    predicted_complex_set = experimental_interaction.predictedcomplex_set.filter(
        size__lte=80)[:10]
    data['complex_count'] = experimental_interaction.predictedcomplex_set.count()
    data['load_more_complexes'] = data['complex_count'] > 10
    for predicted_complex in predicted_complex_set:
        predicted_complex_protein_set = predicted_complex.proteins.all()[:10]
        predicted_complex_protein_list = list(predicted_complex_protein_set)
        predicted_complex_list.append(
            [predicted_complex.id, predicted_complex_protein_list, predicted_complex.size])
    data["experimental_interaction"] = experimental_interaction
    data["evidence_list"] = evidence_list
    data["inferred_interolog_list"] = experimental_interaction_inferred_interolog_list
    data["sibling_experimental_interaction_list"] = sibling_experimental_interaction_list
    data["predicted_complex_list"] = predicted_complex_list
    return render(request, "interaction.html", data)


def interolog(request, first_accession, second_accession):
    data = dict()
    data['tooltips'] = TOOLTIPS
    first = get_object_or_404(Protein, accession=first_accession)
    second = get_object_or_404(Protein, accession=second_accession)
    inferred_interolog = get_object_or_404(
        PredictedProteinInteraction,
        ((Q(first=first) & Q(second=second))
         | (Q(second=first) & Q(first=second)))
        & Q(is_best=True))
    source_exp_intera_set = set()

    interologs_with_same_interactors_set = (
        PredictedProteinInteraction.objects.filter(
            (Q(first=inferred_interolog.first)
             & Q(second=inferred_interolog.second))
            | (Q(second=inferred_interolog.first)
               & Q(first=inferred_interolog.second))
            ).order_by('-quality')[:10])

    data['interaction_count'] = PredictedProteinInteraction.objects.filter(
        (Q(first=inferred_interolog.first)
         & Q(second=inferred_interolog.second))
        | (Q(second=inferred_interolog.first)
           & Q(first=inferred_interolog.second))).count()
    data['load_more_interactions'] = data['interaction_count'] > 10

    # TODO: ask Alfonso whether sibling interologs are interesting
    # wsi stands for "with same interactor"
    for interolog_wsi in interologs_with_same_interactors_set:
        source_experimental_interaction = interolog_wsi.origin_experimental
        source_exp_intera_set.add((
            source_experimental_interaction,
            interolog_wsi.quality))
    predicted_complex_list = []
    predicted_complex_set = inferred_interolog.predictedcomplex_set.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"])[:10]
    data['complex_count'] = inferred_interolog.predictedcomplex_set.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"]).count()
    data['load_more_complexes'] = data['complex_count'] > 10
    for predicted_complex in predicted_complex_set:
        predicted_complex_protein_set = predicted_complex.proteins.all()[:10]
        predicted_complex_protein_list = list(predicted_complex_protein_set)
        predicted_complex_list.append(
            [predicted_complex.id,
             predicted_complex_protein_list,
             predicted_complex.size])
    data["inferred_interolog"] = inferred_interolog
    data["source_experimental_interaction_list"] = sorted(
        list(source_exp_intera_set),
        key=lambda x: x[1],
        reverse=True
    )
    data["predicted_complex_list"] = predicted_complex_list
    return render(request, "interolog.html", data)


def complex(request, predicted_complex_id):
    predicted_complex = get_object_or_404(
        PredictedComplex, pk=predicted_complex_id)
    protein_set = predicted_complex.proteins.all()
    context = {}
    context['tooltips'] = TOOLTIPS
    context['include_trembl'] = request.GET.get(
        'include_trembl', 'true') != 'false'
    context["predicted_complex"] = predicted_complex
    context["protein_list"] = predicted_complex.proteins.order_by("accession")[
        :LIMITS["MAX_ITEMS_LOAD"]]
    context["protein_count"] = predicted_complex.proteins.count()
    context["load_more_proteins"] = context["protein_count"] > LIMITS["MAX_ITEMS_LOAD"]
    context["experimental_interaction_list"] = predicted_complex.exp_interactions.order_by(
        "first__accession")[:LIMITS["MAX_ITEMS_LOAD"]]
    context["interaction_count"] = predicted_complex.exp_interactions.count()
    context["load_more_interactions"] = context["interaction_count"] > LIMITS["MAX_ITEMS_LOAD"]
    context["inferred_interolog_list"] = predicted_complex.pred_interactions.order_by(
        "-quality")[:LIMITS["MAX_ITEMS_LOAD"]]
    context['interolog_count'] = predicted_complex.pred_interactions.count()
    context["load_more_interologs"] = context["interolog_count"] > LIMITS["MAX_ITEMS_LOAD"]
    context["complex_functional_assignment_list"] = predicted_complex.complexfunctionalassignment_set.order_by("pvalue")[
        :LIMITS["MAX_ITEMS_LOAD"]]
    context["goterm_count"] = predicted_complex.complexfunctionalassignment_set.count()
    context["load_more_goterms"] = context["goterm_count"] > LIMITS["MAX_ITEMS_LOAD"]
    return render(request, "predicted_complex.html", context)


def complexes(request):
    n = LIMITS["MAX_ITEMS_LOAD"]
    context = {}
    context['include_trembl'] = include_trembl = request.GET.get(
        'include_trembl', 'true') != 'false'
    complex_qs = PredictedComplex.objects.filter(
        size__lte=LIMITS["COMPLEX_MAX_SIZE"])
    if not include_trembl:
        complex_qs = complex_qs.filter(proteins__database=0)
    complex_count = complex_qs.count()
    context["complexes"] = complex_qs.order_by("-size")[:n]
    context["load_more_complexes"] = complex_count > n
    return render(request, "all_complexes.html", context)


def go_term(request, go_term_goid):
    return render(request, "home.html")

# API


def get_proteins(request):
    data = "fail"
    if request.method == "GET":
        include_trembl = request.GET.get('include_trembl', 'true') != 'false'
        query = request.GET.get("term", "")
        protein_qs = Protein.objects
        if not include_trembl:
            protein_qs = protein_qs.filter(database=0)
        proteins = protein_qs.filter(
            Q(accession__icontains=query) |
            Q(entry_name__icontains=query)
        ).order_by("accession")[:LIMITS["MAX_ITEMS_LOAD"]]
        proteins = proteins.values_list("accession", "entry_name")
        res = []
        for accession, entry_name in proteins:
            item = {"elem": accession}
            if entry_name.strip():
                item["display"] = f"{accession} - {entry_name}"
            else:
                item["display"] = accession
            res.append(item)
        data = json.dumps(res)
    mimetype = "application/json"
    return HttpResponse(data, content_type=mimetype)


def load_more_proteins(request, limit, offset):
    data = "fail"
    Protein.objects.all().order_by("accession")
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
                'id': inte.id,
                'source': inte.first.accession,
                'target': inte.second.accession,
                'c': colour
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
    nodes = [{'data': {'id': prot.accession}} for prot in protein_set]
    edges = get_interactions_dict(
        inferred_interolog_set, PREDICTED_INTERACTION_COLOUR)

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
    protein = get_object_or_404(Protein, accession=protein_accession)
    interactions = ExperimentalProteinInteraction.objects.filter(
        Q(first=protein) | Q(second=protein))
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
        # interologs = PredictedProteinInteraction.objects.filter(Q(first=protein) | Q(second=protein)).filter(quality__gte=LIMITS["MIN_QUALITY"]).order_by("quality")[:remaining_nodes]
        interologs = PredictedProteinInteraction.objects.filter(
            Q(first=protein) | Q(second=protein)).order_by("quality")[:remaining_nodes]
        for interolog in interologs:
            protein_set.add(interolog.first)
            protein_set.add(interolog.second)
            accession_set.add(interolog.first.accession)
            accession_set.add(interolog.second.accession)
    nodes = [{'data': {'id': prot.accession}} for prot in protein_set]
    secondary_interactions = get_interactions_for_protein_set(protein_set)
    secondary_interologs = get_interologs_for_protein_set(protein_set)
    # print 'we have'. len(secondary_interactions), 'secondary interactions'
    data = defaultdict(list)
    data['nodes'] = nodes
    data['edges'] = get_interactions_dict(
        secondary_interactions, EXPERIMENTAL_INTERACTION_COLOUR)
    data['edges'].extend(get_interactions_dict(
        secondary_interologs, PREDICTED_INTERACTION_COLOUR))
    return HttpResponse(json.dumps(data), mimetype)

# LOAD MORE API


# the maximum amount of stuff that can be included in a single request to the "load more" API
MAX_LIMIT_RANGE = 40


def api_lm_interolog(request):
    '''
    returns a json which encodes the requested fields 
    from interologs
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - a protein
        #   - an experimental interaction
        #   - an organism
        if filt == 'protein':
            protein_id = int(request.GET.get('element_id', 0))
            protein = get_object_or_404(Protein, pk=protein_id)
            interolog_set = PredictedProteinInteraction.objects.filter(
                Q(first=protein) | Q(second=protein)).order_by('-quality')[offset:offset+limit]
        elif filt == 'exp_int':
            experimental_interaction_id = int(request.GET.get('element_id', 0))
            experimental_interaction = get_object_or_404(
                ExperimentalProteinInteraction, pk=experimental_interaction_id)
            interolog_set = experimental_interaction.predictedproteininteraction_set.all(
            ).order_by('-quality')[offset:offset+limit]
        elif filt == 'organism':
            organism_id = int(request.GET.get('element_id', 0))
            organism = get_object_or_404(Organism, pk=organism_id)
            interolog_set = PredictedProteinInteraction.objects.filter(
                taxon_id=organism).order_by('-quality')[offset:offset+limit]
        elif filt == "complex":
            complex_id = int(request.GET.get("element_id", 0))
            predicted_complex = get_object_or_404(
                PredictedComplex, pk=complex_id)
            interolog_set = predicted_complex.pred_interactions.order_by(
                "-quality")[offset:offset+limit]
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        interolog_list = []
        for interolog in interolog_set:
            interolog_list.append(
                {
                    'id': interolog.id,
                    'first': interolog.first.accession,
                    'second': interolog.second.accession,
                    'first_description': interolog.first.description,
                    'second_description': interolog.second.description,
                    'quality': '{0:.2f}'.format(interolog.quality),
                    'organism_name': interolog.taxon_id.name
                }
            )

        data = json.dumps(interolog_list)
    return HttpResponse(data, mimetype)


def api_lm_complex(request):
    '''
    returns a json which encodes the requested fields 
    from a protein complex
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        include_trembl = request.GET.get('include_trembl', 'true') != 'false'
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - a protein
        #   - an experimental interaction
        #   - a predicted interaction
        #   - an organism
        #   - a GO term
        if filt == 'protein':
            protein_id = int(request.GET.get('element_id', 0))
            protein = get_object_or_404(Protein, pk=protein_id)
            complex_set = protein.predictedcomplex_set.filter(
                size__lte=LIMITS["COMPLEX_MAX_SIZE"])[offset:offset+limit]
        elif filt == 'exp_int':
            experimental_interaction_id = int(request.GET.get('element_id', 0))
            experimental_interaction = get_object_or_404(
                ExperimentalProteinInteraction, pk=experimental_interaction_id)
            complex_set = experimental_interaction.predictedcomplex_set.filter(
                size__lte=LIMITS["COMPLEX_MAX_SIZE"])[offset:offset+limit]
        elif filt == 'interolog':
            interolog_id = int(request.GET.get('element_id', 0))
            interolog = get_object_or_404(
                PredictedProteinInteraction, pk=interolog_id)
            complex_set = interolog.predictedcomplex_set.filter(
                size__lte=LIMITS["COMPLEX_MAX_SIZE"])[offset:offset+limit]
        elif filt == 'organism':
            # complexes are only listed for the target organism, so the taxon id column is no longer present in the complexes
            # therefore, this filter simply returns all complexes in the database
            if include_trembl:
                complex_set = PredictedComplex.objects.filter(
                    size__lte=LIMITS["COMPLEX_MAX_SIZE"]).order_by("-size")[offset:offset+limit]
            else:
                complex_set = PredictedComplex.objects.filter(
                    size__lte=LIMITS["COMPLEX_MAX_SIZE"],
                    protins__database=0).order_by('-size')[offset:offset+limit]
        elif filt == 'goterm':
            # this is a special case because we have to go through the
            # ComplexFunctionalAssignment model as opposed to just
            # the PredictedComplex, which adds a little layer of abstraction
            # in order to get the information we need for the UI
            go_term_id = int(request.GET.get('element_id', 0))
            go_term = get_object_or_404(GOTerm, pk=go_term_id)
            complex_functional_assignment_set = go_term.complexfunctionalassignment_set.all()[
                offset:offset+limit]
            predicted_complex_list = []
            for complex_functional_assignment in complex_functional_assignment_set:
                predicted_complex = complex_functional_assignment.complex
                predicted_complex_protein_set = predicted_complex.proteins.all()
                predicted_complex_protein_list = [
                    p.accession for p in predicted_complex_protein_set]
                predicted_complex_list.append(
                    {
                        'pvalue': '{0:.4g}'.format(complex_functional_assignment.pvalue),
                        'id': predicted_complex.id,
                        'size': predicted_complex.size,
                        'proteins': predicted_complex_protein_list
                    })
            data = json.dumps(predicted_complex_list)
            return HttpResponse(data, mimetype)
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        predicted_complex_list = []
        for predicted_complex in complex_set:
            predicted_complex_protein_set = predicted_complex.proteins.all()
            predicted_complex_protein_list = [
                p.accession for p in predicted_complex_protein_set]
            predicted_complex_list.append(
                {
                    'id': predicted_complex.id,
                    'size': predicted_complex.size,
                    'quality': predicted_complex.quality,
                    'proteins': predicted_complex_protein_list,
                }
            )

        data = json.dumps(predicted_complex_list)
    return HttpResponse(data, mimetype)


def api_lm_protein(request):
    '''
    returns a json which encodes the requested fields 
    from proteins
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        include_trembl = request.GET.get('include_trembl', 'true') != "false"
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - an organism
        #   - a goterm
        #   - a complex
        elif filt == 'organism':
            organism_id = int(request.GET.get('element_id', 0))
            protein_qs = Protein.objects
            if not include_trembl:
                protein_qs = protein_qs.filter(database=0)
            if organism_id != 0:
                organism = get_object_or_404(Organism, pk=organism_id)
                protein_qs = protein_qs.filter(taxon_id=organism)
            protein_set = protein_qs.order_by("accession")[offset:offset+limit]
        elif filt == 'goterm':
            go_term_id = int(request.GET.get('element_id', 0))
            go_term = get_object_or_404(GOTerm, pk=go_term_id)
            if include_trembl:
                protein_set = go_term.protein_set.all().order_by("accession")[
                    offset:offset+limit]
            else:
                protein_set = go_term.protein_set.filter(database=0).order_by("accession")[
                    offset:offset+limit]
        elif filt == 'complex':
            complex_id = int(request.GET.get('element_id', 0))
            predicted_complex = get_object_or_404(
                PredictedComplex, pk=complex_id)
            if include_trembl:
                protein_set = predicted_complex.proteins.all().order_by("accession")[
                    offset:offset+limit]
            else:
                protein_set = predicted_complex.proteins.filter(
                    database=0).order_by("accession")[offset:offset+limit]
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        protein_list = []
        for protein in protein_set:
            protein_list.append(
                {
                    'id': protein.id,
                    'accession': protein.accession,
                    'entry_name': protein.entry_name,
                    'description': protein.description,
                }
            )

        data = json.dumps(protein_list)
    return HttpResponse(data, mimetype)


def api_lm_interaction(request):
    '''
    returns a json which encodes the requested fields 
    from interologs
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - a protein
        #   - an interolog
        #   - an organism
        if filt == 'protein':
            protein_id = int(request.GET.get('element_id', 0))
            protein = get_object_or_404(Protein, pk=protein_id)
            interaction_set = ExperimentalProteinInteraction.objects.filter(
                Q(first=protein) | Q(second=protein))[offset:offset+limit]
        elif filt == 'exp_int':
            experimental_interaction_id = int(request.GET.get('element_id', 0))
            experimental_interaction = get_object_or_404(
                ExperimentalProteinInteraction, pk=experimental_interaction_id)
            interologs_with_same_interactors_set = PredictedProteinInteraction.objects.filter(
                (Q(first=experimental_interaction.first) & Q(second=experimental_interaction.second)) |
                (Q(second=experimental_interaction.first) &
                 Q(first=experimental_interaction.second))
            )[offset:offset+limit]
            interaction_set = []
            for interolog_with_same_interactor in interologs_with_same_interactors_set:
                interaction_set.append(
                    interolog_with_same_interactor.origin_experimental)
        elif filt == 'interolog':
            # this is a special case, as the list of interactions for an interolog refer to experimental
            # interactions that sourced interologs with the same interacting proteins, and so they're considered
            # as additional sources for the current interolog
            interolog_id = int(request.GET.get('element_id', 0))
            interolog = get_object_or_404(
                PredictedProteinInteraction, pk=interolog_id)
            source_experimental_interaction_set = set()
            interolog_with_same_interactors_set = PredictedProteinInteraction.objects.filter(
                (Q(first=interolog.first) & Q(second=interolog.second)) |
                (Q(second=interolog.first) & Q(first=interolog.second))
            ).order_by('-quality')[offset:offset+limit]
            for interolog_with_same_interactors in interolog_with_same_interactors_set:
                source_experimental_interaction = interolog_with_same_interactors.origin_experimental
                source_experimental_interaction_set.add((
                    source_experimental_interaction,
                    interolog_with_same_interactors.quality))
            interaction_list = []
            for interaction in source_experimental_interaction_set:
                interaction_list.append(
                    {
                        'id': interaction[0].id,
                        'first': interaction[0].first.accession,
                        'second': interaction[0].second.accession,
                        'first_description': interaction[0].first.description,
                        'second_description': interaction[0].second.description,
                        'quality': '{0:.2f}'.format(interaction[1]),
                        'organism_name': interaction[0].taxon_id.name
                    }
                )

            data = json.dumps(interaction_list)
            return HttpResponse(data, mimetype)

        elif filt == 'organism':
            organism_id = int(request.GET.get('element_id', 0))
            organism = get_object_or_404(Organism, pk=organism_id)
            interaction_set = ExperimentalProteinInteraction.objects.filter(taxon_id=organism)[
                offset:offset+limit]
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        interaction_list = []
        for interaction in interaction_set:
            interaction_list.append(
                {
                    'id': interaction.id,
                    'first': interaction.first.accession,
                    'second': interaction.second.accession,
                    'first_description': interaction.first.description,
                    'second_description': interaction.second.description,
                    'organism_name': interaction.taxon_id.name
                }
            )

        data = json.dumps(interaction_list)
    return HttpResponse(data, mimetype)


def api_lm_goterm(request):
    '''
    returns a json which encodes the requested fields 
    from GO terms
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - a protein
        #   - a complex
        if filt == 'protein':
            protein_id = int(request.GET.get('element_id', 0))
            protein = get_object_or_404(Protein, pk=protein_id)
            go_term_set = protein.goa_assigned_goterms.all()[
                offset:offset+limit]
        elif filt == 'complex':
            complex_id = int(request.GET.get('element_id', 0))
            predicted_complex = get_object_or_404(
                PredictedComplex, pk=complex_id)
            go_term_set = predicted_complex.complexfunctionalassignment_set.all()[
                offset:offset+limit]
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        go_term_list = []
        for go_term in go_term_set:
            go_term_list.append(
                {
                    'id': go_term.id,
                    'go_id': go_term.go_id,
                    'function': go_term.function,
                }
            )

        data = json.dumps(go_term_list)
    return HttpResponse(data, mimetype)


def api_lm_evidence(request):
    '''
    returns a json which encodes the requested fields 
    from interologs
    '''
    data = 'fail'
    mimetype = 'application/json'
    if is_ajax(request):
        filt = request.GET.get('filter', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 0))
        if limit > MAX_LIMIT_RANGE:
            data = 'fail: please limit your requests to ' + \
                str(MAX_LIMIT_RANGE) + ' elements or less'
            return HttpResponse(data, mimetype)

        # the filter can refer to either
        #   - a protein
        #   - an experimental interaction
        #   - an organism
        if filt == 'protein':
            protein_id = int(request.GET.get('protein_id', 0))
            protein = get_object_or_404(Protein, pk=protein_id)
            interolog_set = PredictedProteinInteraction.objects.filter(
                Q(first=protein) | Q(second=protein))[offset:offset+limit]
        elif filt == 'exp_int':
            experimental_interaction_id = int(request.GET.get('element_id', 0))
            experimental_interaction = get_object_or_404(
                ExperimentalProteinInteraction, pk=experimental_interaction_id)
            evidence_set = experimental_interaction.evidence_set.all()[
                offset:offset+limit]
        elif filt == 'organism':
            organism_id = int(request.GET.get('organism_id', 0))
            organism = get_object_or_404(Organism, pk=organism_id)
            interolog_set = PredictedProteinInteraction.objects.filter(taxon_id=organism)[
                offset:offset+limit]
        else:
            data = 'fail: wrong filter'
            return HttpResponse(data, mimetype)
        evidence_list = []
        for evidence in evidence_set:
            evidence_list.append(
                {
                    'id': evidence.id,
                    'pubmed_id': evidence.pubmed_id,
                    'interaction_type': evidence.interaction_type,
                    'detection_method': evidence.detection_method
                }
            )

        data = json.dumps(evidence_list)
    return HttpResponse(data, mimetype)
