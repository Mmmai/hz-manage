#!/usr/bin/env python
# coding: utf-8

# import os, django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE','vuedjango.settings')
# django.setup()

# from mlog.models import *


# print(Portal._meta.get_fields())
# print(dir(Portal._meta.get_fields()[0]))
# for i in Portal._meta.get_fields():
#     if i._verbose_name:
#         print(i.name)
#         print(i._verbose_name)

# # p = PortalResource()
# querset = LogFlow.objects.filter(id='42')
# print(querset)
# datas = p.export(querset)
# print(datas.csv)
import datetime,time
print(datetime.datetime.now())
print(time.strftime("%Y%m%d_%H%M%S"))

from django.http import HttpResponse,JsonResponse

import json
a = {1:'44',13:'555',10:'xxx'}
print(JsonResponse(a))