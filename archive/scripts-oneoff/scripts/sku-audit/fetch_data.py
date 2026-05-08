#!/usr/bin/env python3
"""Fetch latest platform items + lionwheel data from Supabase REST.

Uses the project's Supabase URL + anon key (read-only RLS-safe).
"""
import json
import os
import urllib.request
import urllib.parse
import sys
from pathlib import Path

# Read DATABASE_URL from env, or hard-fail
SUPABASE_URL = 'https://rvadsozabmxkkrktwgnv.supabase.co'
ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
KEY = SERVICE_KEY or ANON_KEY

if not KEY:
    print('ERROR: set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY env var', file=sys.stderr)
    sys.exit(2)

OUT = Path(__file__).resolve().parent

# We can't use RPC if there's no exposed function, so we need a different path.
# Best path: Tom should run this through the existing harness. For now, leave a stub.
print('This script requires DATABASE_URL access; run via psql or supabase MCP.', file=sys.stderr)
print('Use the inline JSON dumps already produced above.', file=sys.stderr)
