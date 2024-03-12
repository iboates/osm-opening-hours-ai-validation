#!/bin/bash

wget -4 -O data/data.pbf https://download.geofabrik.de/europe/france/ile-de-france-latest.osm.pbf
docker compose run --rm osmium tags-filter -o /data/opening_hours.osm.pbf /data/data.osm.pbf n/opening_hours
docker compose run --rm --entrypoint=osm2pgsql osm2pgsql -O flex -S /data/opening_hours.lua -H postgis -d o2p -U o2p /data/opening_hours.osm.pbf
