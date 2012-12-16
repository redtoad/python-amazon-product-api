# Copyright (C) 2010 Sebastian Rahlf <basti at redtoad dot de>

"""
Compare performance of different parsing methods. On my netbook the following
output was generated::

    Collecting test files...
    Parsing 2020 XML files...
    minidom 25.83
    lxml.etree 1.79
    lxml.objectify 2.43

"""

import os.path
import time

import lxml.etree
import lxml.objectify
import xml.dom.minidom

# make sure that amazonproduct can be imported
# from parent directory
import sys
sys.path.insert(0, '..')

from amazonproduct import API, AWSError
from amazonproduct.processors import objectify, etree, minidom

if __name__ == '__main__':

    #: how many times are all XML files parsed
    RUNS = 10

    custom_parsers = {
        'lxml.objectify': objectify.Processor(), 
        'lxml.etree': etree.Processor(module='lxml.etree'), 
        'xml.etree.cElementTree': etree.Processor(module='xml.etree.cElementTree'),
        'xml.etree.ElementTree': etree.Processor(module='xml.etree.ElementTree'),
        'cElementTree': etree.Processor(module='cElementTree'),
        'elementtree.ElementTree': etree.Processor(module='elementtree.ElementTree'),
        'minidom': minidom.Processor(), 
    }

    print "Collecting test files..."
    xml_files = [os.path.join(root, file)
        for root, dirs, files in os.walk('.')
        for file in files
        if os.path.splitext(file)[1].lower() == '.xml']

    print "Parsing %i XML files..." % (len(xml_files)*RUNS, )
    for label, parser in custom_parsers.items():
        print label, 
        if getattr(parser, 'etree', '') is None:
            print 'not installed!'
            continue
        start = time.clock()
        api = API(locale='de', processor=parser)
        for i in range(RUNS):
            for path in xml_files:
                try:
                    api._parse(open(path))
                except Exception, e:
                    pass

        stop = time.clock()
        print stop - start
