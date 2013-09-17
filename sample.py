# -*- coding: utf-8 -*-

"""Command-line skeleton application for Compute Engine API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

To get detailed log output run:

  $ python sample.py --logging_level=DEBUG
"""

import gflags
import httplib2
import logging
import os
import pprint
import sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

import constants


FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret.
# You can see the Client ID and Client secret on the API Access tab on the
# Google APIs Console <https://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

API_VERSION = 'v1beta15'
GCE_URL = 'https://www.googleapis.com/compute/%s/projects/' % (API_VERSION)

# Helpful message to display if the CLIENT_SECRETS file is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to download the client_secrets.json file
and save it at:

   %s

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/compute',
      'https://www.googleapis.com/auth/compute.readonly',
      'https://www.googleapis.com/auth/devstorage.read_only',
      'https://www.googleapis.com/auth/devstorage.read_write',
    ],
    message=MISSING_CLIENT_SECRETS_MESSAGE)


# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')


def main(argv):
  # Let the gflags module process the command-line arguments
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
    sys.exit(1)

  # Set the logging according to the command-line flag
  logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

  # If the Credentials don't exist or are invalid, run through the native
  # client flow. The Storage object will ensure that if successful the good
  # Credentials will get written back to a file.
  storage = Storage('sample.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  auth_http = credentials.authorize(http)

  service = build('compute', 'v1beta15', http=auth_http)

  try:

    print "# Authentication Success! Now add code here."
    print "#### Please note the output is in YAML format :)"

    gce_service = build('compute', API_VERSION)
    project_url = GCE_URL + constants.PROJECT_ID

    # List instances
    request = gce_service.instances().list(project=constants.PROJECT_ID,
                                           filter=None, zone=constants.DEFAULT_ZONE)
    response = request.execute(auth_http)
    # response = request.execute(http)
    print "Instances in zone '{}':".format(constants.DEFAULT_ZONE)
    if response and 'items' in response:
      instances = response['items']
      for instance in instances:
        print "- {}".format(instance['name'])
    else:
      print '# No instances to list.'

    print "Available Zones: # with maintenance zone end"
    request = gce_service.zones().list(project=constants.PROJECT_ID, filter=None)
    response = request.execute(auth_http)
    if response and 'items' in response:
      zones = response['items']
      for zone in zones:
        maint_win = None
        if 'maintenanceWindows' in zone:
          maint_win = zone['maintenanceWindows']
        if maint_win:
          maint_win = zone['maintenanceWindows'][0]['endTime']
        print "- {} # {}".format(zone['name'], maint_win)

    # For more information on the Compute Engine API API you can visit:
    #
    #   https://developers.google.com/compute/docs/reference/v1beta15
    #
    # For more information on the Compute Engine API API python library surface you
    # can visit:
    #
    #   https://google-api-client-libraries.appspot.com/documentation/compute/v1beta15/python/latest/
    #
    # For information on the Python Client Library visit:
    #
    #   https://developers.google.com/api-client-library/python/start/get_started

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
