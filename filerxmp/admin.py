# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                         Django
from django.forms import ModelForm
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import ModelAdmin, StackedInline
# ______________________________________________________________________________
#                                                                        Contrib
from filer.admin import ImageAdmin
# ______________________________________________________________________________
#                                                                         Custom
from filerxmp.models import XMPImage, XMPBase
from filersets.admin import ItemAdmin
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


# ______________________________________________________________________________
#                                                           ModelForm: XMP Image
class XMPImageForm(ModelForm):
    class Meta:
        model = XMPImage
        widgets = {
            # 'file': LinkedSelect,
            # 'xmp_caption': AutosizedTextarea(
            #     attrs={'rows': 3, 'class': 'input-xlarge'}),
            # 'xmp_description': AutosizedTextarea(
            #     attrs={'rows': 3, 'class': 'input-xlarge'}),
            # 'xmp_createdate': SuitSplitDateTimeWidget,
            # 'xmp_modifydate': SuitSplitDateTimeWidget,
        }


# ______________________________________________________________________________
#                                                          ModelAdmin: XMP Image
class XMPImageAdmin(ModelAdmin):
    form = XMPImageForm
    readonly_fields = ('file', 'is_processed', 'has_data',)
    list_display = ('file', 'xmp_createdate', 'xmp_title', 'xmp_creatortool',
                    'has_data', 'is_processed',)


# ______________________________________________________________________________
#                                                       StackedInline: XMP Image
if has_suit:
    class XMPImageForm(ModelForm):
        class Meta:
            model = XMPImage
            widgets = {
                'xmp_createdate': SuitSplitDateTimeWidget,
                'xmp_modifydate': SuitSplitDateTimeWidget,
                'xmp_caption': AutosizedTextarea,
                'xmp_description': AutosizedTextarea,
            }


class XMPImageAdminInline(StackedInline):
    if has_suit:
        form = XMPImageForm

    exclude = ['xmp_creatortool', 'xmp_blend', 'xmp_lens']
    readonly_fields = ('file', 'is_processed', 'has_data',)
    model = XMPImage
    extra = 0
    max_num = 0

# ______________________________________________________________________________
#                                                            Extension ItemAdmin
class HasXMPFilter(admin.SimpleListFilter):
    title = _('xmp')
    parameter_name = 'xmp'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('yes')),
            ('no', _('no')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(filer_file__file_xmpbase__has_data=True)

        if self.value() == 'no':
            return queryset.filter(filer_file__file_xmpbase__has_data=False)


def xmp(self, obj):
    """
    Get an indicator whether the item carries XMP data.
    """
    # Note that normally defining the boolean attribute on the method would
    # turn django to render the nice yesno images. But since we're extending
    # the host class from here and python < 3 does not support assigning
    # attributes to instancemethods, we're returning yes or no here.
    return _('yes') if obj.filer_file.file_xmpbase.has_data else _('no')

ItemAdmin.xmp = classmethod(xmp)
ItemAdmin.list_display = ItemAdmin.list_display + ('xmp',)
ItemAdmin.list_filter = ItemAdmin.list_filter + (HasXMPFilter,)
# ItemAdmin.inlines = ItemAdmin.inlines + [XMPImageAdminInline]
ItemAdmin.Media.js.append('filerxmp/js/filerxmp_admin.js')
ItemAdmin.Media.css['all'].append('filerxmp/css/filerxmp_admin.css')

ImageAdmin.inlines = [XMPImageAdminInline] + ImageAdmin.inlines

# ______________________________________________________________________________
#                                                                   Registration
admin.site.register(XMPImage, XMPImageAdmin)