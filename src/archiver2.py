#!/usr/bin/env python
'''
The idea here is to be able to monitor a folder for changes. Specifically, additions. I think we 
are going to just look for an addition, and then pass that to the next function to
handle
'''

import os
import sys
import time
import json
import hashlib
from threading import Thread
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader

TEST = True

class ArchiverMain:


        config_file = ''#whoa now...
        log_file = 'log'
        dirs_present = []
        musicdir = '/Users/dan/Desktop/pyconfig'
        scan_period_secs = 60 * 60
        download_wait_secs = 60 * 10 if not TEST else 0
        mbp_db_file = ''
        mbp_db = {}
        skip_dirs = ['DOCS - plz read', 'For Shame']
        
        def __init__(self):
                self.dirs_present = self.getDirsPresent()
                                
        def run_that_shit(self):
                #self._load_db()
                for subdir in filter(lambda x: x not in self.skip_dirs, self.getDirsPresent()):
                        if '.mbp_guid' not in os.listdir(self.musicdir + '/' + subdir):
                                #we got a new one! generate and rock out w cock out
                                guid = hashlib.sha1(subdir + str(time.time())).hexdigest()
                                
                                f = open(self.musicdir+'/'+subdir+'/.mbp_guid', 'w')
                                f.write(guid)
                                f.close()
                        else:
                                print 'mbp_guid found in ' + subdir
                        print 'done'
        
                        
        def _load_db(self):
                #for now, assume that it is a file
                f = open(self.mbp_db_file)
                contents = f.read()
                f.close()
                self.mbp_db = json.loads(contents)
        
        def _log(self, text):
                pass#will want to print out and also write to a log file

        def fatal_error(self):
                print 'disaster'#will probably want to email me or something
                
        def getDirsPresent(self):
                return [x for x in os.listdir(self.musicdir) if os.path.isdir(self.musicdir + '/' + x)]
        
        #######################################
        ##This stuff copied from old archiver##
        ########################################
        
        def looksLikeMusic(self, name):
                print name
                return (name.endswith(".mp3")) or (name.endswith(".m4a")) or (name.endswith(".aac"))

        def readPlaintext(self, path):
                contents = ""
                with open(path) as f:
                        contents = f.read()
                f.closed
                return contents
        
        def readRtf(self, path):
                try:
                  doc = Rtf15Reader.read(open(path, "rb"))
                except:
                  print("Some screwy rtf shit going on with " + path)
                  return "Can't process ur shitty rtf <3 dfbot"
                contents = PlaintextWriter.write(doc).getvalue()
                #print contents
                return contents
     
class ArchiverWorker(Thread):
        def run(self, root):
                #first, sleep for several minutes to give this stuff time to download
                time.sleep(self.download_wait_secs)
                text = ''
                files = os.listdir(root)
                for filename in files:
                        if filename.endswith(".txt"):
                                text = readPlaintext(root + "/"+ filename)
                                break
                        if filename.endswith(".rtf"):
                                text = readRtf(root +"/"+ filename)
                                break
                        if filename.endswith(".rtfd"):
                                text = readRtf(root + '/' + filename + '/TXT.rtf')
                                break
                if text != '':
                        (title, doc) = self.compose(root, text)
                #now do what we will with this-- archive, email, blog, tweet....
                else:
                        pass#notify someone, or at least log something indicating that we failed to find any info
        
        def compose(self, folder_path, text):
                title = folder_path.rsplit("/")[-1]#folder_path better have / in it
                all_files = os.listdir(folder_path)
                doc = text
                doc +='\n\nTracklist:\n'
                tracks = filter(looksLikeMusic, all_files)
                if len(tracks) == 0: f.write( "No music :(")
                for track in tracks:
                    doc += (track[:-4] + "\n")
                highlightFiles = self._find_highlights(text, tracks)
                author = self._find_author(text)
                return (title, doc)

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
                
                
             
if __name__ == "__main__":
        archiver = ArchiverMain()
        #archiver.mainloop()
        archiver.run_that_shit()
