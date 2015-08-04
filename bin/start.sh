#!/bin/sh

script=$(readlink -f "$0")
bindir=$(dirname "$script")

PYTHONPATH="$bindir"/.. paster serve paste.config --reload >> /var/log/reporting-api.log 2>&1
