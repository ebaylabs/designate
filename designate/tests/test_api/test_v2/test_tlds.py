# Copyright (c) 2014 Rackspace Hosting
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from designate.tests.test_api.test_v2 import ApiV2TestCase


class ApiV2ZTldsTest(ApiV2TestCase):
    def setUp(self):
        super(ApiV2ZTldsTest, self).setUp()

    def test_create_tld(self):
        self.policy({'create_tld': '@'})
        fixture = self.get_tld_fixture(0)
        response = self.client.post_json('/tlds/', {'tld': fixture})

        # Check the headers are what we expect
        self.assertEqual(201, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Check the body structure is what we expect
        self.assertIn('tld', response.json)
        self.assertIn('links', response.json['tld'])
        self.assertIn('self', response.json['tld']['links'])

        # Check the values returned are what we expect
        self.assertIn('id', response.json['tld'])
        self.assertIn('created_at', response.json['tld'])
        self.assertIsNone(response.json['tld']['updated_at'])
        self.assertEqual(fixture['name'], response.json['tld']['name'])

    def test_create_tld_validation(self):
        self.policy({'create_tld': '@'})
        invalid_fixture = self.get_tld_fixture(-1)

        # Ensure it fails with a 400
        response = self.client.post_json('/tlds/', {'tld': invalid_fixture},
                                         status=400)
        self.assertEqual(400, response.status_int)

    def test_get_tlds(self):
        self.policy({'find_tlds': '@'})
        response = self.client.get('/tlds/')

        # Check the headers are what we expect
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Check the body structure is what we expect
        self.assertIn('tlds', response.json)
        self.assertIn('links', response.json)
        self.assertIn('self', response.json['links'])

        # We should start with 0 tlds
        self.assertEqual(0, len(response.json['tlds']))

        # Test with 1 tld
        self.create_tld(fixture=0)

        response = self.client.get('/tlds/')

        self.assertIn('tlds', response.json)
        self.assertEqual(1, len(response.json['tlds']))

        # test with 2 tlds
        self.create_tld(fixture=1)

        response = self.client.get('/tlds/')

        self.assertIn('tlds', response.json)
        self.assertEqual(2, len(response.json['tlds']))

    def test_get_tld(self):
        tld = self.create_tld(fixture=0)
        self.policy({'get_tld': '@'})

        response = self.client.get('/tlds/%s' % tld['id'],
                                   headers=[('Accept', 'application/json')])

        # Check the headers are what we expect
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Check the body structure is what we expect
        self.assertIn('tld', response.json)
        self.assertIn('links', response.json['tld'])
        self.assertIn('self', response.json['tld']['links'])

        # Check the values returned are what we expect
        self.assertIn('id', response.json['tld'])
        self.assertIn('created_at', response.json['tld'])
        self.assertIsNone(response.json['tld']['updated_at'])
        self.assertEqual(self.get_tld_fixture(0)['name'],
                         response.json['tld']['name'])

    def test_delete_tld(self):
        tld = self.create_tld(fixture=0)
        self.policy({'delete_tld': '@'})

        self.client.delete('/tlds/%s' % tld['id'], status=204)

    def test_update_tld(self):
        tld = self.create_tld(fixture=0)
        self.policy({'update_tld': '@'})

        # Prepare an update body
        body = {'tld': {'description': 'prefix-%s' % tld['description']}}

        response = self.client.patch_json('/tlds/%s' % tld['id'], body,
                                          status=200)

        # Check the headers are what we expect
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Check the body structure is what we expect
        self.assertIn('tld', response.json)
        self.assertIn('links', response.json['tld'])
        self.assertIn('self', response.json['tld']['links'])

        # Check the values returned are what we expect
        self.assertIn('id', response.json['tld'])
        self.assertIsNotNone(response.json['tld']['updated_at'])
        self.assertEqual('prefix-%s' % tld['description'],
                         response.json['tld']['description'])
