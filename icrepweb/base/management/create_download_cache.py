from django.core.management.base import BaseCommand
from django.contrib.staticfiles.storage import staticfiles_storage
from base.models import *

import os
import logging

log = logging.getLogger(__name__)


def write_complexes_cache():
    complexes = PredictedComplex.objects.all()
    
    for comp in complexes:

def write_interaction_cache(organism):
    pass

def write_interolog_cache(organism):
    pass


def create_download_cache():
    all_organisms = Organism.objects().all()
    for organism in all_organisms:

