# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                         Django
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.db.models.signals import post_save
from django.dispatch import receiver
# ______________________________________________________________________________
#                                                                        Contrib
from filer.models import File, Image
from taggit_autosuggest_select2.managers import TaggableManager
# ______________________________________________________________________________
#                                                                         Custom
# ______________________________________________________________________________
#                                                                        Package
from filerxmp.xmpextractor import extract_xmp_for_image, \
    get_empty_default_dict_for_image
from filerxmp.helpers import get_xmp_string_from__file, get_datetime_or_none


# ______________________________________________________________________________
#                                                               Manager: XMPBase
class XMPBaseManager(models.Manager):

    def create_or_update_xmp(self, fid=None):
        """
        This method is the entry point for XMP meta data creation for all
        supported file types. It delegates the detailed tasks to private
        methods of the model manager.

        :param fid: None, int or list of file ids to process
        """
        # TODO  Support fid parameter
        if not fid:
            filter_query = {}
        else:
            filter_query = {'pk': fid}

        files = File.objects.filter(**filter_query)

        for f in files:
            if f.file_type == 'Image':
                self._create_or_update_image(f)

    def _create_or_update_image(self, f):
        """
        This private routine creates or updates meta data for a given
        image file

        :param f: object of instan filer file
        """
        try:
            xmp_img = XMPImage.objects.get(file=f.pk)
        except ObjectDoesNotExist:
            xmp_img = XMPImage()

        xmp_img.file = f
        xmp_str = get_xmp_string_from__file(xmp_img.file.path)

        # File doesn't carry XMP data
        if not xmp_str:
            defaults = get_empty_default_dict_for_image()
            skip_keys = ('createdate', 'modifydate')
            for k, v in defaults.items():
                if k in skip_keys:
                    continue
                xmp_img.__setattr__('xmp_{}'.format(k), v)
            xmp_img.has_data = False
            xmp_img.is_processed = True
            xmp_img.save()
            return

        # File carries XMP data
        results = extract_xmp_for_image(xmp_str)

        # Taggit keywords need to be treated specially in three ways
        # First existings tags need to be dumped
        # Secondly they need to be inserted via add()
        # Thrid they may only be inserted we have a PK
        if 'keywords' in results \
                and len(results['keywords']) > int(1):
            keys = results['keywords'].split(',')
            del results['keywords']

        results['createdate'] = get_datetime_or_none(
            results['createdate'])

        results['modifydate'] = get_datetime_or_none(
            results['modifydate'])

        for k, v in results.items():
            xmp_img.__setattr__('xmp_{}'.format(k), v)

        try:
            # First save
            # Yes it's a bit more costly but we assure proper saving before
            # setting the is_processed flag to True on second save
            xmp_img.has_data = True
            xmp_img.save()

            # Second save
            # No exception so far -> add tags and set is_processed to True
            if 'keys' in locals():
                xmp_img.xmp_keywords.clear()
                for key in reversed(keys):
                    key = key.replace('"', '').strip().lower()
                    xmp_img.xmp_keywords.add(key)
            xmp_img.is_processed = True
            xmp_img.save()

        except (IntegrityError, ValidationError):
            # TODO Do some logging, prepare a message
            print 'Could not save {}'.format(f.pk)
            return


# ______________________________________________________________________________
#                                                                 Model: XMPBase
class XMPBase(TimeStampedModel):

    class Meta:
        verbose_name = _('XMP base')
        verbose_name_plural = _('XMP base')

    objects = XMPBaseManager()

    id = models.AutoField(primary_key=True)

    has_data = models.BooleanField(
        _('has XMP data'),
        blank=True,
        default=False,
        null=False
    )

    is_processed = models.BooleanField(
        _('is processed'),
        blank=True,
        default=False,
        null=False
    )

    file = models.OneToOneField(
        File,
        verbose_name=_('file'),
        related_name='file_xmpbase',
        blank=False,
        null=False,
        default=None
    )

    xmp_title = models.CharField(
        _('XMP title'),
        max_length=150,
        blank=True,
        default=None,
        null=True
    )

    xmp_caption = models.TextField(
        _('XMP capture text'),
        blank=True,
        default=None,
        null=True
    )

    xmp_description = models.TextField(
        _('XMP description'),
        blank=True,
        default=None,
        null=True
    )

    xmp_keywords = TaggableManager(
        blank=True,
    )

    xmp_createdate = models.DateTimeField(
        _('create date'),
        blank=True,
        default=None,
        null=True
    )

    xmp_modifydate = models.DateTimeField(
        _('modify date'),
        blank=True,
        default=None,
        null=True
    )

    xmp_creator = models.CharField(
        _('author'),
        max_length=100,
        blank=True,
        default=None,
        null=True
    )

    xmp_copyright = models.CharField(
        _('copyright'),
        max_length=100,
        blank=True,
        default=None,
        null=True
    )

    xmp_creatortool = models.CharField(
        _('creator tool'),
        max_length=120,
        blank=True,
        default=None,
        null=True
    )

    def get_tags_display(self):
        # TODO This needs to currently be invoked by child instance or it
        #      returns 0 keywords.
        return self.xmp_keywords.values_list('name', flat=True)

    def __unicode__(self):
        return u'{}'.format(self.file.original_filename)


# ______________________________________________________________________________
#                                                                Model: XMPImage
class XMPImage(XMPBase):

    class Meta:
        verbose_name = _('XMP image data')
        verbose_name_plural = _('XMP image data')

    xmp_blend = models.CharField(
        _('blend'),
        max_length=4,
        blank=True,
        default=None,
        null=True
    )

    xmp_lens_info = models.CharField(
        _('lens info'),
        max_length=100,
        blank=True,
        default=None,
        null=True
    )

    xmp_lens = models.CharField(
        _('lens'),
        max_length=60,
        blank=True,
        default=None,
        null=True
    )

    def __unicode__(self):
        return u'{}, type: Image'.format(self.file.original_filename)


# ______________________________________________________________________________
#                                                               Signal Listeners
@receiver(post_save, sender=File)
def extract_file_xmp(sender, **kwargs):
    pass

@receiver(post_save, sender=Image)
def extract_image_xmp(sender, **kwargs):
    XMPBase.objects.create_or_update_xmp(kwargs.get('instance').pk)