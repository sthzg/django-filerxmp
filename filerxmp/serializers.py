# -*- coding: utf-8 -*-
from filerxmp.models import XMPBase, XMPImage
from rest_framework import serializers


class XMPBaseSerializer(serializers.HyperlinkedModelSerializer):
    xmp_keywords = serializers.Field(source='get_tags_display')

    class Meta:
        model = XMPBase
        fields = ['id', 'file', 'has_data', 'is_processed', 'xmp_title',
                  'xmp_description', 'xmp_keywords']


class XMPImageSerializer(serializers.HyperlinkedModelSerializer):
    xmp_keywords = serializers.Field(source='get_tags_display')

    class Meta:
        model = XMPImage
        fields = ['id', 'file', 'has_data', 'is_processed', 'xmp_title',
                  'xmp_description', 'xmp_keywords']