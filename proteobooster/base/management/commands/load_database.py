from django.core.management.base import BaseCommand
from base.models import (GOTerm, MITerm, Organism, Protein,
                         GOAFunctionalAssignment, HomologyRelation,
                         ExperimentalProteinInteraction, Evidence,
                         PredictedProteinInteraction)
import logging


log = logging.getLogger("main")


def insert_goterm_table(obo_file):
    header_read = False
    bulk_buffer = []
    with open(obo_file) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, go_id, function, ontology = line.strip().split("\t")
            go_id = int(go_id)
            bulk_buffer.append(GOTerm(go_id=go_id,
                                      function=function,
                                      ontology=ontology))
    GOTerm.objects.bulk_create(bulk_buffer)


def insert_mi_ontology(mi_ontology):
    header_read = False
    bulk_buffer = []
    with open(mi_ontology) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, mi_id, desc = line.strip().split("\t")
            bulk_buffer.append(MITerm(mi_id=mi_id,
                                      description=desc))
    MITerm.objects.bulk_create(bulk_buffer)


def insert_organism(organisms_metada):
    header_read = False
    bulk_buffer = []
    with open(organisms_metada) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, taxon, name, domain = line.strip().split("\t")
            taxon = int(taxon)
            bulk_buffer.append(Organism(taxon_id=taxon,
                                        name=name,
                                        domain=domain))
    Organism.objects.bulk_create(bulk_buffer)


def insert_proteins(proteins_metadata):
    header_read = False
    bulk_buffer = []
    with open(proteins_metadata) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, acc, entry, desc, db, org_id, hei = line.strip().split("\t")
            db = int(db)
            org_id = Organism.objects.get(pk=int(org_id))
            bulk_buffer.append(Protein(accession=acc,
                                       entry_name=entry,
                                       description=desc,
                                       database=db,
                                       taxon_id=org_id,
                                       has_experimental_interactions=hei))
    Protein.objects.bulk_create(bulk_buffer)


def insert_go_annotations(functional_assignment):
    header_read = False
    bulk_buffer = []
    with open(functional_assignment) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            go_id, prot_id = line.strip().split("\t")
            go_id = GOTerm.objects.get(pk=int(go_id))
            prot_id = Protein.objects.get(pk=int(prot_id))
            bulk_buffer.append(GOAFunctionalAssignment(goterm=go_id,
                                                       protein=prot_id))
    GOAFunctionalAssignment.objects.bulk_create(bulk_buffer)


def insert_homologs(homologs):
    header_read = False
    bulk_buffer = []
    with open(homologs) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, source, target, eval, perc = line.strip().split("\t")
            source = Protein.objects.get(pk=int(source))
            target = Protein.objects.get(pk=int(target))
            eval = float(eval)
            perc = float(perc)
            bulk_buffer.append(HomologyRelation(source=source,
                                                target=target,
                                                evalue=eval,
                                                percent_identity=perc))
    HomologyRelation.objects.bulk_create(bulk_buffer)


def insert_interactions(interactions):
    header_read = False
    bulk_buffer = []
    with open(interactions) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, i_type, pb_id, p1, p2, org_id = line.strip().split("\t")
            i_type = int(i_type)
            pb_id = int(pb_id)
            p1 = Protein.objects.get(pk=int(p1))
            p2 = Protein.objects.get(pk=int(p2))
            org_id = Organism.objects.get(pk=int(org_id))
            bulk_buffer.append(ExperimentalProteinInteraction(
                first=p1, second=p2, icrep_id=pb_id,
                taxon_id=org_id, interaction_type=i_type))
    ExperimentalProteinInteraction.objects.bulk_create(bulk_buffer)


def insert_evidence(evidence):
    header_read = False
    bulk_buffer = []
    with open(evidence) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, pmed, d_t, i_t, supp = line.strip().split("\t")
            pmed = int(pmed)
            d_t = MITerm.objects.get(pk=int(d_t))
            i_t = MITerm.objects.get(pk=int(i_t))
            supp = ExperimentalProteinInteraction.objects.get(pk=int(supp))
            bulk_buffer.append(Evidence(pubmed_id=pmed,
                                        detection_method=d_t,
                                        interaction_type=i_t,
                                        interaction_supported=supp))
    Evidence.objects.bulk_create(bulk_buffer)


