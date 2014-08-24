google-drive-cleaner
====================

Python script to scan through Google Drive, find orphaned files, and put them in the trash.

Google API Code
===============

The following were the steps I took to get this running.

 - Go to the APIs console at [https://code.google.com/apis/console](https://code.google.com/apis/console)
 - Create a project (no need to change the ID)
 - It will take a minute or so for the project to finish then you should be redirected to the project hompage
 - Under "APIs & Auth" click on APIs
   - Turn on Drive API and Drive SDK (I turned off the rest)
 - Under "APIs & Auth" click on Consent screen
   - (VERY IMPORTANT) Enter a Product Name and save the page.  You'll get hard-to-diagnose auth errors if you fail to do this.
 - Under "APIs & Auth" click on Credentials
   - Under the OAuth Section click "Create new Client ID"
   - Make sure you choose "Installed application" and "Other"
   - Clicking create should present you to the two pieces of data you need
   - Copy those values into config.py

Use (to assist non-programmers)
===============================

WARNING: This procedure is provided is provided "as is" without express or implied warranty.  The Google API includes commands that could result in the loss of data.  While the author believes the guide to be accurate, any number of things (including the Google API) could have changed since it was written.  If you elect to follow this guide, you take full responsibility for the consequences.  If you live in a country where the author cannot disclaim such a warranty, you are not licensed to use the following procedure.

 - Install Python
 - Install pip (http://pip.readthedocs.org/en/latest/installing.html)
 - Install the Google API by running "pip install --upgrade google-api-python-client"
 - Install another required library by runnign "pip install httplib2"
 - Using a command prompt, change directory into the folder that contains cleaner.py 
 - Start python.  In the python console (once you see >>>), run:
```
from cleaner import *
dc = build_connection()
```
This second command will prompt you to go to a URL in your browser and complete an authorization process.  Copy the string provided by Google and paste it back into the python console.  Pressing enter should complete the process successfully and you should see python loading all your files.

While the original author designed this to delete orphaned files, I strongly recommend that you create a folder (named something like "_delete") and move all your orphaned files/folders to this directory.  This will give you a chance to visually review all the files before deleting (and you can always delete the whole folder if that's what you really want to do).

To move files, navigate to the target Google Drive folder in your web browser.  The URL will end in something like "folders/0B1Bdl-YbgK8ZUWx0cVEtTklWdUU".  Everything after the '/' is the ID of the folder.  Using that ID, run the following substituting the ID for <folder>.  In the final command, the ID should be enclosed in quotes:
```
dc.moveItems("<folder id>")
```