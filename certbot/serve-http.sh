#!/bin/bash
set -e

# Simple HTTP server for ACME challenges using Python
python3 -m http.server --directory /var/www/certbot 80 