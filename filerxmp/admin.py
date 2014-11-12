# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.forms import ModelForm
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.options import ModelAdmin, StackedInline
from filer.admin import ImageAdmin
from filer.models import Image
from filersets.models import Item
from filerstream.hooks import admin_stream_hook
from filerxmp.models import XMPImage
from filersets.admin import ItemAdmin

try:
    from suit.widgets import LinkedSelect, AutosizedTextarea, \
        SuitSplitDateTimeWidget

    has_suit = True
except ImportError:
    has_suit = False

try:
    from django_select2 import AutoSelect2MultipleField, Select2MultipleWidget
    has_select2 = True
except ImportError:
    has_select2 = False


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


class XMPImageAdmin(ModelAdmin):
    form = XMPImageForm
    readonly_fields = ('file', 'is_processed', 'has_data',)
    list_display = ('file', 'xmp_createdate', 'xmp_title', 'xmp_creatortool',
                    'has_data', 'is_processed',)


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


ItemAdmin.Media.js.append('filerxmp/js/filerxmp_admin.js')
ItemAdmin.Media.css['all'].append('filerxmp/css/filerxmp_admin.css')

ItemAdmin = admin.site._registry[Item].__class__


class ExtendedItemAdmin(ItemAdmin):
    """
    Extends the default filersets ItemAdmin to show a column that indicates
    whether XMP data is available for a file.
    """
    def __init__(self, *args, **kwargs):
        super(ItemAdmin, self).__init__(*args, **kwargs)

    def get_list_display(self, request):
        default_list_display = super(ItemAdmin, self).get_list_display(request)
        return list(default_list_display) + [self.xmp]

    def get_list_filter(self, request):
        default_list_filter = super(ItemAdmin, self).get_list_filter(request)
        return default_list_filter + [HasXMPFilter]

    def xmp(self, obj):
        """
        Get an indicator whether the item carries XMP data.
        """
        return True if obj.filer_file.file_xmpbase.has_data else False

    xmp.boolean = True
    xmp.allow_tags = True

ItemAdmin = ExtendedItemAdmin
admin.site.unregister(Item)
admin.site.register(Item, ItemAdmin)


# Extension for Filer ImageAdmin
ImageAdmin = admin.site._registry[Image].__class__


class ExtendedImageAdmin(ImageAdmin):
    """
    Extends the filer image change page with an inline for XMP data.
    """
    def __init__(self, *args, **kwargs):
        super(ImageAdmin, self).__init__(*args, **kwargs)
        self.inlines = self.inlines + [XMPImageAdminInline]

ImageAdmin = ExtendedImageAdmin


class ImageAdminMedia:
    js = ['filerxmp/js/filerxmp_admin.js']
    css = {'all': [
        'filersets/css/filersets_admin.css',
        '//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.min.css'
    ]}

ImageAdmin.Media = ImageAdminMedia

admin.site.unregister(Image)
admin.site.register(Image, ImageAdmin)

admin.site.register(XMPImage, XMPImageAdmin)


def has_xmp_data_field(obj):
    """Returns a flag whether the item carries XMP data."""
    if hasattr(obj, 'file_xmpbase'):
        yesno = 'yes' if obj.file_xmpbase.has_data else 'no'
    else:
        yesno = 'no'

    return '<img src="/static/admin/img/icon-{}.gif">'.format(yesno)

admin_stream_hook.register('has_xmp_data', _('XMP'), has_xmp_data_field)