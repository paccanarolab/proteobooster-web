from django.db import models

# Create your models here.
class GOTerm(models.Model):
    """ GO terms contain information about the `go_id`, the description of
        the `function`, the sub-`ontology` it belongs to (bp, mf or cc) or
        the `release` it belongs to.
    """
    GO_ONTOLOGIES = (('bp', 'Biological Process'), ('mf', 'Molecular Function'), ('cc', 'Cellular component'))
    go_id = models.IntegerField()
    function = models.CharField(max_length=300)
    ontology = models.CharField(max_length=2, choices=GO_ONTOLOGIES)

    def print_go_id(self):
        return "GO:{0:07d}".format(self.go_id)


class Organism(models.Model):
    """ An organism is identified by its `taxon_id` and its
        `name` (scientific name). 
    """
    DOMAINS = (('a', 'Archaea'), ('b', 'Bacteria'), ('e', 'Eukaryota'), ('v', 'Viridae'))
    taxon_id = models.PositiveIntegerField()
    name = models.CharField(db_index=True, max_length=150)
    domain = models.CharField(max_length=1, choices=DOMAINS)


class Protein(models.Model):
    """ A protein is a UniProtKB sequence identified by the `accession`
        and the `entry_name`. It has a `description`, 
        the `gene` name, the `taxon_id` it belongs to.
        It belongs to a `database` (either '0', SwissProt, or
        '1', TremBL), and to a certain `release`. It also
        stores whether it `has_experimental_interactions`
        or not.
    """
    DATABASES = ((0, 'SwissProt'), (1, 'TremBL'))
    accession = models.CharField(max_length=10)
    entry_name = models.CharField(max_length=20)
    description = models.TextField()
    gene = models.CharField(max_length=50, db_index=True) 
    database = models.PositiveIntegerField(choices=DATABASES, default=0)
    taxon_id = models.ForeignKey(Organism, on_delete=models.CASCADE)
    has_experimental_interactions = models.BooleanField(default=False)
    goa_assigned_goterms = models.ManyToManyField(GOTerm, through='GOAFunctionalAssignment')

    def __unicode__(self):
        return self.accession

    def get_homologs(self):
        """ Returns the set of homologs a a list of triplets,
            where the first member is the target protein, the
            second is the evalue and the third one is the percent
            identity.
        """
        return ((h.target, h.evalue, h.percent_identity) for h in self.homologyrelation_set.iterator())


class GOAFunctionalAssignment(models.Model):
    """ A `GOAFunctionalAssignment` is a mapping between
        a `goterm` and a `protein`  
    """
    goterm = models.ForeignKey(GOTerm, on_delete=models.CASCADE)
    protein = models.ForeignKey(Protein, on_delete=models.CASCADE)


class HomologyRelation(models.Model):
    """ A homology relation is defined as a BLAST
        hit from the `source` protein to the `target`
        protein, with a certain `evalue` and a 
        `percent_identity`.
    """
    source = models.ForeignKey(Protein, 
                               related_name='homologyrelation_source_set',
                               on_delete=models.CASCADE)
    target = models.ForeignKey(Protein,
                               related_name='homologyrelation_target_set',
                               on_delete=models.CASCADE)
    evalue = models.FloatField()
    percent_identity = models.FloatField()


class ProteinInteraction(models.Model):
    """ This is a protein interaction (either
        `ExperimentalProteinInteraction` or
        `PredictedProteinInteraction`). It has
        two interacting proteins (`first` and
        `second`) and a `taxon_id` (duplicated
        for efficiency purposes).
    """
    INTERACTION_TYPES = (
        (0, 'Experimental Protein Interaction'),
        (1, 'Predicted Protein Interaction'))
    first = models.ForeignKey(Protein, related_name='prots_%(class)s_first_set', on_delete=models.CASCADE)
    second = models.ForeignKey(Protein, related_name='prots_%(class)s_second_set', on_delete=models.CASCADE)
    taxon_id = models.ForeignKey(Organism, on_delete=models.CASCADE)
    interaction_type = models.IntegerField(choices=INTERACTION_TYPES, default=0)

    class Meta:
        abstract = True


