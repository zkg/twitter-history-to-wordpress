from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import media,posts
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import taxonomies
from datetime import datetime
import json
import os.path
import re
import sys
import time
import mimetypes

client = Client(url="https://www.yourBlogUrl.com/xmlrpc.php", username="wpUsername", password="wpPassword")

TAG_RE = re.compile(r'<[^>]+>')
tags = client.call(taxonomies.GetTerms('post_tag',{'search':'lessthan280chars'}))
for date in index:
    try:
        year_str = '%04d' % date['year']
        month_str = '%02d' % date['month']
        data_filename = 'data/js/tweets/%s_%s.js' % (year_str, month_str)
        with open(data_filename) as data_file:
            data_str = data_file.read()
            # Remove the assignment to a variable that breaks JSON parsing,
            # but save for later since we have to recreate the file
            first_data_line = re.match(r'Grailbird.data.tweets_(.*) =', data_str).group(0)
            data_str = re.sub(first_data_line, '', data_str)
            #if (year_str == "2017"):
            data = json.loads(data_str)
            for tweet in data:
                #exclude retweets. There should be a better way, but I'm lazy
                if (tweet['text'].startswith('RT')):
                    continue
                #exclude reply tweets
                if 'in_reply_to_status_id' in tweet:
                    continue
                #if this is a conversation with many people, bail
                if (len(tweet['entities']['user_mentions']) > 1):
                    continue
                if (len(tweet['entities']['user_mentions']) == 1):
                    recipient = tweet['entities']['user_mentions'][0]['name']
                mediaurls = []
                #process all media in tweet
                for mediafile in tweet['entities']['media']:
                    expanded_url = mediafile['expanded_url']
                    #risky heuristics ahead
                    if "video" in expanded_url:
                        filename = mediafile['media_url'][:-5] + "video-"+mediafile['media_url'][len(mediafile['media_url'])-5:-4]+".mp4"
                        if os.path.isfile(filename) == False:
                            filename = mediafile['media_url']  
                    else:
                        filename = mediafile['media_url']  
                    # prepare metadata
                    data = {}
                    data['type'] = mimetypes.guess_type(filename)[0]
                    data['name'] = os.path.basename(filename)
                    # read the binary file and let the XMLRPC library encode it into base64
                    with open(filename, 'rb') as img:
                            data['bits'] = xmlrpc_client.Binary(img.read())
                    #upload media to xmlrcp server
                    response = client.call(media.UploadFile(data))
                    #link only if we recognize the data type: image or video
                    if data['type'].startswith('image'):
                        mediaurls.append("<br>\n<img src=\""+response['link']+"\">")
                    if data['type'].startswith('video'):
                        mediaurls.append("<br>\n<video controls> <source src=\""+response['link']+"\" type=\""+data['type']+"\"></video>")
                    #mediaurls.append(media['media_url'])
                urls = []
                #save all links in tweet...
                for url in tweet['entities']['urls']:
                    #...except for links within twitter. We hate those.
                    if "https://twitter.com" in url['expanded_url']:
                        continue
                    else:
                        urls.append(url['expanded_url'])
                newtweet = ""
                len(tweet['entities']['user_mentions'])
                i=0
                for word in tweet['text'].split():
                    if (word.startswith('@')):
                        newtweet = newtweet + recipient + " "
                        continue
                    if (word.startswith('#')):
                        newtweet = newtweet + word[1:] + " "
                        continue
                    if (word.startswith('https://t.co/')):
                        #if we still have links, add a link
                        if (i<len(urls)):
                            #accounting for wordpress autoembed capabilities
                            if "https://www.youtube.com/" in urls[i] or "https://www.vimeo.com/" in urls[i] or "https://vimeo.com/" in urls[i] or "https://youtu.be" in urls[i]:
                                newtweet = newtweet + "<br>\n" + urls[i] + " "
                            else:
                                newtweet = newtweet + "<br>\n<a target=\"_blank\" href=\"" + urls[i] + "\">" + urls[i] + "</a> "
                            i += 1
                            continue
                        #else add an image to the new tweet
                        else:
                            for mediaurl in mediaurls:
                                newtweet = newtweet + mediaurl + " "   
                            continue
                    #if we are still around, this is just a boring, normal word
                    newtweet = newtweet + word + " "
                #let's compose our blogpost
                post = WordPressPost()
                #pick first 8 words for title
                post.title = ' '.join(TAG_RE.sub('', newtweet).split()[:8])
                post.content = newtweet
                post.terms = tags
                post.date = datetime.strptime(tweet['created_at'].split()[0]+" "+tweet['created_at'].split()[1], '%Y-%m-%d %H:%M:%S')
                post.post_status = 'publish'
                post.id = client.call(posts.NewPost(post))
                #print (newtweet)
            
    except KeyboardInterrupt:
        print("")
        print("Interrupted! Come back any time.")
        sys.exit()
