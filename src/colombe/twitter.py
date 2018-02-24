from django.conf import settings

from django_redis import get_redis_connection

from twitter import Api
from twitter.error import TwitterError

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

con = get_redis_connection("default")


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

        self.key_id = ":1:twitter:user:id:{}"
        self.key_name = ":1:twitter:user:name:{}"

    def create_block(self, user_id):
        self.api.CreateBlock(user_id)

    def destroy_block(self, user_id):
        self.api.DestroyBlock(user_id)

    def lookup_users_from_id(self, ids):
        results = []
        missing_ids = []

        pipe = con.pipeline()

        print('Retrieving from cache....')
        for user_id in ids:
            pipe.get(self.key_id.format(user_id))

        users_found = pipe.execute()

        if None in users_found:
            print('Missing users...')
            for index, user_found in enumerate(users_found):
                if user_found is None:
                    missing_ids.append(ids[index])
                else:
                    results.append(user_found.decode('utf-8'))
        else:
            print('All users found!')
            print(users_found)
            return [u.decode('utf-8') for u in users_found]

        print('Retrieving from twitter api...')
        try:
            users = self.api.UsersLookup(user_id=missing_ids, include_entities=False)
            pipe = con.pipeline()
            for user in users:
                print(user.screen_name, user.id)
                pipe.set(self.key_id.format(user.id), user.screen_name, 60 * 60)
                pipe.set(self.key_name.format(user.screen_name), user.id, 60 * 60)
                results.append(user.screen_name)
        except TwitterError:
            return results

        pipe.execute()

        print('Cache refreshed...')

        return results

    def lookup_users_from_screen_name(self, screen_names):
        results = []
        missing_names = []

        pipe = con.pipeline()

        print('Retrieving {} from cache....'.format(len(screen_names)))
        for name in screen_names:
            pipe.get(self.key_name.format(name))

        users_found = pipe.execute()
        print('USERS_FOUND', users_found)

        if None in users_found:
            print('Missing users...')
            for index, user_found in enumerate(users_found):
                if user_found is None:
                    missing_names.append(screen_names[index])
                else:
                    results.append(int(user_found))
        else:
            print('All {} users found!'.format(len(screen_names)))
            return [int(i) for i in users_found]

        print('Retrieving from twitter api...')
        try:
            users = self.api.UsersLookup(screen_name=missing_names, include_entities=False)
            pipe = con.pipeline()
            for user in users:
                print(user.screen_name, user.id)
                pipe.set(self.key_id.format(user.id), user.screen_name, 60 * 60)
                pipe.set(self.key_name.format(user.screen_name), user.id, 60 * 60)
                results.append(user.id)
        except TwitterError:
            return results

        pipe.execute()

        print('Cache refreshed...')

        return results
