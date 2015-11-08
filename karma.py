from errbot import BotPlugin, botcmd, re_botcmd
from datetime import datetime
import re
import logging

log = logging.getLogger(name='errbot.plugins.Karma')


class Karma(BotPlugin):

    def update_karma(self, username, count=1):
        ''' Updates db with current count '''

        username = str(username)

        try:
            old_count = self.shelf.get(username).get('karma', 0)
            new_count = old_count + count
        except AttributeError:
            self.shelf[username] = {}
            new_count = count

        log.debug('new karma count is {}'.format(new_count))

        self.shelf[username] = {
            'time': datetime.now(),
            'karma': new_count,
        }
        self.shelf.sync()

    @re_botcmd(pattern=r'^[a-z0-9]+\+\+$', prefixed=False, flags=re.IGNORECASE)
    def give_karma(self, msg, match):
        ''' This gives karma '''
        if match:
            username = match.group(0).rstrip('++')
            self.update_karma(username)

            self.send(msg.frm,
                    'karma -- {}: {}'.format(username,self.shelf.get(username).get('karma')),
                      message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)

    @re_botcmd(pattern=r'^[a-z0-9]+--$', prefixed=False, flags=re.IGNORECASE)
    def remove_karma(self, msg, match):
        ''' This removes a karma '''
        self.send(msg.frm,
                  'Seriously...?',
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
        for user in self.shelf.keys():
            user_list.append("%s: %d" % (user, self.shelf.get(user).get('karma')))

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
