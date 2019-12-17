# Load some libraries for reading the data from the database and plotting

import django
import sys, os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('/home/galm/software/django/tmv/BasicBrowser/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BasicBrowser.settings")
django.setup()

from scoping.models import *
from tmv_app.tasks import *

from django.db.models import Count, Sum


queries = Query.objects.filter(pk__in=[7956,7957])
for method in ["NM","LD"]:
    for K in [20, 40, 60, 80, 100]:
        for q in queries.order_by('r_count'):
            for alpha in [0.05,0.1]:
                if method=="LD":
                    alpha = alpha*10
                else:
                    alpha = 0.1
                model, created = RunStats.objects.get_or_create(
                    method=method,
                    min_freq=15,
                    fancy_tokenization=True,
                    K=K,
                    alpha=alpha,
                    query=q,
                )
                if created or model.status < 3:
                    do_nmf(model.pk)