import praw
from wikia import wikia
import sys

BASE_URL = "wikia.com/wiki/"
REPLY_MESSAGE = "^(Want to help make this better? Check out the [source code](https://github.com/Timidger/WikiaBot))"


bot = praw.Reddit("Wikia Bot: The wikia version of autowikipedia bot")

with open("datafile.inf", "r") as login_details:
    USER = login_details.readline().strip()
    PASSWORD = login_details.readline().strip()

bot.login(USER, PASSWORD)
print("Logged in!")

sub_reddit = str(sys.argv[1])
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
    for index, char in enumerate(body):
        if char in (" ", ")"):
            end_index = index
            break
    else:
        end_index = index
    link = body[begin_index:end_index + 1]
    return link

def find_title(link):
    begin_index = link.find(BASE_URL)
    title = link[begin_index:].partition(BASE_URL)[-1]
    # Translate from a title in a url to a proper title
    title = title.replace("%27", "'")
    title = title.replace("_", " ")
    return title

def find_sub_wikia(link):
    # Just after http://, maybe should be more explicit here
    start_index = link.find("//") + 2
    end_index = link.find(".")
    if wikia.LANG:
        start_index = end_index
        end_index = link.find(".", start_index + 1)
    print(start_index, end_index)
    return link[start_index:end_index]

def get_message(title, link, summary):
    BASE_MESSAGE = "\n".join(("[{title}]({link})",
                              "---",
                              ">{body}",
                              "---",
                            ))
    return BASE_MESSAGE.format(title=title, link=link, body=summary)
                   

while True:
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
            post.reply(message)
