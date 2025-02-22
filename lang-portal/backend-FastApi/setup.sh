#!/bin/bash
export PYTHONPATH=.
python -m scripts.run_migrations
python -m scripts.seed_data 