# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

"""
Compare performance of different parsing methods,
"""

import os, os.path
import time

import lxml.etree
import lxml.objectify
import xml.dom.minidom

from amazonproduct import API
from amazonproduct import AWSError
from config import AWS_KEY, SECRET_KEY

# xml.minidom
#
def minidom_response_parser(fp):
    root = xml.dom.minidom.parse(fp)
    # parse errors
    for error in root.getElementsByTagName('Error'):
        code = error.getElementsByTagName('Code')[0].firstChild.nodeValue
        msg = error.getElementsByTagName('Message')[0].firstChild.nodeValue
        raise AWSError(code, msg)
    return root

# lxml.objectify
#
def objectify_response_parser(fp):
    root = lxml.objectify.parse(fp).getroot()
    nspace = root.nsmap.get(None, '')
    errors = root.xpath('//aws:Request/aws:Errors/aws:Error', 
                        namespaces={'aws' : nspace})
    for error in errors:
        raise AWSError(error.Code.text, error.Message.text)
    return root

# lxml.etree
#
def etree_response_parser(fp):
    root = lxml.etree.parse(fp).getroot()
    error = root.find('Error')
    if error:
        raise AWSError(error.Code.text, error.Message.text)
    return root

if __name__ == '__main__':

    #: how many times are all XML files parsed
    RUNS = 10

    custom_parsers = {
        'lxml.objectify' : objectify_response_parser, 
        'lxml.etree' : etree_response_parser, 
        'minidom' : minidom_response_parser, 
    }

    xml_files = [os.path.join(root, file)
        for root, dirs, files in os.walk('.')
        for file in files
        if os.path.splitext(file)[1].lower() == '.xml']

    print "Parsing %i XML files..." % (len(xml_files)*RUNS, )
    for label, parser in custom_parsers.items():
        print label, 
        start = time.clock()
        api = API(AWS_KEY, SECRET_KEY, processor=parser)
        for i in range(RUNS):
            for path in xml_files:
                try:
                    api._parse(open(path))
                except AWSError:
                    pass
        stop = time.clock()
        print stop - start
