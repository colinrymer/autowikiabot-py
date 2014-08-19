# -*- coding: utf-8 -*-
import urllib2
import collections

import util
import constants

# Counts each time /u/autowikibot replies to a user (user stored by id)
# This is so /u/autowikibot isn't spammed and doesn't over reply
SUBMISSION_COUNTER = collections.Counter()
# A simple counter to determine how many posts have been submitted
TOTAL_POSTED = 0

def is_summon_chain(post, bot):
    """Determines if posting a reply would be part of a chain of replies. A
    Reddit bot instance is required to check the parent author through
    comment ids"""
    if not post.is_root:
        parent_comment_id = post.parent_id
        parent_comment = bot.get_info(thing_id=parent_comment_id)
        author = parent_comment.author
        if author is not None and author.name == constants.BOT_NAME:
            return True
    return False

def comment_limit_reached(post):
    """If the post was made in a /u/autowikibot's private sub, in
    /r/todayilearned, or /r/autowikibot, then this returns False. Those subs,
    either for testing for purposes or because of the nature of the sub, have
    no limitations on post count. As well each user can be replied to a total
    of four (4) times before /u/autowikibot will stop replying (so as not be
    annoying, and so spam bot cannot take advantage of /u/autowikibot"""
    count_of_this = SUBMISSION_COUNTER[str(post.submission.id)]
    # These are subs that don't have post limits
    bad_subs = ('autowikibotdelreq', 'todayilearned', constants.BOT_NAME)
    if count_of_this > 4 and str(post.subreddit) not in bad_subs:
        return True
    return False

def is_already_done(post):
    for reply in post.replies:
        # If /u/autowikibot has already responded,
        # or /u/Text_Reader_Bot is mirroring, then the bot already replied
        summarizers = (constants.BOT_NAME, "Text_Reader_Bot")
        if reply.author is not None and reply.author.name in summarizers:
            #util.warn("%s IS ALREADY DONE"%post.id)
            return True
    return False

def post_reply(reply, post):
    """Attempts to post the reply to the post, returns True if successfull,
    otherwise an error is raised"""
    try:
        place_holder = ("[#placeholder-awb]Comment is being processed... "
                        "It will be automatically replaced by new text"
                        "within a minute or will be deleted if that fails.")
        header = "#####&#009;\n\n######&#009;\n\n####&#009;\n"
        disclaimer = ("^Parent ^commenter ^can [^toggle ^NSFW]"
                      "(http://www.np.reddit.com/message/compose?"
                      "to=autowikibot&subject=AutoWikibot "
                      "NSFW toggle&message=%2Btoggle-nsfw+{id}) ^or[](#or) "
                      "[^delete](http://www.np.reddit.com/message/compose?"
                      "to=autowikibot&subject=AutoWikibot"
                      "Deletion&message=%2Bdelete+{id})^. ^Will ^also ^delete "
                      "^on ^comment ^score ^of ^-1 ^or ^less. ^| "
                      "[^(FAQs)](http://www.np.reddit.com/r/autowikibot"
                      "/wiki/index) ^| [^Mods]"
                      "(http://www.np.reddit.com/r/autowikibot/comments/"
                      "1x013o/for_moderators_switches_commands_and_css/) ^| "
                      "[^Magic ^Words](http://www.np.reddit.com/r/autowikibot/"
                      "comments/1ux484/ask_wikibot/)")
        comment = post.reply(place_holder)
        # Add the header + the actual message
        reply = header + reply
        # Add the disclaimer/information footer
        reply += disclaimer.format(id=comment.id)
        # Edit the placeholder post
        postsuccess = comment.edit(reply)
        if not postsuccess:
            raise ReplyException('reply unsuccessful')
        TOTAL_POSTED += 1
        SUBMISSION_COUNTER[str(post.submission.id)] += 1
        #util.success("[OK] #%s "%TOTAL_POSTED)
        return True
    except urllib2.HTTPError as e:
        #util.warn("REPLY FAILED: %s @ %s"%(e, post.subreddit))
        if e.code == 414:
            comment.delete()
        raise
#        elif e.code == 403:
#            load_changing_variables()
#            badsubs.append(str(post.subreddit))
#            editsummary = 'added '+ str(post.subreddit)
#            save_changing_variables(editsummary)
    except ReplyException as e:
        #util.warn("REPLY FAILED: %s @ %s"%(e, post.subreddit))
        #util.fail(e)
        comment.delete()
        raise

class ReplyException(Exception):
    """When a non-praw issue happens with the posting code, this error is
    raised instead so that the programmer knows it's not praw's fault"""
    pass

if __name__ == "__main__":
    import praw
    BOT = praw.Reddit("Testing /u/autowikibot")