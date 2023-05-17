from django.core.management.base import BaseCommand
from django.conf import settings
from base.models import *
import logging

log = logging.getLogger("main")

STATIC_PATH = settings.STATIC_ROOT / 'downloads'


def write_complexes_cache() -> None:

    def write_complexes(qs, fn):
        with open(STATIC_PATH / fn, "w") as f:
            f.write("size,density,quality,pvalue,members\n")
            for i in complexes:
                f.write(",".join([
                    str(i.size),
                    str(i.density),
                    str(i.quality),
                    str(i.pvalue),
                    ";".join(p.accession for p in i.proteins.order_by("accession"))
                ]))
                f.write("\n")

    log.info("creating complexes cache")
    complexes = PredictedComplex.objects.order_by("-size")
    write_complexes(complexes, "complexes.csv")

    log.info("creating complexes cache (no trembl)")
    complexes_no_trembl = PredictedComplex.objects.filter(
        proteins__database=0).order_by("-size")
    write_complexes(complexes_no_trembl, "complexes-no-trembl.csv")


def write_interaction_cache(organism: Organism, cutoff: int) -> None:

    def write_interactions(qs, fn):
        with open(STATIC_PATH / fn, "w") as f:
            f.write("protein_1,protein_2,pubmed_id,detection_method,interaction_type\n")
            for i in qs:
                evs = i.evidence_set.all()
                for e in evs:
                    f.write(",".join([
                        i.first.accession,
                        i.second.accession,
                        str(e.pubmed_id),
                        str(e.detection_method.mi_id),
                        str(e.interaction_type.mi_id),
                    ]))
                    f.write("\n")

    log.info(f"Creating interaction cache for {organism.name}")
    interactions = ExperimentalProteinInteraction.objects.filter(taxon_id=organism).order_by("first__accession")
    write_interactions(interactions, f"interactions-{organism.taxon_id}.csv")

    log.info(f"Creating interaction cache for {organism.name} (no trembl)")
    interactions = ExperimentalProteinInteraction.objects.filter(taxon_id=organism, first__database=0, second__database=0).order_by("first__accession")
    write_interactions(interactions, f"interactions-{organism.taxon_id}-no-trembl.csv")


def write_interolog_cache(organism: Organism, cutoff: int) -> None:

    def write_interologs(qs, fn):
        with open(STATIC_PATH / fn, "w") as f:
            f.write("protein_1,protein_2,source_1,source_2,quality,homology_1_evalue,homology_2_evalue,homology_1_identity,homology_2_identity\n")
            for i in qs:
                f.write(",".join([
                    i.first.accession,
                    i.second.accession,
                    i.origin_experimental.first.accession,
                    i.origin_experimental.second.accession,
                    str(i.quality),
                    str(i.first_homology.evalue),
                    str(i.second_homology.evalue),
                    str(i.first_homology.percent_identity),
                    str(i.second_homology.percent_identity),
                ]))
                f.write("\n")

    log.info(f"Creating interolog cache for {organism.name}")
    interologs = PredictedProteinInteraction.objects.filter(taxon_id=organism).order_by("-quality")
    write_interologs(interologs, f"interologs-{organism.taxon_id}.csv")

    log.info(f"Creating interolog cache for {organism.name} (no trembl)")
    interologs = PredictedProteinInteraction.objects.filter(taxon_id=organism, first__database=0, second__database=0).order_by("-quality")
    write_interologs(interologs, f"interologs-{organism.taxon_id}-no-trembl.csv")


class Command(BaseCommand):
    args = "interactions_cutoff interologs_cutoff"
    
    def add_arguments(self, parser):
        parser.add_argument("interactions_cutoff")
        parser.add_argument("interologs_cutoff")
        
    def handle(self, *args, **options):
        # print("args", args)
        # if len(args) != 3:
        #     print "ARGUMENTS: ", Command.args
        #     raise CommandError("Argument error")

        interactions_cutoff, interologs_cutoff = options["interactions_cutoff"], options["interologs_cutoff"]

        STATIC_PATH.mkdir(exist_ok=True)

        log.info("Creating complexes cache")
        write_complexes_cache()
        # interactions and interologs are done per-organism
        organisms = Organism.objects.all()
        for organism in organisms:
            write_interaction_cache(organism, interactions_cutoff)
            write_interolog_cache(organism, interologs_cutoff)
