# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.utils import IntegrityError, DataError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from filer.models import File, Image
from filerxmp.helpers import get_iptc_keywords
from taggit_autosuggest_select2.managers import TaggableManager
from .xmpextractor import extract_xmp_for_image, get_empty_default_dict_for_image
from .helpers import get_xmp_string_from__file, get_datetime_or_none


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
        """Creates or updates meta data for a given image file.

        :param f: A filer file instance.
        """
        try:
            xmp_img = XMPImage.objects.get(file=f.pk)
        except XMPImage.DoesNotExist:
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

        # Additionally check for IPTC keywords and add a diff from XMP.
        iptc_keywords = get_iptc_keywords(f.path)

        keys = iptc_keywords

        # Taggit keywords need to be treated specially in three ways
        # First existing tags need to be dumped
        # Secondly they need to be inserted via add()
        # Third they may only be inserted if we have a PK
        if 'keywords' in results and len(results['keywords']) > int(1):
            xmp_keywords = results['keywords'].split(',')
            xmp_keywords = [k.strip() for k in xmp_keywords]

            # Make a diff between keys and iptc_keys and add unique tags.
            lower_compare = [k.lower() for k in keys]
            for key in xmp_keywords:
                if key.lower() not in lower_compare:
                    keys.append(key)
            del results['keywords']

        results['createdate'] = get_datetime_or_none(
            results['createdate'])

        results['modifydate'] = get_datetime_or_none(
            results['modifydate'])

        for k, v in results.items():
            if k == 'keywords': continue
            xmp_img.__setattr__('xmp_{}'.format(k), v)

        try:
            # First save
            xmp_img.has_data = True
            xmp_img.save()

            # Second save
            if len(locals()['keys']) > 0:
                xmp_img.xmp_keywords.clear()

                for key in reversed(keys):
                    key = key.replace('"', '').strip().lower()
                    if not key or key == '': continue
                    xmp_img.xmp_keywords.add(key)

            xmp_img.is_processed = True
            xmp_img.save()

        except (IntegrityError, ValidationError):
            # TODO Do some logging, prepare a message
            print 'Could not save {}'.format(f.pk)
            return


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
        return self.xmp_keywords.values_list('name', flat=True)

    def __unicode__(self):
        return u'{}'.format(self.file.original_filename)


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


@receiver(post_save, sender=File)
def extract_file_xmp(sender, **kwargs):
    pass

@receiver(post_save, sender=Image)
def extract_image_xmp(sender, **kwargs):
    XMPBase.objects.create_or_update_xmp(kwargs.get('instance').pk)