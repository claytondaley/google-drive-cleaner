#!/usr/bin/python

import httplib2
import pprint
import sys

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials


class DriveCleaner():

	def __init__(self, drive_service):
		self.drive = drive_service
		self.requests = 0
		self.total = 0
		self.trashed = 0
		self.errors = 0


	def __str__(self):
		return str(self.total) + ' processed so far, ' + str(self.trashed) + ' trashed, ' + str(self.errors) + ' errors'


	def cleanFiles(self):

		keep_going = True
		next_token = None

		while keep_going:

			self.requests += 1
			print 'Making request ' + str(self.requests)

			f = self.drive.files().list(maxResults = 1000, pageToken = next_token).execute()
			try:
				next_token = f['nextPageToken']
			except KeyError:
				next_token = None
				keep_going = False

			self.total += len(f['items'])
			print str(self)

			self.processItems(f['items'])

		print str(self)


	def processItems(self, responseItemDict):

		for item in responseItemDict:

			# find items with no parents
			if len(item['parents']) == 0:

				# that belong only to the user
				if len(item['owners']) == 1 and item['owners'][0]['isAuthenticatedUser']:

					# ... check to see if already trashed
					if item['labels'] and item['labels']['trashed']:
						# print '\tAlready in trash: ' + item['title'] + ' - ' + item['id']
						pass

					else:
						print '\tTrashing: ' + item['title'] + ' - ' + item['id']
						try:
							self.drive.files().trash(fileId = item['id']).execute()
							self.trashed += 1
						except:
							print '\t\t>>> ERROR TRASHING THIS FILE <<<'
							self.errors += 1


def main():

	# Copy your credentials from the APIs Console
	CLIENT_ID = 'SOME_NUMBER_GOES_HERE.apps.googleusercontent.com'
	CLIENT_SECRET = 'SOME_SECRET_GOES_HERE'

	# Check https://developers.google.com/drive/scopes for all available scopes
	OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

	# Redirect URI for installed apps
	REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

	# Run through the OAuth flow and retrieve credentials
	flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
	authorize_url = flow.step1_get_authorize_url()
	print 'Go to the following link in your browser: ' + authorize_url
	code = raw_input('Enter verification code: ').strip()
	credentials = flow.step2_exchange(code)

	# Create an httplib2.Http object and authorize it with our credentials
	http = httplib2.Http()
	http = credentials.authorize(http)
	drive_service = build('drive', 'v2', http=http)

	# Create drivecleaner and run it
	dc = DriveCleaner(drive_service)
	dc.cleanFiles()


# intialize global utiltiy classes and call main
pp = pprint.PrettyPrinter()
main()








