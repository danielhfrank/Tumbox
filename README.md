# Tumbox #
Dropbox shared music folder --> Tumblr music blog 


---

**Motivation**: You participate in a Dropbox shared folder in which music albums are shared frequently. You usually leave some sort of text or .rtf file with the albums to describe what they are - *right now nothing will happen without some sort of info file - I will make it possible to blog without one soon*. You want a record of what's been shared and/or want to be able to notify members when a new album is posted and/or want to show people outside your shared folder a glimpse of what is being shared. You kind of want to prove that this can all be done without renting any server space, just by using Dropbox.

---

**Setup**: 
1. Fill out the config file (from the example) as fits your needs. Afterwards you *must* rename it to tumboxconfig.py

2. Set up tumbox-bot to run as a [cron job](http://en.wikipedia.org/wiki/Cron); recommended that you run every half hour.

(One day there will be an installation script....)

---

**Working Example**: [Music Butt Pirate](http://musicbuttpirate.tumblr.com)

___

***What exactly is it doing?***: Tumbox leaves behind a tiny hidden file in each of your album folders and uses the contents of that file to determine whether it has already logged that album. Every time it runs it will check to see if there are new albums that it hasn't logged, and at the end of this process keep a record of everything it has stored in its database (at time of writing, this is just a json file... sorry I'm not sorry)

---

***Help! I don't know what to do with the config file! Can I see yours?***: No, it's full of sensitive info! But feel free to shoot me a message here if you want help setting yourself up

---

## Important Notes for those who have made it this far ##

 At this time I haven't implemented anything to automatically clean up certain resources that could grow indefinitely. Specifically, the log file will probably start to stack up pretty quickly. Also, hosted preview songs and images will pile up in your Dropbox public folder. You will probably want to delete those. In future versions both of these tasks will be automated