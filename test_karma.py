import karma
from errbot.backends.test import testbot, push_message, pop_message
from errbot import plugin_manager


class TestKarma(object):
    extra_plugin_dir = '.'

    def test_delete_karma_list_empty(self, testbot):
        push_message('!karma list')
        assert 'No users' in pop_message()

    def test_delete_karma_user_empty(self, testbot):
        push_message('!karma delete_entries sijis')
        assert 'User sijis has no entries' in pop_message()

    def test_give_karma(self, testbot):
        push_message('!sijis++')
        assert 'karma updated for sijis' in pop_message()

    def test_remove_karma(self, testbot):
        push_message('!sijis--')
        assert 'Seriously...?' in pop_message()

    def test_delete_karma_user(self, testbot):
        push_message('!sijis++')
        assert 'karma updated for sijis' in pop_message()
        push_message('!karma delete_entries sijis')
        assert 'Entries deleted for sijis user' in pop_message()

    def test_delete_karma_list(self, testbot):
        push_message('!sijis++')
        assert 'karma updated for sijis' in pop_message()
        push_message('!tom++')
        assert 'karma updated for tom' in pop_message()
        push_message('!karma list')
        assert 'sijis, tom' in pop_message()

    def test_karma_stats(self, testbot):
        push_message('!karma sijis')
        assert 'sijis has 1 kudo points' in pop_message()

    def test_karma_stats_empty(self, testbot):
        push_message('!karma sijis_empty')
        assert 'sijis_empty has 0 kudo points' in pop_message()

    def test_karma_blank_user(self, testbot):
        push_message('!karma')
        assert 'Username is required.' in pop_message()
