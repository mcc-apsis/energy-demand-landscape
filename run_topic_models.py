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

do_no_reviews = True

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
    for p in pids:
        q = queries.get(project__id=p)
        #for q in queries.order_by('project_id'):
        print(f"\n{q.title}")
        print(q.r_count)
        q.doc_set.clear()
        qs = Query.objects.filter(
            project=q.project,
        ).exclude(
            text="[GENERATED TYPE 1]"
        )
        if q.project.id == 186:
            print("all documents!")
            docs = all_docs
        elif q.project.id == 147:
            docs = set(Doc.objects.filter(
                query__in=qs,
            ).values_list('pk',flat=True))
        elif q.project.id == 148:
            docs = set(Doc.objects.filter(
                query__project=q.project,
                query__title__icontains="_renew"
            ).values_list('pk',flat=True))           
        else:
            docs = set(Doc.objects.filter(query__project=q.project).values_list('pk',flat=True))
            all_docs = all_docs | docs
        Through = Doc.query.through
        dqs = [Through(doc_id=d,query=q) for d in docs]
        Through.objects.bulk_create(dqs)
        q.r_count = q.doc_set.count()
        q.save()
        print(q.r_count)
        
qids = set(queries.exclude(project__in=[148,147,210]).values_list('pk',flat=True)) 
qids.add(no_reviews.id)
queries = Query.objects.filter(pk__in=qids)


for method in ["NM","LD"]:
    for K in [20, 40, 60, 80, 100]:
        for q in queries.order_by('r_count'):
            for alpha in [0.05,0.1]:
                if method=="LD":
                    alpha = alpha*10
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
