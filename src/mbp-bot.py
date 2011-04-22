#!/usr/bin/python2.7
'''
The idea here is to be able to monitor a folder for changes. Specifically, additions. I think we 
are going to just look for an addition, and then pass that to the next function to
handle
'''

from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

import os
import sys
import time
import json
import hashlib
import shutil
import mbpconfig


#Eclipse and others sometimes indicate an error on those first two. Ignore, I hope?

TEST = False

class ArchiverMain:

        def __init__(self):
            self.log_file = mbpconfig.log_file
            self.musicdir = mbpconfig.musicdir
            self.mbp_db_file = mbpconfig.db_file
            self.mbp_db = {}
            self.skip_dirs = mbpconfig.skip_dirs
            self.log_output = ''
            
                                
        def run_that_shit(self):
                self._load_db()
#                for key in self.mbp_db.keys():
#                    self.mbp_db[key]['full_path'] = ''
#                self._save_db()
#                guid = self.mbp_db.keys()[1]
#                self.blog(guid, self.mbp_db[guid])
#                sys.exit()
                
                                
                processed = 0
                for subdir in filter(lambda x: x not in self.skip_dirs, self.getDirsPresent()):
                        if '.mbp_guid' not in os.listdir(self.musicdir + '/' + subdir):
                                #we got a new one! generate and rock out w cock out
                                guid = hashlib.sha1(subdir + str(time.time())).hexdigest()
                                
                                f = open(self.musicdir+'/'+subdir+'/.mbp_guid', 'w')
                                f.write(guid)
                                f.close()
                                #Don't log now - this is now marked to be logged next time
                        else:
                                #now, action depends on whether we have that guid in our db or not
                                f = open(self.musicdir+'/'+subdir+'/.mbp_guid', 'r')
                                guid = f.read()
                                f.close()
                                if guid in self.mbp_db:
                                    pass#nothing for now. could look for updates in the future
                                else:
                                    #We found but did not log last time. This means that we log now
                                    if self._process_dir(self.musicdir+'/'+subdir, guid):
                                        self._log('Processed ' +subdir)
                                        processed += 1
                                        print 'Processing ' + subdir
                self._log(str(processed) + " processed")
                return processed
                
                        
        def _load_db(self):
                #for now, assume that it is a file
                try:
                    f = open(self.mbp_db_file)
                    self.mbp_db = json.load(f)
                    f.close()
                    self._log('Successfully loaded db')
                except:
                    self.fatal_error()
        
        def _save_db(self):
                f = open(self.mbp_db_file, 'w')
                json.dump(self.mbp_db, f, indent=5)
                f.close()
        
        def _log(self, text):
                self.log_output += '\n' + text
                print text

        def fatal_error(self):
                self._log('Fatal Error, exiting')
                #will probably want to email me or something
                self.cleanup(0)
                
        def cleanup(self, processed):
                if processed > 0:
                    self._save_db()
                self._log('Exiting')
                f = open(self.log_file, 'a')
                f.write('\n********' +time.strftime("%a, %d %b %Y %H:%M") +'**********')
                f.write(self.log_output)
                f.close()
                
        def getDirsPresent(self):
                return [x for x in os.listdir(self.musicdir) if os.path.isdir(self.musicdir + '/' + x)]
            
        
        #######################################
        ##This stuff copied from old archiver##
        ########################################
        
        def looksLikeMusic(self, name):
                #print name
                return (name.endswith(".mp3")) or (name.endswith(".m4a")) or (name.endswith(".aac"))
                
        def looksLikeAPicture(self, name):
                extension = name[name.index('.')+1:]
                return (extension in ['jpg', 'jpeg', 'gif', 'png'])

        def readPlaintext(self, path):
                with open(path) as f:
                        contents = f.read()
                return contents
        
        def readRtf(self, path):
                try:
                    doc = Rtf15Reader.read(open(path, "rb"))
                except:
                    self._log("Some screwy rtf shit going on with " + path)
                    return "Can't process ur shitty rtf <3 dfbot"
                contents = PlaintextWriter.write(doc).getvalue()
                #print contents
                return contents
     
        def _process_dir(self, root, guid=None):
                text = ''
                files = os.listdir(root)
                for filename in files:
                        if filename.endswith(".txt"):
                                text = self.readPlaintext(root + "/"+ filename)
                                break
                        if filename.endswith(".rtf"):
                                text = self.readRtf(root +"/"+ filename)
                                break
                        if filename.endswith(".rtfd"):
                                text = self.readRtf(root + '/' + filename + '/TXT.rtf')
                                break
                if text != '':
                        obj = self.compose(root, text)
                        self.mbp_db[guid] = obj
                        self.distribute(guid, obj)
                        return True
                else:
                        self._log('No info file found in ' + root)
                        return False
        
        def compose(self, folder_path, text):
                title = folder_path.rsplit("/")[-1]#folder_path better have / in it
                all_files = os.listdir(folder_path)
                doc = text
                doc +='\n\nTracklist:\n'
                tracks = filter(self.looksLikeMusic, all_files)
                tracks.sort()
                if len(tracks) == 0: doc += "No music :("
                for track in tracks:
                    doc += (track[:-4] + "\n")
                highlightFiles = self._find_highlights(text, tracks)
                author = self._find_author(text)
                picture = self._find_picture(all_files)
                retMap = {
                          'content':doc,
                          'author':author,
                          'found_on':time.time(),
                          'highlights':highlightFiles,
                          'title':title,
                          'picture':picture
                          }
                return retMap
    
        def _find_highlights(self, text, musicfiles):
                lines = text.split('\n')
                highlightLines = [x for x in lines if x.lower().startswith('highlights:')]
                if len(highlightLines) == 0: return []
                highlightLine = highlightLines[-1]#assume the last one is the one we want
                sep = ';' if ';' in highlightLine else ',' #probably most often ',' but just to be safe
                titles = highlightLine[len('highlights:'):].split(sep)
                results = []
                for musicfile in musicfiles:
                        if any(songname in musicfile for songname in titles): results.append(musicfile)
                return results
    
        def _find_author(self, text):
                lines = text.split('\n')
                authorLines = [x for x in lines if x.startswith('-')]
                if len(authorLines) == 0: return None
                authorLine = authorLines[0] #this time assume first: people sometimes use - in comments
                return authorLine[1:].strip()
        
        '''
        Given list of files in a directory, try to extract which one is cover art
        '''
        def _find_picture(self, filenames):
                img_files = [x for x in filenames if self.looksLikeAPicture(x)]
                if len(img_files) < 1: return None
                good_names = ['Folder.jpg', 'folder.jpg', 'cover.jpg', 'front.jpg']
                for name in good_names:
                    if name in img_files: return name
                return img_files[0]
        
        '''
        This is where we save our post object to various sources. Uncomment and add for different sources
        '''    
        def distribute(self, guid, obj):               
                print obj['content']#This shit is seriously just for testing
                if mbpconfig.local_archive: self.archive_locally(guid, obj)
                if mbpconfig.email_people: self.email_people(guid, obj)
                if mbpconfig.tumblr: self.blog(guid, obj)
                pass
        
        def archive_locally(self, guid, obj):
                archive_dir = mbpconfig.archive_dir if not TEST else mbpconfig.archive_test_dir
                f = open(archive_dir + '/' + obj['title'] + '.txt', 'w')
                f.write(obj['content'])
                
        def compose_email(self, guid, obj):
        		rawk = '_+880______________________________\n_++88______________________________\n_++88______________________________\n__+880__________________________++_\n__+888_________________________+88_\n__++880________________________+88_\n__++888_______+++88__________++88__\n__+++8888__+++88880++888____+++88__\n___++888+++++8888+++888888+++888___\n___++88++++88888+++8888888++888____\n___+++++++88888888888888888888_____\n___++++++++88888888888888888888____\n___+++++++++0088888888888888888____\n____++++++++0088888888888888888____\n_____++++++++000888888888888888____\n_____+++++++++08888888888888888____\n______++++++++0888888888888888_____\n________+++++++88888888888888______\n________+++++++88888888888888______'
                subject = '[MBP] New post from ' + (obj['author'] if obj['author'] is not None else 'someone in mbp')
                text = obj['title'] + '\n\n' + obj['content'] + '\n\n--------------\n\n' + rawk
                return (subject, text)
        
        def send_email(self, subject, text):
                msg = MIMEMultipart()
                msg['From'] = mbpconfig.mailer_email_address
                msg['To'] = mbpconfig.mailer_email_address
                msg['Subject'] = subject
                
                msg.attach(MIMEText(text))
                        
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.ehlo()  
                server.starttls()
                server.ehlo()
                server.login(mbpconfig.mailer_email_address, mbpconfig.mailer_pw)
                response = server.sendmail(mbpconfig.mailer_email_address,
                                mbpconfig.email_address_list,
                                msg.as_string())
                if len(response) != 0:
                     self._log('Possibly some trouble with emailing: ' +str(response))
                server.close()
                
        def email_people(self, guid, obj):
                try:
                    subject, text = self.compose_email(guid, obj)
                    self.send_email(subject, text)       
                except:
                    self._log("Some kind of disastrous error occurred while emailing " + obj['title'])
                    
        def blog(self, guid, obj):
                import pumblr
                #first, need to copy media to hosted dirs
                #actually, only if we have a highlight and/or a picture 
                #but, going to just go ahead and make the dir anyway
                media_dir = mbpconfig.local_media_dir + '/' + guid
                os.system('mkdir ' + media_dir)
                
                full_path = mbpconfig.musicdir + '/' + obj['title']
                
                #now, go ahead and check if this will be an audio post
                audio = (len(obj['highlights']) > 0) and full_path != ''
                
                #initialize text
                text = ''
                
                if obj['picture'] is not None:
                    pic_path = full_path + '/' + obj['picture']
                    shutil.copy(pic_path, media_dir)
                    text = '<img src="' + mbpconfig.hosted_media_url+'/'+guid+'/'+obj['picture']+'"/>\n\n'
                if audio:
                    song_path = full_path + '/' + obj['highlights'][0]
                    shutil.copy(song_path, media_dir)                

                #now that we have media in place, can create our post
                text += obj['content'] if not audio else obj['title'] + '\n\n' + obj['content']
                
                #create post params...
                if audio:
                    print 'gonna be an audio post'
                    params = {'externally_hosted_url':mbpconfig.hosted_media_url+'/'+guid+'/'+obj['highlights'][0],
                              'caption':text}
                else:
                    print 'gonna be a text post'
                    params = {'title':obj['title'],
                              'body':text}
                if mbpconfig.tumblr_blog not in ['', None]:
                    params['group'] = mbpconfig.tumblr_blog
                if obj['author'] not in ['', None]:
                	params['tags'] = obj['author']
                
                #post that shit!
                pumblr.api.auth(mbpconfig.tumblr_email, mbpconfig.tumblr_pw)
                print params
                try:
                    if audio:
                        pumblr.api.write_audio(**params)
                    else:
                        pumblr.api.write_regular(**params)
                except:
                    self._log("Failed to post to tumblr, possibly some encoding issue")
             
if __name__ == "__main__":
        #sys.exit()
        archiver = ArchiverMain()
        num_processed = 0
        try:
        		num_processed = archiver.run_that_shit()
        finally:
        		archiver.cleanup(num_processed)
