import logging
import uuid

import requests
import json
import base64

logger = logging.getLogger(__name__)

class AkeneoClientException(Exception):
    pass

class AkeneoClient():
    """
        A client that makes Akeneo API access simple.

        An example:
        akeneo = AkeneoClient()
        akeneo.login('admin', 'admin', '1_4ouoorldlxus8o4g8ccg8os0kg0wcwgscwskcgswg48so00wk8',
                     '6d306yd2ln48wk00080c4wcogc4c0wsg04sc480wgwcook4s0c')
        akeneo.post('products', JSON_WITH_PRODUCT_DATA)
    """

    base_url = 'http://localhost:8080'

    def __init__(self):
        # for now I only tested with this docker image :: https://github.com/pardahlman/docker-akeneo
        self.authorization = None  # init without authorization

    def login(self, username, password, client_id, secret):
        # get a token
        url = self.base_url + '/api/oauth/v1/token'
        authorization = 'Basic %s' % base64.b64encode(client_id+':'+secret)
        headers = {'Content-Type': 'application/json',
                   'Authorization': authorization}
        data = '''{ "grant_type": "password", "username": "%s", "password": "%s"}''' % (username, password)
        response = requests.post(url, data=data, headers=headers)
        access_token = json.loads(response._content)['access_token']
        self.authorization = 'Bearer %s' % access_token
        print self.authorization

    def get(self, endpoint):
        if not self.authorization:
            raise AkeneoClientException("client is not authorized yet.")

        url = self.base_url + '/api/rest/v1' + endpoint
        headers = {'Content-Type': 'application/json', 'Authorization': self.authorization}
        response = requests.get(url, headers=headers)
        # if not ok or already exists
        if not response.status_code == 200:
            raise AkeneoClientException("Unexpected response code: {code}.".format(code=response.status_code))
        return response.json()

    def post(self, endpoint, data):
        if not self.authorization:
            raise AkeneoClientException("client is not authorized yet.")

        url = self.base_url + '/api/rest/v1' + endpoint
        headers = {'Content-Type': 'application/json', 'Authorization': self.authorization}
        response = requests.post(url, data=data, headers=headers)
        # if not ok or already exists
        if not response.status_code in [201, 422]:
            raise AkeneoClientException("Unexpected response code: {code}.".format(code=response.status_code))
        return response

# test
akeneo = AkeneoClient()
akeneo.login('admin', 'admin', '1_4ouoorldlxus8o4g8ccg8os0kg0wcwgscwskcgswg48so00wk8',
             '6d306yd2ln48wk00080c4wcogc4c0wsg04sc480wgwcook4s0c')

# You need an attribute name and description to try this one!
data = '''{
          "identifier": "%s",
          "enabled": true,
          "groups": [],
          "variant_group": null,
          "values": {
            "name": [
              {
                "data": "%s",
                "locale": null,
                "scope": null
              }],
            "description": [
              {
                "data": "%s",
                "locale": null,
                "scope": null
              }
            ]
          }
        }''' % (uuid.uuid4(), "Product name", "Product name")
print(akeneo.post('/products', data))
print(akeneo.get('/products'))

