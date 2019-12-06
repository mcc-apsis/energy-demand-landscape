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

pids = [148, 210, 147, 186]

queries = Query.objects.filter(
    text="[GENERATED TYPE 1]",
    project__in=pids
)

all_docs = set([])

redo_queries = False

do_no_reviews = False

no_reviews, created = Query.objects.get_or_create(
    title="No reviews",
    project=Project.objects.get(pk=186),
    text="Manually generated",
    creator=User.objects.get(pk=1)
)

if do_no_reviews:
    nrdocs = set([])
    no_reviews.doc_set.clear()
    
    for q in queries.order_by('project_id'):
        if q.project.id in [186,147]:
            continue
        else:
            docs = set(Doc.objects.filter(query__project=q.project).values_list('pk',flat=True))
            all_docs = all_docs | docs
            
    Through = Doc.query.through
    dqs = [Through(doc_id=d,query=no_reviews) for d in docs]
    Through.objects.bulk_create(dqs)
    no_reviews.r_count = no_reviews.doc_set.count()
    no_reviews.save()

if redo_queries:

    for q in queries.order_by('project_id'):
        print(f"\n{q.title}")
        print(q.r_count)
        q.doc_set.clear()
        if q.project.id == 186:
            docs = all_docs
        else:
            docs = set(Doc.objects.filter(query__project=q.project).values_list('pk',flat=True))
            all_docs = all_docs | docs
        Through = Doc.query.through
        dqs = [Through(doc_id=d,query=q) for d in docs]
        Through.objects.bulk_create(dqs)
        q.r_count = q.doc_set.count()
        q.save()
        print(q.r_count)
        
qids = set(queries.values_list('pk',flat=True)) 
qids.add(no_reviews.id)
queries = Query.objects.filter(pk__in=qids)


for method in ["NM","LD"]:
    for K in [20,40,60,80, 100, 120, 140 ]:
        for q in queries.order_by('r_count'):
            for alpha in [0.05,0.1]:
                if method=="LD":
                    alpha = alpha*10
                model, created = RunStats.objects.get_or_create(
                    method=method,
                    min_freq=10,
                    fancy_tokenization=True,
                    K=K,
                    alpha=alpha,
                    query=q,
                )
                if created or model.status < 3:
                    do_nmf(model.pk)
