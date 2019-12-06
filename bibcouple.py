import networkx as nx
import pickle
import random
import scipy
from scipy.sparse import tril, find
import django
import sys, os
import pandas as pd
import matplotlib.pyplot as plt
import igraph
from django.core.management import call_command

sys.path.append('/home/galm/software/django/tmv/BasicBrowser/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BasicBrowser.settings")
django.setup()

from scoping.models import *
from tmv_app.tasks import *

from django.db.models import Count, Sum

pids = [148, 182, 147, 186]

queries = Query.objects.filter(
    text="[GENERATED TYPE 1]",
    project__in=pids
)
for q in queries:
    print(q)
    call_command('citation_matrix', q.id)
    call_command('bib_matrix', q.id, 0, "/home/galm/projects/energy-demand/citation_data")