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
import tumboxconfig


#Eclipse and others sometimes indicate an error on those first two. Ignore, I hope?

TEST = False

class ArchiverMain:

        def __init__(self):
            self.log_file = tumboxconfig.log_file
            self.musicdir = tumboxconfig.musicdir
            self.tumbox_db_file = tumboxconfig.db_file
            self.tumbox_db = {}
            self.skip_dirs = tumboxconfig.skip_dirs
            self.log_output = ''
            
                                
        def run(self):
                self._load_db()
                
                                
                processed = 0
                for subdir in filter(lambda x: x not in self.skip_dirs, self.getDirsPresent()):
                        if '.tumbox_guid' not in os.listdir(self.musicdir + '/' + subdir):
                                #we got a new one! generate the guid
                                self._log('Adding guid file to ' + subdir)
                                guid = hashlib.sha1(subdir + str(time.time())).hexdigest()
                                
                                f = open(self.musicdir+'/'+subdir+'/.tumbox_guid', 'w')
                                f.write(guid)
                                f.close()
                                #Don't log now - this is now marked to be logged next time
                        else:
                                #now, action depends on whether we have that guid in our db or not
                                f = open(self.musicdir+'/'+subdir+'/.tumbox_guid', 'r')
                                guid = f.read()
                                f.close()
                                if guid in self.tumbox_db:
                                    pass#nothing for now. could look for updates in the future
                                else:
                                    #We found but did not log last time. This means that we log(process) now
                                    if self._process_dir(self.musicdir+'/'+subdir, guid):
                                        self._log('Processed ' +subdir)
                                        processed += 1
                                        print 'Processing ' + subdir
                self._log(str(processed) + " processed")
                return processed
                
                        
        def _load_db(self):
                #for now, assume that it is a file
                try:
                    f = open(self.tumbox_db_file)
                    self.tumbox_db = json.load(f)
                    f.close()
                    self._log('Successfully loaded db')
                except:
                    self.fatal_error()
        
        def _save_db(self):
                f = open(self.tumbox_db_file, 'w')
                json.dump(self.tumbox_db, f, indent=5)
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
                        self.tumbox_db[guid] = obj
                        self.distribute(guid, obj)
                        return True
                else:
                        self._log('No info file found in ' + root)
                        return False
        
        def compose(self, folder_path, text):
                title = folder_path.rsplit("/")[-1]#folder_path better have / in it
                all_files = os.listdir(folder_path)
                doc = str(unicode(text, errors='ignore'))#convert to unicode as such to avoid weird errors with bad characters
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
                if len(musicfiles) == 1: return [musicfiles[0]]
                lines = text.split('\n')
                highlight_triggers = ['highlights:', 'standout tracks:']
                results = []
                for trigger in highlight_triggers:
                    highlightLines = [x for x in lines if x.lower().startswith(trigger)]
                    if len(highlightLines) == 0: continue
                    highlightLine = highlightLines[-1]#assume the last one is the one we want
                    sep = ';' if ';' in highlightLine else ',' #probably most often ',' but just to be safe
                    highlight_titles = highlightLine[len(trigger):].split(sep)
                    for songname in highlight_titles:
                        for musicfile in musicfiles:
                            #the check on isdigit is so that we will be able to make things prettier in blog                                
                            if (songname.lower() in musicfile.lower()) and not (songname[0].isdigit()): results.append(musicfile)
                    #Don't want to do this for more than one trigger, so break if we get here
                    break
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
                if tumboxconfig.local_archive: self.archive_locally(guid, obj)
                if tumboxconfig.email_people: self.email_people(guid, obj)
                if tumboxconfig.tumblr: self.blog(guid, obj)
                pass
        
        def archive_locally(self, guid, obj):
                archive_dir = tumboxconfig.archive_dir if not TEST else tumboxconfig.archive_test_dir
                f = open(archive_dir + '/' + obj['title'] + '.txt', 'w')
                f.write(obj['content'])
                
        def compose_email(self, guid, obj):
                subject = '['+tumboxconfig.email_shortname+'] New post from ' + (obj['author'] if obj['author'] is not None else 'someone in '+tumboxconfig.email_shortname)
                text = obj['title'] + '\n\n' + obj['content'] + '\n\n--------------\n\n' + tumboxconfig.email_sig
                return (subject, text)
        
        def send_email(self, subject, text):
                msg = MIMEMultipart()
                msg['From'] = tumboxconfig.mailer_email_address
                msg['To'] = tumboxconfig.mailer_email_address
                msg['Subject'] = subject
                
                msg.attach(MIMEText(text))
                        
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.ehlo()  
                server.starttls()
                server.ehlo()
                server.login(tumboxconfig.mailer_email_address, tumboxconfig.mailer_pw)
                response = server.sendmail(tumboxconfig.mailer_email_address,
                                tumboxconfig.email_address_list,
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
                media_dir = tumboxconfig.local_media_dir + '/' + guid
                os.system('mkdir ' + media_dir)
                
                full_path = tumboxconfig.musicdir + '/' + obj['title']
                
                #now, go ahead and check if this will be an audio post
                audio = (len(obj['highlights']) > 0) and full_path != ''
                
                #initialize text
                text = ''
                
                if audio:
                    sample_song = obj['highlights'][0]
                    song_path = full_path + '/' + sample_song
                    shutil.copy(song_path, media_dir)
                    
                    #Put in name of song that we decided to play: first, remove numbers from start
                    sample_song = sample_song[self.firstAlpha(sample_song):-4]
                    text += '<i>Playing - ' + sample_song + '</i>\n\n'
                    #And now the title
                    text += '<h2>' +obj['title'] + '</h2>\n\n'
                
                if obj['picture'] is not None:
                    from PIL import Image
                    pic_name = obj['picture']
                    pic_path = full_path + '/' + pic_name
                    img = Image.open(pic_path)
                    if img.size[0] > 500:
                    	#too wide, need to shrink
                    	ratio = img.size[1] / float(img.size[0])
                    	height = int(round(ratio * 500))
                    	img1 = img.resize((500, height), Image.ANTIALIAS)
                    	pic_name = '/resized-' + pic_name
                    	pic_path = full_path + '/' + pic_name
                    	img1.save(pic_path)
                    shutil.copy(pic_path, media_dir)
                    text += '<img src="' + tumboxconfig.hosted_media_url+'/'+guid+'/'+pic_name+'"/>\n\n'
              

                #now that we have media in place, can create our post
                text += obj['content']
                text = text.replace('\n', '<br/>')

                
                #create post params...
                if audio:
                    print 'gonna be an audio post'
                    params = {'externally_hosted_url':tumboxconfig.hosted_media_url+'/'+guid+'/'+obj['highlights'][0],
                              'caption':text}
                else:
                    print 'gonna be a text post'
                    params = {'title':obj['title'],
                              'body':text}
                if tumboxconfig.tumblr_blog not in ['', None]:
                    params['group'] = tumboxconfig.tumblr_blog
                if obj['author'] not in ['', None]:
                	params['tags'] = obj['author']
                
                #post that shit!
                pumblr.api.auth(tumboxconfig.tumblr_email, tumboxconfig.tumblr_pw)
                print params
                try:
                    if audio:
                        pumblr.api.write_audio(**params)
                    else:
                        pumblr.api.write_regular(**params)
                except:
                    self._log("Failed to post to tumblr, possibly some encoding issue")
                    
                    
        def firstAlpha(self, input):
            for x in range(len(input)):
                if input[x].isalpha(): return x
            return -1
             
if __name__ == "__main__":
        # sys.exit()
        archiver = ArchiverMain()
        num_processed = 0
        try:
        		num_processed = archiver.run()
        finally:
        		archiver.cleanup(num_processed)
