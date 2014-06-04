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
from filerxmp.serializers import XMPBaseSerializer, XMPImageSerializer
from filerxmp.models import XMPBase, XMPImage


# ______________________________________________________________________________
#                                                               View: ProcessXMP
from rest_framework.generics import RetrieveAPIView


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


class XMPImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows XMPImage data to be viewed
    """
    queryset = XMPImage.objects.all()
    serializer_class = XMPImageSerializer


class XMPBaseDetail(RetrieveAPIView):
    """
    Return the associated XMP item.

    Currently supported lookups by:
    - pk_item
    - pk_file

    Note that this method checks for known child classes of XMPBase and returns
    the child class rather than the base class if available. Otherwise the
    XMPBase class is returned.
    """
    queryset = XMPBase.objects.all()
    serializer_class = XMPBaseSerializer
    lookup_field = 'pk'

    def get_object(self):
        # Check which lookup we need to perform.
        if 'pk_item' in self.kwargs:
            g_query = {'pk': int(self.kwargs.get('pk_item'))}
        elif 'pk_file' in self.kwargs:
            g_query = {'file': int(self.kwargs.get('pk_file'))}
        else:
            raise ValueError

        try:
            # xmpbase = Item.objects.get(**g_query).filer_file.file_xmpbase
            xmpbase = XMPBase.objects.get(**g_query)
            if hasattr(xmpbase, 'xmpimage'):
                return xmpbase.xmpimage
            else:
                return xmpbase
        except Item.DoesNotExist:
            raise Http404