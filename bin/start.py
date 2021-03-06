#!/usr/bin/python

"""Start the Reporting API application using Paste Deploy.
"""

import logging
import os
from paste.deploy import loadapp
from paste.deploy import loadserver
import sys


if __name__ == '__main__':
    logging.basicConfig(
        filename='/var/log/reporting-api.log', level=logging.INFO
    )
    REALFILE = os.path.realpath(__file__)
    REALDIR = os.path.dirname(REALFILE)
    PARDIR = os.path.realpath(os.path.join(REALDIR, os.pardir))
    CONFDIR = os.path.join(PARDIR, 'reporting_api', 'conf')
    PASTE_CONFIG = os.path.join(CONFDIR, 'paste.config')
    sys.path.insert(0, PARDIR)
    REPORTING_APP = loadapp('config:' + PASTE_CONFIG)
    SERVER = loadserver('config:' + PASTE_CONFIG)
    SERVER(REPORTING_APP)
