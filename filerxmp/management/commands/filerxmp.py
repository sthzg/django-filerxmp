# -*- coding:utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                           Core
import sys
# ______________________________________________________________________________
#                                                                         Django
from django.core.management.base import BaseCommand
# ______________________________________________________________________________
#                                                                        Package
from filerxmp.models import XMPBase


class Command(BaseCommand):
    args = ''
    help = 'Process XMP data'
    can_import_settings = True

    def handle(self, *args, **options):
        """ Command extracts XMP data for all files """
        XMPBase.objects.create_or_update_xmp()

        sys.exit(0)
