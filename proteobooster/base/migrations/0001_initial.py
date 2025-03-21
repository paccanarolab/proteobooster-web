# Generated by Django 4.1.7 on 2023-05-19 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentalProteinInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.IntegerField(choices=[(0, 'Experimental Protein Interaction'), (1, 'Predicted Protein Interaction')], default=0)),
                ('icrep_id', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GOAFunctionalAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='GOTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('go_id', models.IntegerField()),
                ('function', models.CharField(max_length=300)),
                ('ontology', models.CharField(choices=[('bp', 'Biological Process'), ('mf', 'Molecular Function'), ('cc', 'Cellular component')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='HomologyRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evalue', models.FloatField()),
                ('percent_identity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='MITerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mi_id', models.CharField(max_length=7)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxon_id', models.PositiveIntegerField()),
                ('name', models.CharField(db_index=True, max_length=150)),
                ('domain', models.CharField(choices=[('a', 'Archaea'), ('b', 'Bacteria'), ('e', 'Eukaryota'), ('v', 'Viridae')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Protein',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.CharField(max_length=30)),
                ('entry_name', models.CharField(default='', max_length=30)),
                ('description', models.TextField()),
                ('database', models.PositiveIntegerField(choices=[(0, 'SwissProt'), (1, 'TremBL')], default=0)),
                ('has_experimental_interactions', models.BooleanField(default=False)),
                ('goa_assigned_goterms', models.ManyToManyField(through='base.GOAFunctionalAssignment', to='base.goterm')),
                ('taxon_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.organism')),
            ],
        ),
        migrations.CreateModel(
            name='PredictedProteinInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.IntegerField(choices=[(0, 'Experimental Protein Interaction'), (1, 'Predicted Protein Interaction')], default=0)),
                ('quality', models.FloatField()),
                ('is_best', models.BooleanField(default=False)),
                ('first', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prots_%(class)s_first_set', to='base.protein')),
                ('first_homology', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictedinteraction_first_homology_set', to='base.homologyrelation')),
                ('origin_experimental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.experimentalproteininteraction')),
                ('second', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prots_%(class)s_second_set', to='base.protein')),
                ('second_homology', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictedinteraction_second_homology_set', to='base.homologyrelation')),
                ('taxon_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.organism')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PredictedComplex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.IntegerField()),
                ('density', models.FloatField()),
                ('quality', models.FloatField()),
                ('pvalue', models.FloatField()),
                ('exp_interactions', models.ManyToManyField(to='base.experimentalproteininteraction')),
                ('pred_interactions', models.ManyToManyField(to='base.predictedproteininteraction')),
                ('proteins', models.ManyToManyField(to='base.protein')),
            ],
        ),
        migrations.AddField(
            model_name='homologyrelation',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homologyrelation_source_set', to='base.protein'),
        ),
        migrations.AddField(
            model_name='homologyrelation',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homologyrelation_target_set', to='base.protein'),
        ),
        migrations.AddField(
            model_name='goafunctionalassignment',
            name='goterm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.goterm'),
        ),
        migrations.AddField(
            model_name='goafunctionalassignment',
            name='protein',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.protein'),
        ),
        migrations.AddField(
            model_name='experimentalproteininteraction',
            name='first',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prots_%(class)s_first_set', to='base.protein'),
        ),
        migrations.AddField(
            model_name='experimentalproteininteraction',
            name='second',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prots_%(class)s_second_set', to='base.protein'),
        ),
        migrations.AddField(
            model_name='experimentalproteininteraction',
            name='taxon_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.organism'),
        ),
        migrations.CreateModel(
            name='Evidence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pubmed_id', models.TextField()),
                ('detection_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_detection_method', to='base.miterm')),
                ('interaction_supported', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.experimentalproteininteraction')),
                ('interaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evidence_interaction_type', to='base.miterm')),
            ],
        ),
        migrations.CreateModel(
            name='ComplexFunctionalAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pvalue', models.FloatField(default=0.0)),
                ('goterm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.goterm')),
                ('protein_complex', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.predictedcomplex')),
            ],
        ),
    ]
