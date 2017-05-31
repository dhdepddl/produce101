# adapted from firebase/EventSource-Examples/python/chat.py by Shariq Hashme

from sseclient import SSEClient
import requests
from firebase_token_generator import FirebaseTokenGenerator

from Queue import Queue
import json
import threading
import socket
import ast


def json_to_dict(response):
    return ast.literal_eval(json.dumps(response))


class ClosableSSEClient(SSEClient):

    def __init__(self, *args, **kwargs):
        self.should_connect = True
        super(ClosableSSEClient, self).__init__(*args, **kwargs)

    def _connect(self):
        if self.should_connect:
            super(ClosableSSEClient, self)._connect()
        else:
            raise StopIteration()

    def close(self):
        self.should_connect = False
        self.retry = 0
        try:
            self.resp.raw._fp.fp._sock.shutdown(socket.SHUT_RDWR)
            self.resp.raw._fp.fp._sock.close()
        except AttributeError:
            pass


class RemoteThread(threading.Thread):

    def __init__(self, parent, URL, function, params, headers):
        self.function = function
        self.URL = URL
        self.parent = parent
        self.params = params
        self.headers = headers
        super(RemoteThread, self).__init__()

    def run(self):
        try:
            self.sse = ClosableSSEClient(self.URL, self.params, self.headers)
            print self.sse
            for msg in self.sse:
                msg_test = json.loads(msg.data)
                if msg_test is None:    # keep-alives
                    continue
                msg_data = json_to_dict(msg.data)
                msg_event = msg.event
                # TODO: update parent cache here
                self.function((msg.event, msg_data))
        except socket.error:
            pass    # this can happen when we close the stream
        except KeyboardInterrupt:
            self.close()

    def close(self):
        if self.sse:
            self.sse.close()


class FirebaseUser(object):
    """
    Class that wraps the credentials of the authenticated user. Think of
    this as a container that holds authentication related data.
    """

    def __init__(self, email, firebase_auth_token, provider, id=None):
        self.email = email
        self.firebase_auth_token = firebase_auth_token
        self.provider = provider
        self.id = id


class FirebaseAuthentication(object):
    def __init__(self, secret, email, debug=False, admin=False, extra=None):
        self.authenticator = FirebaseTokenGenerator(secret, debug, admin)
        self.email = email
        self.provider = 'password'
        self.extra = (extra or {}).copy()
        self.extra.update({'debug': debug, 'admin': admin,
                           'email': self.email, 'provider': self.provider})

    def get_user(self):
        token = self.authenticator.create_token(self.extra)
        user_id = self.extra.get('id')
        return FirebaseUser(self.email, token, self.provider, user_id)


def firebaseURL(URL):
    if '.firebaseio.com' not in URL.lower():
        if '.json' == URL[-5:]:
            URL = URL[:-5]
        if '/' in URL:
            if '/' == URL[-1]:
                URL = URL[:-1]
            URL = 'https://' + \
                URL.split('/')[0] + '.firebaseio.com/' + URL.split('/', 1)[1] + '.json'
        else:
            URL = 'https://' + URL + '.firebaseio.com/.json'
        return URL

    if 'http://' in URL:
        URL = URL.replace('http://', 'https://')
    if 'https://' not in URL:
        URL = 'https://' + URL
    if '.json' not in URL.lower():
        if '/' != URL[-1]:
            URL = URL + '/.json'
        else:
            URL = URL + '.json'
    return URL


class EventListener:

    def __init__(self, URL, function, params=None, headers=None):
        self.cache = {}
        self.remote_thread = RemoteThread(self, firebaseURL(URL), function, params, headers)

    def start(self):
        self.remote_thread.start()

    def stop(self):
        self.remote_thread.close()
        self.remote_thread.join()

    def wait(self):
        self.remote_thread.join()


class FirebaseException(Exception):
    pass


class Firebase():
    def __init__(self, name, authentication=None):
        assert name.startswith('https://'), 'DSN must be a secure URL'
        self.name = name
        self.URL = firebaseURL(name)
        self.authentication = authentication

    def child(self, child):
        return Firebase(self.name + child + "/", self.authentication)

    def _authenticate(self, params, headers):
        if self.authentication:
            user = self.authentication.get_user()
            params.update({'auth': user.firebase_auth_token})
            headers.update(self.authentication.authenticator.HEADERS)

    def put(self, msg, params=None, headers=None):
        to_post = json.dumps(msg)
        params = params or {}
        headers = headers or {}
        self._authenticate(params, headers)
        response = requests.put(firebaseURL(self.URL), data=to_post, params=params, headers=headers)
        if response.status_code != 200:
            raise FirebaseException(response.text)

    def patch(self, msg, params=None, headers=None):
        to_post = json.dumps(msg)
        params = params or {}
        headers = headers or {}
        self._authenticate(params, headers)
        response = requests.patch(firebaseURL(self.URL), data=to_post, params=params, headers=headers)
        if response.status_code != 200:
            raise FirebaseException(response.text)

    def get(self, params=None, headers=None):
        params = params or {}
        headers = headers or {}
        self._authenticate(params, headers)
        response = requests.get(firebaseURL(self.URL), params=params, headers=headers)
        if response.status_code != 200:
            raise FirebaseException(response.text)
        return response._content

    def listener(self, callback=None, params=None, headers=None):

        def handle(response):
            print response

        params = params or {}
        headers = headers or {}
        self._authenticate(params, headers)
        return EventListener(self.name, callback or handle, params, headers)

    def __str__(self):
        return self.name

