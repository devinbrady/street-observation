#!/bin/bash

if [ -d ".venv" ]
then
    source .venv/bin/activate
    pip install -r requirements.txt
    gunicorn wsgi:app
else
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    gunicorn wsgi:app
fi