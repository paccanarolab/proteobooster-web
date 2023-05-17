from django.core.management.base import BaseCommand
import logging

log = logging.getLogger("main")


def run(obo_file: str, mi_ontology: str, organisms_metadata: str,
        proteins_metadata: str, functional_assignment: str, homologs: str,
        interactions: str, evidence: str, interologs: str, complexes: str,
        complexes_interactions: str, complexes_interologs: str,
        overrep: str) -> None:
    print(f"obo_file = {obo_file}")
    print(f"mi_ontology = {mi_ontology}")
    print(f"organisms_metadata = {organisms_metadata}")
    print(f"proteins_metadata = {proteins_metadata}")
    print(f"functional_assignment = {functional_assignment}")
    print(f"homologs = {homologs}")
    print(f"interactions = {interactions}")
    print(f"evidence = {evidence}")
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
