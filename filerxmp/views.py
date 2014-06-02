# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                         Django
from django.http.response import Http404
from django.views.generic.base import View
# ______________________________________________________________________________
#                                                                        Contrib
from filersets.models import Item
from rest_framework import viewsets
# ______________________________________________________________________________
#                                                                        Package
from filerxmp.serializers import XMPBaseSerializer
from filerxmp.models import XMPBase


# ______________________________________________________________________________
#                                                               View: ProcessXMP
from rest_framework.generics import RetrieveAPIView, ListAPIView


class ProcessXMPView(View):

    def get(self, request, file_id=None):
        pass


# ______________________________________________________________________________
#                                                              API View: XMPBase
class XMPBaseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows XMPBase data to be viewed
    """
    queryset = XMPBase.objects.all()
    serializer_class = XMPBaseSerializer


class XMPBaseDetailByItemPk(RetrieveAPIView):
    """
    Return the associated XMP item by Item pk.

    Note that this method checks for known child classes of XMPBase and returns
    the child class rather than the base class if available. Otherwise the
    XMPBase class is returned.
    """
    queryset = XMPBase.objects.all()
    serializer_class = XMPBaseSerializer
    lookup_field = 'pk'

    def get_object(self):
        try:
            pk = int(self.kwargs.get('pk'))
        except TypeError:
            # TODO  Do exception handling
            pass

        try:
            xmpbase = Item.objects.get(pk=pk).filer_file.file_xmpbase
            if hasattr(xmpbase, 'xmpimage'):
                return xmpbase.xmpimage
            else:
                return xmpbase
        except Item.DoesNotExist:
            raise Http404