#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

python manage.py download_geolite2_country
