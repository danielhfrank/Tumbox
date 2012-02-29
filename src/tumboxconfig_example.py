'''
Config file for tumbox

Created on Apr 3, 2011

@author: dan
'''

#Music directory - where it all goes down. Absolute path required
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

#Log file - log output will be stored here. Absolute path
log_file = ''

#======DB==============================


# dbtype = 'file'
dbtype = 'mongo'

# db_file = '/Users/dan/Dropbox/.mbp_helpers/mbp_db.json'

#MONGO
mongo_host = ''
mongo_port = 29117
mongo_dbname = ''
mongo_user = ''
mongo_pw = ''

#=========================================

#Send to an email list?
email_people = True

#List of emails
email_address_list = ['email1@exmaple.com',
					  'email2@example.com'
                      ]
email_shortname = 'Tumbox' #this is for email subject line
email_sig = 'Sent by Tumbox'

mailer_email_address = ''
mailer_pw = ''

#Post to tumblr?
tumblr = True

#account info
tumblr_email = ''
tumblr_pw = ''
#You can leave this one blank if you only have one blog on your account
tumblr_blog = ''

#hosting stuff - you will probably want to make a media folder within your dropbox folder for this
#
local_media_dir = '/path/to/your/dropbox/public/media/folder'
hosted_media_url = 'http://dl.dropbox.com/u/fill_in_this_number/possibly_a_subfolder_if_you_made_one'