class ExperimentalProteinInteraction(ProteinInteraction):
    """ An experimental interaction is an interaction
        which has certain `Evidence` associated to it.
        We use `icrep_id` as an internal identifier
        for our purpose.
    """
    icrep_id = models.IntegerField()

class PredictedProteinInteraction(ProteinInteraction):
    """ A `PredictedProteinInteraction` is an interaction
        which comes from two associated homology relations,
        (namely `first_homology` and `second_homology`),
        forming a "generalized interolog" as defined by
        "Yu et al. 2004". A `quality` measure [0-100.0] is
        stored, as well as a flag denoting whether it is
        the best (`is_best`) among all other parallel
        interologs. A link to the `origin_experimental`
        interaction is also stored.
    """
    first_homology = models.ForeignKey(HomologyRelation, 
                                       related_name='predictedinteraction_first_homology_set',
                                       on_delete=models.CASCADE)
    second_homology = models.ForeignKey(HomologyRelation, 
                                        related_name='predictedinteraction_second_homology_set',
                                        on_delete=models.CASCADE)
    quality = models.FloatField()
    is_best = models.BooleanField(default=False)
    origin_experimental = models.ForeignKey(ExperimentalProteinInteraction,
                                            on_delete=models.CASCADE)


class MITerm(models.Model):
    """ `MITerm` is a term that belongs to the MI ontology
    """
    mi_id = models.IntegerField(primary_key=True)
    description = models.TextField()

class Evidence(models.Model):
    """ `Evidence` is a triplet of integers representing
        data about a particular experiment. First, the
        `pubmed_id` where it is published, and then the
        `interaction_type` and the `detection_type`, both
        terms in the Molecular interaction Ontology.
    """
    pubmed_id = models.IntegerField()
    #detection_method = models.IntegerField()
    #interaction_type = models.IntegerField()
    detection_method = models.ForeignKey(MITerm,
                                         related_name="evidence_detection_method",
                                         on_delete=models.CASCADE)
    interaction_type = models.ForeignKey(MITerm,
                                         related_name="evidence_interaction_type",
                                         on_delete=models.CASCADE)
    interaction_supported = models.ForeignKey(ExperimentalProteinInteraction,
                                              on_delete=models.CASCADE)


class StringencyValue(models.Model):
    """ This represents different `e_value` values
        cutoff for which complexes are predicted.
    """

    e_value = models.FloatField()


class PredictedComplex(models.Model):
    """ Represents a predicted complex. It has an
        `stringency_value`, a `tax_id`, a set of
        `proteins`, and a set of `interactions`.

        The field `identifier` is for internal consumption.
        For any given pair (`taxon_id`, `stringency_value`)
        the `identifier` will be unique.
    """
    size = models.IntegerField()
    density = models.FloatField()
    quality = models.FloatField()
    pvalue = models.FloatField()
    identifier = models.IntegerField()
    stringency_value = models.ForeignKey(StringencyValue, on_delete=models.CASCADE)    
    taxon_id = models.ForeignKey(Organism, on_delete=models.CASCADE)
    proteins = models.ManyToManyField(Protein)
    exp_interactions = models.ManyToManyField(ExperimentalProteinInteraction)
    pred_interactions = models.ManyToManyField(PredictedProteinInteraction)


class ComplexFunctionalAssignment(models.Model):
    """ Represents a functional assignment to a predicted 
        protein `complex` obtained through over-representation
        analysis of the individual `GOAFunctionalAssignment`
        of each individual protein and containing a `pvalue`
        and a goterm.    
    """
    goterm = models.ForeignKey(GOTerm, on_delete=models.CASCADE)
    protein_complex = models.ForeignKey(PredictedComplex, on_delete=models.CASCADE)
    pvalue = models.FloatField(default=0.0)
