# twitter-history-to-wordpress
Imports tweets, images and videos from your tweet archive to your Wordpress blog

This script does some basic filtering on your tweets (no RT, no replies, no messages with many recipients), connects to your Wordpress blog via wordpress_xmlrpc and creates posts with images, videos and all the rest. The only thing we are missing, as far as I am concerned, is some way to progess gif files. Each post created has the date and time of the original tweet and is tagged "lessthan280chars". 

### Instructions

1. Go to <a href="https://github.com/mwichary/twitter-export-image-fill">twitter-export-image-fill</a> and follow the instructions to a T.
2. Download twitterToWordpress.py and place it in the root directory of your twitter archive.
3. Open twitterToWordpress.py and put your Wordpress blog credentials and URL on line 14. You may also want to change the default tag for your twitter posts to something other than 'lessthan280chars' on line 17.
4. Go to the root directory of your twitter archive and run `twitterToWordpress.py` there (using terminal/command line).


### Version history

**0.1 (23 Apr 2018)**
- First commit, quick and brutal, no niceties, no options, plug your values in the raw code
