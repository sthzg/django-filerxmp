# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                         Django
from django.views.generic.base import View


class ProcessXMPView(View):

    def get(self, request, file_id=None):
        pass