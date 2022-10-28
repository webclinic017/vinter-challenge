#!/usr/bin/env bash

# Activate Python virtual environment.
. .venv/bin/activate

# Execute.
python -W ignore::FutureWarning main.py -tt uni -dp binance -us kdj -wg
