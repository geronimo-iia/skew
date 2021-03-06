# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
# Copyright (c) 2020 Jerome Guibert
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

import logging

import jmespath
from botocore.exceptions import ClientError

from skew.awsclient import get_awsclient
from skew.resources.json_dump import json_dump

LOG = logging.getLogger(__name__)

__all__ = ["Resource"]


class Resource(object):
    @classmethod
    def get_awsclient(cls, region_name, account_id, **kwargs):
        """Get aws client and merge parameters."""
        return get_awsclient(
            **{**kwargs, "service_name": cls.Meta.service, "region_name": region_name, "account_id": account_id}
        )

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):

        client = cls.get_awsclient(region_name=region, account_id=account, **kwargs)

        op_kwargs = {}

        do_client_side_filtering = False
        if resource_id and resource_id != "*":
            # If we are looking for a specific resource and the
            # API provides a way to filter on a specific resource
            # id then let's insert the right parameter to do the filtering.
            # If the API does not support that, we will have to filter
            # after we get all of the results.
            filter_name = cls.Meta.filter_name
            if filter_name:
                if cls.Meta.filter_type == "arn":
                    op_kwargs[filter_name] = [str(arn)]
                elif cls.Meta.filter_type == "list":
                    op_kwargs[filter_name] = [resource_id]
                else:
                    op_kwargs[filter_name] = resource_id
            else:
                do_client_side_filtering = True

        enum_op, path, extra_args = cls.Meta.enum_spec
        if extra_args:
            op_kwargs.update(extra_args)
        LOG.debug("enum_spec=%s" % str(cls.Meta.enum_spec))

        try:
            data = client.call(enum_op, query=path, **op_kwargs)
            if data:
                if do_client_side_filtering:
                    data = filter(lambda d: cls.filter(arn, resource_id, d), data)
                return map(lambda d: cls(client, d, arn.query), data)
        except ClientError as e:
            LOG.debug(e)
            # if the error is because the resource was not found, be quiet
            if "NotFound" not in e.response["Error"]["Code"]:
                raise
        return []

    class Meta(object):
        type = "resource"
        dimension = None
        tags_spec = None
        id = None
        date = None
        name = None

    def __init__(self, client, data, query=None):
        self._client = client
        self._data = data if data else {}
        self._id = self._data.get(self.Meta.id, "") if hasattr(self.Meta, "id") and isinstance(self._data, dict) else ""
        self._metrics = None
        self._name = None
        self._date = None
        self._arn = None
        self._tags = None
        self._cloudwatch = (
            self._client.create_client(service="cloudwatch")
            if hasattr(self.Meta, "dimension") and self.Meta.dimension
            else None
        )
        self._query = query
        self.filtered_data = self._query.search(self._data) if self._query else None

    def __repr__(self):
        return self.arn

    @property
    def arn(self):
        if not self._arn:
            self._arn = (
                f"arn:aws:{self._client.service_name}:{self._client.region_name}"
                f":{self._client.account_id}:{self.resourcetype}/{self.id}"
            )
        return self._arn

    @property
    def data(self):
        return self._data

    @property
    def resourcetype(self):
        return self.Meta.type

    @property
    def parent(self):
        pass

    @property
    def name(self):
        if not self._name:
            self._name = jmespath.search(self.Meta.name, self._data)
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        if not self._date:
            self._date = jmespath.search(self.Meta.date, self._data)
        return self._date

    @property
    def tags(self):
        return self._tags

    @property
    def metrics(self):
        return self._metrics if self._metrics else []

    @property
    def metric_names(self):
        return [m["MetricName"] for m in self.metrics]

    def find_metric(self, metric_name):
        for m in self.metrics:
            if m["MetricName"] == metric_name:
                return m
        return None

    def json_dump(self, normalize=True):
        return json_dump(self.data, normalize=normalize)
