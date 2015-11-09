from errbot import BotPlugin, botcmd, re_botcmd
from datetime import datetime, timedelta
import re
import logging

log = logging.getLogger(name='errbot.plugins.Karma')
min_timeout = 10

class Karma(BotPlugin):

    def update_karma(self, username, msg, count=1):
        ''' Updates db with current count '''

        if msg.type == 'chat':
            return("cheating")
            self.send(msg.frm,
                "No cheating!",
                message_type=msg.type,
                in_reply_to=msg,
                groupchat_nick_reply=True)

        username = str(username)
        calling_nick = str(msg.nick)
        history_key = "{}_karmatimer".format(calling_nick)
        if calling_nick == '':
            calling_nick = "blank_nick"
        target_reference = '{}_karma'.format(username)
        try:
            myshelf = self.shelf.get(history_key)
            last_karma_this_user_combo = myshelf.get(target_reference, datetime.now()-timedelta(1))
            timediff = int((datetime.now() - last_karma_this_user_combo).total_seconds())
            #import ipdb; ipdb.set_trace()
            if timediff < min_timeout:
                log.debug('{} tried to change karma for {} after only {} seconds'.format(calling_nick, username, timediff))
                self.send(msg.frm,
                    "You can't change karma for {} for another {} seconds".format(username,min_timeout-timediff),
                    message_type=msg.type,
                    in_reply_to=msg,
                    groupchat_nick_reply=True)
                return("tooquick")
            myshelf[target_reference] = datetime.now()
            self.shelf[history_key] = myshelf
        except AttributeError:
            self.shelf[history_key] = {target_reference: datetime.now()}

        try:
            old_count = self.shelf.get(username).get('karma', 0)
            new_count = old_count + count
        except AttributeError:
            self.shelf[username] = {}
            new_count = count

        log.debug('new karma count is {}'.format(new_count))
        #import ipdb; ipdb.set_trace()
        myshelf = self.shelf[username]
        myshelf['karma_time'] = datetime.now()
        myshelf['karma'] = new_count
        self.shelf[username] = myshelf

        self.shelf.sync()
        return("legit")

    @re_botcmd(pattern=r'^[a-z0-9@]+\+\+$', prefixed=False, flags=re.IGNORECASE)
    def give_karma(self, msg, match):
        ''' This gives karma '''
        if match:
            username = match.group(0).rstrip('++')
            status = self.update_karma(username, msg)
            if status == "cheating":
                return
            elif status == "tooquick":
                return
            else:
                reply_txt = "karma -- {}: {}".format(username,self.shelf.get(username).get('karma'))
                #import ipdb; ipdb.set_trace()
                self.send(msg.frm,
                    reply_txt,
                    message_type=msg.type,
                    in_reply_to=msg,
                    groupchat_nick_reply=True)

    @re_botcmd(pattern=r'^[a-z0-9\@]+--$', prefixed=False, flags=re.IGNORECASE)
    def remove_karma(self, msg, match):
        ''' This removes a karma '''
        if match:
            username = match.group(0).rstrip('--')
            status = self.update_karma(username,msg,count=-1)
            if status == 'cheating':
                return
            elif status == "tooquick":
                return
            else:
                reply_txt = "Ouch... {}, what did {} do to you?".format(msg.nick, username)
                self.send(msg.frm,
                        reply_txt,
                        message_type=msg.type,
                        in_reply_to=msg,
                        groupchat_nick_reply=True)

    @botcmd(admin_only=True)
    def karma_delete_entries(self, msg, args):
        ''' Deletes all entries for a user '''
        username = str(args)

        try:
            del self.shelf[username]
            text = 'Entries deleted for {} user'.format(username)
        except KeyError:
            text = 'User {} has no entries'.format(username)

        self.send(msg.frm,
                  text,
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

    @botcmd
    def karma_list(self, msg, args):
        ''' Returns a list of users that have a karma '''
        user_list = []
        #import ipdb; ipdb.set_trace()
        for user in self.shelf.keys():
            try:
                user_list.append("%s: %d" % (user, self.shelf.get(user).get('karma')))
            except TypeError:
                pass

        if user_list == []:
            response = 'No users'
        else:
            response = '\n'.join(user_list)

        self.send(msg.frm,
                  response,
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
    @botcmd
    def karma_debug(self, msg, args):
        ''' Returns a list of users that have a karma '''
        response = msg
        self.send(msg.frm,
                  response,
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

    @botcmd
    def karma(self, msg, args):
        ''' A way to see your karma stats
            Example:
                !karma <username>
        '''
        username = str(args)

        if username == '':
            self.send(msg.frm,
                      'Username is required.',
                      message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            return

        try:
            count = self.shelf.get(username).get('karma')
        except (TypeError, NameError, AttributeError):
            count = 0

        self.send(msg.frm,
                  '{} has {} karma points.'.format(username, count),
                  message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
