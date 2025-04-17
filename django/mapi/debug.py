#!/usr/bin/env python3
# coding: utf-8

import os, django

os.environ['DJANGO_SETTINGS_MODULE'] = 'vuedjango.settings'
django.setup()
from mapi.resources import PortalResource

from mapi.models import *


# print(Portal._meta.get_fields())
# print(dir(Portal._meta.get_fields()[0]))
# for i in Portal._meta.get_fields():
#     if i._verbose_name:
#         print(i.name)
#         print(i._verbose_name)

# p = PortalResource()
# querset = Portal.objects.filter(id__in=[3,10,5])
# datas = p.export(querset)
# print(datas.csv)
import datetime,time
print(datetime.datetime.now())
print(time.strftime("%Y%m%d_%H%M%S"))