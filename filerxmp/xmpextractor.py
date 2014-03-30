# -*- coding: utf-8 -*-
# ______________________________________________________________________________
#                                                                         Future
from __future__ import absolute_import
# ______________________________________________________________________________
#                                                                        Contrib
from lxml import etree

NS_DC = '{http://purl.org/dc/elements/1.1/}'
NS_RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
NS_AUX = '{http://ns.adobe.com/exif/1.0/aux/}'
NS_XMP = '{http://ns.adobe.com/xap/1.0/}'

def extract_xmp_for_image(xml_as_string):
    """ Parse the XML string for relevant XMP meta data for an image

    :param xml_as_string: string containing valid <x:xmpmeta/>-XML
    :rtype: a dictionary with relevant meta data that was found in xml_as_string
    """

    #
    # This is sparta. Namespace hell and ununique xml structures even with one
    # single vendor like Adobe. This is an approximation but needs thinking
    # to get a clean, dtd/schema-based solution.
    #

    result = get_empty_default_dict_for_image()
    data = etree.fromstring(xml_as_string)

    # Support for Lightroom 3.5
    # --------------------------------------------------------------------------
    query = '*//{0}title/{1}Alt/{1}li'.format(NS_DC, NS_RDF)
    result['title'] = gvod(data, query)

    query = '*//{0}description/{1}Alt/{1}li'.format(NS_DC, NS_RDF)
    result['description'] = gvod(data, query)

    query = '*//{0}description'.format(NS_DC)
    res = data.find(query)

    if res is not None:
        query = '//@aux:LensInfo'
        result['lens_info'] = gaod(res, query, res.nsmap['aux'], 'aux')

        query = '//@aux:Len'
        result['lens'] =  gaod(res, query, res.nsmap['aux'], 'aux')

        query = '//@xmp:CreateDate'
        result['createdate'] = gaod(res, query, res.nsmap['xmp'], 'xmp')

        query = '//@xmp:ModifyDate'
        result['modifydate'] = gaod(res, query, res.nsmap['xmp'], 'xmp')

        query = '//@xmp:CreatorTool'
        result['creatortool'] = gaod(res, query, res.nsmap['xmp'], 'xmp')

        query = '*//{0}subject/{1}Bag/{1}li'.format(NS_DC, NS_RDF)
        result['keywords'] = gvod(data, query)

        query = '*//{0}creator/{1}Seq/{1}li'.format(NS_DC, NS_RDF)
        result['creator'] = gvod(data, query)

        query = '*//{0}rights/{1}Alt/{1}li'.format(NS_DC, NS_RDF)
        result['copyright'] = gvod(data, query)

    # Support for Lightroom 5
    # --------------------------------------------------------------------------
    query = '*//{0}Lens'.format(NS_AUX)
    result['lens'] = gvod(data, query, result['lens'])

    query = '*//{0}LensInfo'.format(NS_AUX)
    result['lens_info'] = gvod(data, query, result['lens_info'])

    query = '*//{0}CreateDate'.format(NS_AUX)
    result['createdate'] = gvod(data, query, result['createdate'])

    query = '*//{0}CreatorTool'.format(NS_XMP)
    result['creatortool'] = gvod(data, query, result['creatortool'])

    query = '*//{0}CreateDate'.format(NS_XMP)
    result['createdate'] = gvod(data, query, result['createdate'])

    query = '*//{0}ModifyDate'.format(NS_XMP)
    result['modifydate'] = gvod(data, query, result['modifydate'])

    print result
    return result


def gvod(data, query, default=''):
    """ Little helper to check whether query matches result and return text

    :param data: lxml element tree
    :param query: query to perform against the tree
    :param default: default value to return if query does not match
    :rtype: `default` or string
    """
    try:
        result = data.find(query).text
    except AttributeError:
        result = default

    return result


def gaod(data, query, ns, ns_prefix, default=''):
    """ Check whether query matches an attribute and return value

    :param data: lxml element tree
    :param query: query to perform against the tree
    :param ns: namespace of the attribute to be looked up
    :param ns_prefix: prefix of `ns`
    :param default: default value to return if query does not match
    :rtype: `default` or string
    """
    try:
        ns_dict = {ns_prefix: ns}
        result = data.xpath(query, namespaces=ns_dict)[0]
    except:
        result = default

    return result


def get_empty_default_dict_for_image():
    return {
        'title': '',
        'description': '',
        'createdate': '',
        'modifydate': '',
        'lens_info': '',
        'lens': '',
        'creatortool': '',
        'keywords': list(),
        'creator': '',
        'copyright': '',
    }