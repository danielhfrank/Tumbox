'''
Config file for mbp-bot

Created on Apr 3, 2011

@author: dan
'''

#Music directory - where it all goes down
musicdir = ''

#Skip Directories - list any subdirs that you don't want to follow.
#DON'T write out absolute paths
skip_dirs = []


#Write to an archives folder?
local_archive = True

#Archive folder (absolute path!)
archive_dir = ''

#Test archive folder (probably don't mess with this unless you are monkeying with code"
archive_test_dir = ''

#Log file - log output will be stored here.. someday
log_file = ''

#DB file - if using a filesystem 'db'
db_file = ''

#Send to an email list?
email_people = True

#List of emails
email_address_list = ['email1@exmaple.com',
					  'email2@example.com'
                      ]

mailer_email_address = ''
mailer_pw = ''

#Post to tumblr?
tumblr = True

#account info
tumblr_email = ''
tumblr_pw = ''
#You can leave this one blank if you only have one blog on your account
tumblr_blog = ''

#hosting stuff
local_media_dir = '/path/to/your/droppages/media/folder'
hosted_media_url = 'http://your-droppages-site.droppages.com'


