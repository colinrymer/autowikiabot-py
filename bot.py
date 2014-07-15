#! /usr/bin/env python2
import praw
from wikia import wikia
from util import *
import sys
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

BASE_URL = "wikia.com/wiki/"
REPLY_MESSAGE = "^(Want to help make this better? Check out the) [^source ^code](https://github.com/Timidger/WikiaBot)"

def login():
    bot = praw.Reddit("Wikia Bot: The wikia version of autowikipedia bot")

    with open("datafile.inf", "r") as login_details:
        USER = login_details.readline().strip()
        PASSWORD = login_details.readline().strip()

    bot.login(USER, PASSWORD)
    print("Logged in!")
    return bot

#sub_wikia = str(sys.argv[2])

def check_user(user):
    # If they deleted the comment
    if user is None:
        return False
    if user == USER:
        return False
    return True

def not_posted(post):
    for comment in post.replies:
        if comment.author is None:
            return False
        if comment.author.name == USER:
            return False
    else:
        return True

def find_link(body):
    begin_index = body.find("http://")
    for index, char in enumerate(body[begin_index:]):
        if char in (" ", ")"):
            end_index = index + begin_index
            break
    else:
        end_index = begin_index + index
    link = body[begin_index: end_index]
    return link

def find_title(link):
    begin_index = link.find(BASE_URL)
    title = link[begin_index:].partition(BASE_URL)[-1]
    # Translate from a title in a url to a proper title
    title = unquote(title)
    title = title.replace("-", " ")
    title = title.replace("_", " ")
    return title

def find_sub_wikia(link):
    # Just after http://, maybe should be more explicit here
    start_index = link.find("//") + 2
    end_index = link.find(".")
    if wikia.LANG:
        start_index = end_index
        end_index = link.find(".", start_index + 1)
    return link[start_index:end_index]

def get_message(title, link, summary):
    BASE_MESSAGE = "\n".join(("[{title}]({link})",
                              "---",
                              ">{body}",
                              "---",
                              REPLY_MESSAGE,
                            ))
    return BASE_MESSAGE.format(title=title, link=link, body=summary)
                   
if __name__ == "__main__":
    bot = login()
    sub_reddit = str(sys.argv[1])
    while True:
        try:
            for post in praw.helpers.comment_stream(bot, sub_reddit, limit=None, verbosity=0):
                if BASE_URL in post.body and check_user(post.author.name) and not_posted(post):
                    print("Found a post to reply to!")
                    link = find_link(post.body)
                    print("Link: ", link)
                    title = find_title(link)
                    print("Title: ", title)
                    sub_wikia = find_sub_wikia(link)
                    print("Sub-Wikia:", sub_wikia)
                    summary = wikia.summary(title, sub_wikia)
                    message = get_message(title, link, summary) 
                    # Quick hack until we fix the Wikia library
                    if "REDIRECT" in message:
                        continue
                    post.reply(message)
        # Just gotta keep chugging along
        except Exception as e:
            fail(e)
            print(post.body)
