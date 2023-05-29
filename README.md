# ProteoBOOSTER web
Web application for ProteoBOOSTER

Once all database files are generated, this repository can be used to setup an instance of the ProteoBOOSTER interactive explorer.

# How to start a new instance (step-by-step)

First, configure the Docker related files. By default a reverse proxy is setup here which mounts the application onto ```http://localhost/proteobooster/```. This might not be what you want, so feel free to ignore the reverse proxy and run simply the rest.

Assuming you ran

```bash
docker compose up -d
```

Then you should run a couple of commands onto the `proteobooster` container. To do this, here we run a `bash` using Docker, but you can achieve the same running `docker compose exec`.

> On the container, run the following (this assumes you have placed the output from the ProteoBOOSTER exporter into `base/data`. This is not required, and you can mount any directory you want and update the paths used below.

```bash
python manage.py migrate
python manage.py load_database base/data/UP000000437_7955-db-goterms.tsv base/data/UP000000437_7955-db-mi_ontology.tsv base/data/UP000000437_7955-db-organisms.tsv base/data/UP000000437_7955-db-proteins.tsv base/data/UP000000437_7955-db-go_annotations.tsv base/data/UP000000437_7955-db-homologs.tsv base/data/UP000000437_7955-db-interactions.tsv base/data/UP000000437_7955-db-evidence.tsv base/data/UP000000437_7955-db-interologs.tsv base/data/UP000000437_7955-db-complexes.tsv base/data/UP000000437_7955-db-complexes_proteins.tsv base/data/UP000000437_7955-db-comp_interactions.tsv base/data/UP000000437_7955-db-comp_interologs.tsv base/data/UP000000437_7955-db-overrep.tsv
python manage.py create_download_cache 0.0 0.0
```

Then, you should run the queries in `queries.sql` while connected to the database. The easiest way to do this at the moment is to use the pgadmin container included in the Docker compose file, and simply run these on the configured database.

Finally, you should configure the `INSTANCE_ORGANISM_ID` environment varible on the `.env.proteobooster.yaml` file.

