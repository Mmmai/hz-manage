from rest_framework.response import Response
from mapi.resources import PortalResource
from django.http import HttpResponse,FileResponse
from rest_framework.views import APIView
import datetime,time
from .models import Portal,Pgroup
from django.utils.encoding import escape_uri_path
from django.utils.http import urlquote

class PortalExport(APIView):
    def __init__(self):
        self.portal_resource = PortalResource()
    def post(self,request,*args,**kwargs):
        rowid = request.data.get('rowid')
        template = request.data.get('template')
        filename = "门户列表_{}.xls".format(time.strftime("%Y%m%d_%H%M%S"))
        if rowid != None:
            querset = Portal.objects.filter(id__in=rowid)
        elif template != None:
            querset = Portal.objects.filter(id__in='1xxx23213323')
            filename = "门户列表-模板导入.xls"

        else:
            querset = Portal.objects.all()
        dataset = self.portal_resource.export(querset)
        # response = FileResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')

        response['Content-Disposition'] = "attachment; filename={}".format(escape_uri_path(filename))
        return response
    def get(self,request,*args,**kwargs):
        # rowid = request.data.get('rowid')
        querset = Portal.objects.filter(id__in='1xxx23213323')
        dataset = self.portal_resource.export(querset)
        filename = "门户列表-模板导入.xls"
        # response = FileResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')

        response['Content-Disposition'] = "attachment; filename={}".format(escape_uri_path(filename))
        return response