def insert_interologs(interologs):
    header_read = False
    bulk_buffer = []
    with open(interologs) as infile:
        for line in infile:
            if not header_read:
                header_read = True
                continue
            _, i_type, pb_id, p1, p2, org_id = line.strip().split("\t")
            i_type = int(i_type)
            pb_id = int(pb_id)
            p1 = Protein.objects.get(pk=int(p1))
            p2 = Protein.objects.get(pk=int(p2))
            org_id = Organism.objects.get(pk=int(org_id))
            bulk_buffer.append(PredictedProteinInteraction(
                first=p1, second=p2,
                taxon_id=org_id, interaction_type=i_type))
    PredictedProteinInteraction.objects.bulk_create(bulk_buffer)


def run(obo_file: str, mi_ontology: str, organisms_metadata: str,
        proteins_metadata: str, functional_assignment: str, homologs: str,
        interactions: str, evidence: str, interologs: str, complexes: str,
        complexes_interactions: str, complexes_interologs: str,
        overrep: str) -> None:
    #print(f"obo_file = {obo_file}")
    #insert_goterm_table(obo_file)
    #print(f"mi_ontology = {mi_ontology}")
    #insert_mi_ontology(mi_ontology)
    #print(f"organisms_metadata = {organisms_metadata}")
    #insert_organism(organisms_metadata)
    #print(f"proteins_metadata = {proteins_metadata}")
    #insert_proteins(proteins_metadata)
    #print(f"functional_assignment = {functional_assignment}")
    #insert_go_annotations(functional_assignment)
    #print(f"homologs = {homologs}")
    #insert_homologs(homologs)
    #print(f"interactions = {interactions}")
    #insert_interactions(interactions)
    #print(f"evidence = {evidence}")
    #insert_evidence(evidence)
    print(f"interologs = {interologs}")
    print(f"complexes = {complexes}")
    print(f"complexes_interactions = {complexes_interactions}")
    print(f"complexes_interologs = {complexes_interologs}")
    print(f"overrep = {overrep}")


class Command(BaseCommand):
    args = ("obo_file mi_ontology organisms_metadata proteins_metadata"
            " functional_assignment homologs interactions evidence interologs"
            " complexes complexes_interactions complexes_interologs overrep")

    def add_arguments(self, parser):
        # all of these files should be pre-parsed before passing it to this
        # command
        parser.add_argument("obo_file")
        parser.add_argument("mi_ontology")
        parser.add_argument("organisms_metadata")
        parser.add_argument("proteins_metadata")
        parser.add_argument("functional_assignment")
        parser.add_argument("homologs")
        parser.add_argument("interactions")
        parser.add_argument("evidence")
        parser.add_argument("interologs")
        parser.add_argument("complexes")
        parser.add_argument("complexes_interactions")
        parser.add_argument("complexes_interologs")
        parser.add_argument("overrep")

    def handle(self, *args, **options):
        obo_file = options["obo_file"]
        mi_ontology = options["mi_ontology"]
        organisms_metadata = options["organisms_metadata"]
        proteins_metadata = options["proteins_metadata"]
        functional_assignment = options["functional_assignment"]
        homologs = options["homologs"]
        interactions = options["interactions"]
        evidence = options["evidence"]
        interologs = options["interologs"]
        complexes = options["complexes"]
        complexes_interactions = options["complexes_interactions"]
        complexes_interologs = options["complexes_interologs"]
        overrep = options["overrep"]

        log.info("Loading files into database")
        run(obo_file, mi_ontology, organisms_metadata, proteins_metadata,
            functional_assignment, homologs, interactions, evidence,
            interologs, complexes, complexes_interactions,
            complexes_interologs, overrep)
