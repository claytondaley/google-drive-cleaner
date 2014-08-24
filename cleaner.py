#!/usr/bin/python

import httplib2
from pprint import pprint

import apiclient.discovery
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow

from config import *


def update_permission(service, file_id, permission_id, new_role):
    """Update a permission's role.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to update permission for.
        permission_id: ID of the permission to update.
        new_role: The value 'owner', 'writer' or 'reader'.

    Returns:
        The updated permission if successful, None otherwise.
    """
    try:
        # First retrieve the permission from the API.
        permission = service.permissions().get(
            fileId=file_id, permissionId=permission_id).execute()
        permission['role'] = new_role
        return service.permissions().update(
            fileId=file_id, permissionId=permission_id, body=permission).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None


class DriveCleaner():
    def __init__(self, drive_service):
        self.drive = drive_service
        self.requests = 0
        self.total = 0
        self.moved = 0
        self.trashed = 0
        self.errors = 0
        self.files = []

    def __str__(self):
        return 'This session, ' + str(self.moved) + ' moved, ' + str(self.trashed) + ' trashed, ' + str(
            self.errors) + ' errors, with ' + str(self.total) + ' files currently listed'

    def updateFiles(self):
        keep_going = True
        next_token = None
        self.files = []
        self.requests = 0
        self.total = 0
        while keep_going:
            self.requests += 1
            print 'Making request ' + str(self.requests)
            f = self.drive.files().list(maxResults=1000, pageToken=next_token).execute()
            try:
                next_token = f['nextPageToken']
            except KeyError:
                next_token = None
                keep_going = False
            self.total += len(f['items'])
            self.files.extend(f['items'])
        print str(self)

    def noParents(self):
        return [x for x in self.files if len(x['parents']) == 0];

    def noParentsMine(self):
        return [x for x in self.noParents() if
                len(x['owners']) == 1 and x['owners'][0]['isAuthenticatedUser']]

    def trashItems(self, reload_files=False):
        if len(self.files) == 0 or reload_files:
            self.updateFiles()
        # find items with no parents owned by me
        for item in self.noParents:
            # ... check to see if already trashed
            if item['labels'] and item['labels']['trashed']:
                # print '\tAlready in trash: ' + item['title'] + ' - ' + item['id']
                pass
            else:
                print '\tTrashing: ' + item['title'] + ' - ' + item['id']
                try:
                    self.drive.files().trash(fileId=item['id']).execute()
                    self.trashed += 1
                except:
                    print '\t\t>>> ERROR TRASHING THIS FILE <<<'
                    self.errors += 1
        self.updateFiles()
        print str(self)

    def moveItems(self, folder, reload_files=False):
        """
        MoveItems will move all orphaned files into a particular folder.  Unlike trashItems,
        this function does not care whether the files are shared so long as they are owned
        by the current user.  Restricting the search to the current user avoids moving files
        owned by others that are "orphaned" because they are still in the "Shared with me"
        or "Incoming" folder).

        Arguments:
            folder (string): the id of the target folder
            reload_files (bool): optional, updateFiles before running the move
        """
        if len(self.files) == 0 or reload_files:
            self.updateFiles()
        # find items with no parents owned by me
        for item in self.noParentsMine():
            # ... check to see if already trashed
            if item['labels'] and item['labels']['trashed']:
                # print '\tAlready in trash: ' + item['title'] + ' - ' + item['id']
                pass
            else:
                print '\tMoving: ' + item['title'] + ' - ' + item['id']
                try:
                    self.drive.parents().insert(fileId=item['id'], body={'id': folder}).execute()
                    self.moved += 1
                except errors.HttpError, error:
                    print '\t\t>>> ERROR MOVING THIS FILE <<<'
                    print '%s' % error
                    self.errors += 1
        self.updateFiles()
        print str(self)


def build_connection():
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)
    drive_service = apiclient.discovery.build('drive', 'v2', http=http)

    # Create drivecleaner and run it
    dc = DriveCleaner(drive_service)
    dc.updateFiles()
    return dc