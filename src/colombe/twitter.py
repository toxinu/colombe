from django.conf import settings
from django.core.cache import cache

from twitter import Api
from twitter.error import TwitterError

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'


class Twitter:
    def __init__(self, access_token_key, access_token_secret):
        self.consumer_key = settings.TWITTER_CONSUMER_KEY
        self.consumer_secret = settings.TWITTER_CONSUMER_SECRET
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret

        self.api = Api(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            access_token_key=self.access_token_key,
            access_token_secret=self.access_token_secret)

    def create_block(self, user_id):
        self.api.CreateBlock(user_id)

    def destroy_block(self, user_id):
        self.api.DestroyBlock(user_id)

    def lookup_users_from_id(self, ids):
        results = []

        for user in self.api.UsersLookup(user_id=ids, include_entities=False):
            if user:
                cache.set("twitter:user:id:{}".format(user.id), user.screen_name, timeout=60 * 60)
                cache.set("twitter:user.name:{}".format(user.screen_name), user.id, timeout=60 * 60)

                results.append(user.screen_name)
            else:
                cache.set("twitter:user:id:{}".format(user.id), None, timeout=60 * 60 * 2)

        return results

    def lookup_users_from_screen_name(self, screen_names):
        results = []

        for user in self.api.UsersLookup(screen_name=screen_names, include_entities=False):
            if user:
                cache.set("twitter:user:id:{}".format(user.id), user.screen_name, timeout=60 * 60)
                cache.set("twitter:user.name:{}".format(user.screen_name), user.id, timeout=60 * 60)

                results.append(str(user.id))
            else:
                cache.set("twitter:user:name:{}".format(user.screen_name), None, timeout=60 * 60 * 2)

        return results

    def get_user_id_from_screen_name(self, screen_name):
        key_id = "twitter:user:id:{}"
        key_name = "twitter:user:name:{}".format(screen_name)

        result = cache.get(key_name)

        if result is None:
            try:
                user = self.api.GetUser(screen_name=screen_name)
                result = user.id
                cache.set(key_id.format(result), screen_name, timeout=60 * 60 * 1)
            except TwitterError:
                result = ''

            cache.set(key_name, result, timeout=60 * 60 * 1)

        if result == '':
            result = None

        return result

    def get_user_screen_name_from_id(self, user_id):
        key_id = "twitter:user:id:{}".format(user_id)
        key_name = "twitter:user:name:{}"

        result = cache.get(key_id)

        if result is None:
            try:
                user = self.api.GetUser(user_id=user_id)
                result = user.screen_name
                cache.set(key_name.format(result), user_id, timeout=60 * 60 * 1)
            except TwitterError:
                result = ''

            cache.set(key_id, result, timeout=60 * 60 * 1)

        if result == '':
            return None

        return result
