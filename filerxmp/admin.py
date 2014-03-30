# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                         Django
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.admin.options import ModelAdmin
# ______________________________________________________________________________
#                                                                         Custom
from filerxmp.models import XMPImage, XMPBase
# ______________________________________________________________________________
#                                                                    Django Suit
try:
    from suit.widgets import LinkedSelect, AutosizedTextarea, \
        SuitSplitDateTimeWidget

    has_suit = True
except ImportError:
    has_suit = False
# ______________________________________________________________________________
#                                                                 Django Select2
try:
    from django_select2 import AutoSelect2MultipleField, Select2MultipleWidget
    has_select2 = True
except ImportError:
    has_select2 = False


class XMPImageForm(ModelForm):
    class Meta:
        model = XMPImage
        widgets = {
            'file': LinkedSelect,
            'xmp_caption': AutosizedTextarea(
                attrs={'rows': 3, 'class': 'input-xlarge'}),
            'xmp_description': AutosizedTextarea(
                attrs={'rows': 3, 'class': 'input-xlarge'}),
            'xmp_createdate': SuitSplitDateTimeWidget,
            'xmp_modifydate': SuitSplitDateTimeWidget,
        }

class XMPImageAdmin(ModelAdmin):
    form = XMPImageForm
    readonly_fields = ('is_processed', 'has_data',)
    list_display = ('file', 'xmp_createdate', 'xmp_title', 'has_data',
                    'is_processed',)


admin.site.register(XMPImage, XMPImageAdmin)