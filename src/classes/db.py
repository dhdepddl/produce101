from firebase import FirebaseAuthentication, FirebaseApplication
from User import User
import firebase_client


class Firebase:
    def __init__(self):
        auth = FirebaseAuthentication('kUFM5wAt2CkXtfKrglMjLPgNsuWsO33j1uKHMRyn', 'dhdepddl@gmail.com', True, True)
        self.db = firebase_client.Firebase('https://pickme-f283e.firebaseio.com/', auth)

    def get_initial_users(self, user_list):
        users = list(self.db.child('/user-profiles/data').get())
        for user in users:
            user_list.append(User(user))

    def get_initial_posts(self):
        posts = self.db.child('cards/data').get()
        return posts
