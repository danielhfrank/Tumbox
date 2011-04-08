#!/usr/bin/python2.7
'''
The idea here is to be able to monitor a folder for changes. Specifically, additions. I think we 
are going to just look for an addition, and then pass that to the next function to
handle
'''

from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader

import os
import sys
import time
import json
import hashlib
import mbpconfig


#Eclipse and others sometimes indicate an error on those first two. Ignore, I hope?

TEST = True

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
                if processed > 0:
                    self._save_db()
                self._log('Exiting')
                        
        def _load_db(self):
                #for now, assume that it is a file
                try:
                    f = open(self.mbp_db_file)
                    self.mbp_db = json.load(f)
                    f.close()
                    self._log('Successfully loaded db')
                except:
                    self.mbp_db = {}#THIS IS TEMPORARY to make sure we don't beef over empty file. DANGER
        
        def _save_db(self):
                f = open(self.mbp_db_file, 'w')
                json.dump(self.mbp_db, f, indent=5)
                f.close()
        
        def _log(self, text):
                self.log_output += '\n' + text
                print text

        def fatal_error(self):
                print 'disaster'#will probably want to email me or something
                
        def cleanup(self):
                f = open(self.log_file, 'a')
                f.write('********' +time.strftime("%a, %d %b %Y %H:%M") +'**********')
                f.write(self.log_output)
                f.close()
                
        def getDirsPresent(self):
                return [x for x in os.listdir(self.musicdir) if os.path.isdir(self.musicdir + '/' + x)]
            
        
        #######################################
        ##This stuff copied from old archiver##
        ########################################
        
        def looksLikeMusic(self, name):
                print name
                return (name.endswith(".mp3")) or (name.endswith(".m4a")) or (name.endswith(".aac"))

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
                if len(tracks) == 0: doc += "No music :("
                for track in tracks:
                    doc += (track[:-4] + "\n")
                highlightFiles = self._find_highlights(text, tracks)
                author = self._find_author(text)
                retMap = {
                          'content':doc,
                          'author':author,
                          'found_on':time.time(),
                          'highlights':highlightFiles,
                          'title':title
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
        This is where we save our post object to various sources. Uncomment and add for different sources
        '''    
        def distribute(self, guid, obj):               
                print obj['content']#This shit is seriously just for testing
                if mbpconfig.local_archive: self.archive_locally(guid, obj)
                pass
        
        def archive_locally(self, guid, obj):
                archive_dir = mbpconfig.archive_dir if not TEST else mbpconfig.archive_test_dir
                f = open(archive_dir + '/' + obj['title'] + '.txt', 'w')
                f.write(obj['content'])        
                
             
if __name__ == "__main__":
        archiver = ArchiverMain()
        #archiver.mainloop()
        archiver.run_that_shit()
        archiver.cleanup()
