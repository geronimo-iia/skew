# Copyright (c) 2014 Scopely, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import os
import unittest

import mock

import skew.awsclient
import skew.resources
from skew.resources.definition import _RESOURCE_TYPES, find_resource_class
from skew.resources.resource import Resource


class FooResource(Resource):
    class Meta(object):
        service = 'ec2'
        type = 'foo'
        id = 'bar'


class TestResource(unittest.TestCase):
    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch('os.environ', self.environ)
        self.environ_patch.start()
        credential_path = os.path.join(os.path.dirname(__file__), 'cfg', 'aws_credentials')
        self.environ['AWS_CONFIG_FILE'] = credential_path
        config_path = os.path.join(os.path.dirname(__file__), 'cfg', 'skew.yml')
        self.environ['SKEW_CONFIG'] = config_path

    def tearDown(self):
        pass

    def test_resource(self):
        client = skew.awsclient.get_awsclient(service_name='ec2', region_name='us-east-1', account_id='123456789012')
        resource = FooResource(client, data={'bar': 'bar'})
        self.assertEqual(resource.id, 'bar')
        self.assertEqual(resource.__repr__(), 'arn:aws:ec2:us-east-1:123456789012:foo/bar')
        self.assertEqual(resource.metrics, [])
        self.assertEqual(resource.find_metric('foobar'), None)

    def test_all_providers(self):
        all_providers = skew.resources.all_providers()
        self.assertEqual(len(all_providers), 1)
        self.assertEqual(all_providers[0], 'aws')

    def test_all_services(self):
        all_providers = skew.resources.all_services('aws')
        self.assertEqual(len(all_providers), 35)

    def test_all_regions(self):
        all_regions = skew.arn.region.Region('arn:aws:*:*:*:*', None).__getattribute__('_all_region_names')
        self.assertEqual(len(all_regions), 22)

    def test_all_resource_class(self):
        for key in _RESOURCE_TYPES.keys():
            self.assertIsNotNone(find_resource_class(key))
