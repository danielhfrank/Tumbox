"""
Tool to archive info files found in MBP

@author: dan
"""

import os
import sys
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader
from datetime import datetime

TEST = True

Desktop = "/Users/dan/Desktop"# for testing
MBP = "/Users/dan/Dropbox/Music Butt Pirate"
DOCS = MBP + "/DOCS - plz read"
archives_dir = (Desktop if TEST else DOCS) + "/Archives/"
ignoreThese = [DOCS, MBP + "/For Shame", MBP + "/APPS FTW"]
def run():
    full_tree = os.walk(MBP)
    for root, dirs, files in full_tree:
        print root + " - "
        print files
        if root == MBP: continue #toplevel text
        if any(ignoreThis in root for ignoreThis in ignoreThese): continue
        if root.endswith(".rtfd"):
            TXT = ""
            for filename in files:
                if(filename == "TXT.rtf"):
                    TXT = filename
            text = readRtf(root + "/" + filename)
            log_item(root[:root.rfind("/")], text)
            continue
        text = ""
        for filename in files:
            if filename.endswith(".txt"):
                text = readPlaintext(root + "/"+ filename)
                break
            if filename.endswith(".rtf"):
                text = readRtf(root +"/"+ filename)
                break
        if text != "": log_item(root, text)




def log_item(folder_path, text):
    title = folder_path.rsplit("/")[-1]#folder_path better have / in it
    #Deal with item possibly already existing
    with open(archives_dir + title + ".txt", "w") as f:
        all_files = os.listdir(folder_path)
        approved = any(filename == "BdfL approve.JPG" for filename in all_files)
        f.write(title + "\n")
        f.write("Logged ")
        f.write(datetime.now().strftime("%m/%d/%y"))
        f.write(" by dfbot")
        f.write("\n")#another blank line can't hurt
        f.write("\n")#another blank line can't hurt
        f.write(text)
        f.write("\n")#another blank line can't hurt
        if approved:
            f.write("\n***BdfL APPROVED***\n")
        f.write("\n")#another blank line can't hurt
        f.write("Tracklist:")
        f.write("\n")#another blank line can't hurt
        tracks = filter(looksLikeMusic, all_files)
        if len(tracks) == 0: f.write( "No music :(")
        for track in tracks:
            f.write( track[:-4] + "\n")
    f.closed#still not even sure this is necessary
                        



def looksLikeMusic(name):
    return (name.endswith(".mp3")) or (name.endswith(".m4a")) or (name.endswith(".aac"))

def readPlaintext(path):
    contents = ""
    with open(path) as f:
        contents = f.read()
    f.closed
    return contents

def readRtf(path):
    contents = ""
    try:
      doc = Rtf15Reader.read(open(path, "rb"))
    except:
      print("Some screwy rtf shit going on with " + path + ", exiting")
      return "Can't process ur shitty rtf <3 dfbot"
    contents = PlaintextWriter.write(doc).getvalue()
    print contents
    return contents



if __name__ == "__main__":
    run()
