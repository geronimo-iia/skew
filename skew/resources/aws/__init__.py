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
"""aws module."""
import datetime
import logging
from collections import namedtuple

import jmespath

from skew.resources.resource import Resource

LOG = logging.getLogger(__name__)

__all__ = ["ArnComponents", "MetricData", "AWSResource"]


class MetricData(object):
    """MetricData Definition.

    This is a simple object that allows us to compose both the returned
    data from a call to ``get_metrics_data`` as well as the period that
    was used when getting the data from CloudWatch.  Since the period
    may be calculated by ``get_metrics_data`` rather than passed explicitly
    the user would otherwise not how what the period value was.

    """

    def __init__(self, data, period):
        self.data = data
        self.period = period


class AWSResource(Resource):
    """Base class for all AWS resource definition.

    Each Resource class defines a Config variable at the class level.  This
    is a dictionary that gives the specifics about which service the resource
    belongs to and how to enumerate the resource.

    Each entry in the dictionary we define:

    * service - The AWS service in which this resource is defined.
    * enum_spec - The enumeration configuration.  This is a tuple consisting
      of the name of the operation to call to enumerate the resources,
      a jmespath query that will be run against the result of the operation
      to retrieve the list of resources, and a dictionary containing any
      extra arguments you want to pass in the enumeration call.  This
      can be None if no additional arguments are required.
    * tags_spec - Some AWS resources return the tags for the resource in
      the enumeration operation (e.g. DescribeInstances) while others
      require a second operation to retrieve the tags.  If a second
      operation is required the ``tags_spec`` describes how to make the
      call.  It is a tuple consisting of:
      * operation name
      * jmespath query to find the tags in the response
      * the name of the parameter to send to identify the specific resource
        (this is not always the same as filter_name, e.g. RDS)
      * the value of the parameter to send to identify the specific resource
        (this is not always the same as the id, e.g. RDS)
      * [OPTIONAL] the fifth parameter is a dict containing the constants
        needed to the call of the operation, in addition to the parameter
        used to identify the specific resource (e.g. needed for Route53).
        Those constants are expressed in a dict of key, value pairs.
    * detail_spec - Some services provide only summary information in the
      list or describe method and require you to make another request to get
      the detailed info for a specific resource.  If that is the case, this
      would contain a tuple consisting of the operation to call for the
      details, the parameter name to pass in to identify the desired
      resource and the jmespath filter to apply to the results to get
      the details.
    * id - The name of the field within the resource data that uniquely
      identifies the resource.
    * dimension - The CloudWatch dimension for this resource.  A value
      of None indicates that this resource is not monitored by CloudWatch.
    * filter_name - By default, the enumerator returns all resources of a
      given type.  But you can also tell it to filter the results by
      passing in a list of id's.  This parameter tells it the name of the
      parameter to use to specify this list of id's.

    """

    class Meta(object):
        type = "awsresource"

    @classmethod
    def filter(cls, arn, resource_id, data):
        """Abstract filter operation.

        If the API does not support filtering, the resource
        return True if the returned data matches the
        resource ID we are looking for.
        """
        LOG.warning("filter classmethod must be implemented for %s", cls)
        pass

    def __init__(self, client, data, query=None):
        super(AWSResource, self).__init__(client=client, data=data, query=query)
        self._extra_attribute_loaded = False

    def __repr__(self):
        return self.arn

    @property
    def data(self):
        """Return data and load extra attributes if needed."""
        if not self._extra_attribute_loaded:
            if hasattr(self, "_load_extra_attribute"):
                self._load_extra_attribute()
            self._extra_attribute_loaded = True
        return super(AWSResource, self).data

    @property
    def metrics(self):
        """Return metrics."""
        if self._metrics is None:
            if self._cloudwatch:
                data = self._cloudwatch.call(
                    "list_metrics",
                    Dimensions=[{"Name": self.Meta.dimension, "Value": self._id}],
                )
                self._metrics = jmespath.search("Metrics", data)
            else:
                self._metrics = []
        return self._metrics

    @property
    def tags(self):
        """Return tags.

        Load and Convert the ugly Tags JSON into a real dictionary and
        memorize the result.
        """
        if self._tags is None:
            LOG.debug("need to build tags")
            self._tags = {}

            if hasattr(self.Meta, "tags_spec") and (self.Meta.tags_spec is not None):
                LOG.debug("have a tags_spec")
                method, path, param_name, param_value = self.Meta.tags_spec[:4]
                kwargs = {}
                filter_type = getattr(self.Meta, "filter_type", None)
                if filter_type == "arn":
                    kwargs = {param_name: [getattr(self, param_value)]}
                elif filter_type == "list":
                    kwargs = {param_name: [getattr(self, param_value)]}
                else:
                    kwargs = {param_name: getattr(self, param_value)}
                if len(self.Meta.tags_spec) > 4:
                    kwargs.update(self.Meta.tags_spec[4])
                LOG.debug("fetching tags")
                self._data["Tags"] = self._client.call(method, query=path, **kwargs)
                LOG.debug(self._data["Tags"])

            if "Tags" in self._data:
                self._tags = self._normalize_tags(self._data["Tags"])

        return self._tags

    def find_metric(self, metric_name):
        """Return specified metric if exists."""
        for m in self.metrics:
            if m["MetricName"] == metric_name:
                return m
        return None

    def _total_seconds(self, delta):
        # python2.6 does not have timedelta.total_seconds() so we have
        # to calculate this ourselves.  This is straight from the
        # datetime docs.
        return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

    def get_metric_data(
        self,
        metric_name=None,
        metric=None,
        days=None,
        hours=1,
        minutes=None,
        statistics=None,
        period=None,
    ):
        """Get metric data for this resource.

        You can specify the time frame for the data as either the number
        of days or number of hours.
        The maximum window is 14 days.  Based on the time frame
        this method will calculate the correct ``period`` to return
        the maximum number of data points up to the CloudWatch max
        of 1440.

        :type metric_name: str
        :param metric_name: The name of the metric this data will
            pertain to.

        :type days: int
        :param days: The number of days worth of data to return.
            You can specify either ``days`` or ``hours``.  The default
            is one hour.  The maximum value is 14 days.

        :type hours: int
        :param hours: The number of hours worth of data to return.
            You can specify either ``days`` or ``hours``.  The default
            is one hour.  The maximum value is 14 days.

        :type statistics: list of str
        :param statistics: The metric statistics to return.  The default
            value is **Average**.  Possible values are:

            * Average
            * Sum
            * SampleCount
            * Maximum
            * Minimum

        :returns: A ``MetricData`` object that contains both the CloudWatch
            data as well as the ``period`` used since this value may have
            been calculated by skew.
        """
        if not statistics:
            statistics = ["Average"]
        if days:
            delta = datetime.timedelta(days=days)
        elif hours:
            delta = datetime.timedelta(hours=hours)
        else:
            delta = datetime.timedelta(minutes=minutes)
        if not period:
            period = max(60, self._total_seconds(delta) // 1440)
        if not metric:
            metric = self.find_metric(metric_name)
        if metric and self._cloudwatch:
            end = datetime.datetime.utcnow()
            start = end - delta
            data = self._cloudwatch.call(
                "get_metric_statistics",
                Dimensions=metric["Dimensions"],
                Namespace=metric["Namespace"],
                MetricName=metric["MetricName"],
                StartTime=start.isoformat(),
                EndTime=end.isoformat(),
                Statistics=statistics,
                Period=period,
            )
            return MetricData(jmespath.search("Datapoints", data), period)
        else:
            raise ValueError("Metric (%s) not available" % metric_name)

    def _normalize_tags(self, tags):
        """Convert the ugly Tags JSON into a real dictionary."""
        result = {}
        if isinstance(tags, list):
            for kvpair in tags:
                # Compatibility fix for ECS, that use lowercase 'key' and 'value' as dict keys
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.list_tags_for_resource
                tags_key = kvpair.get("Key", kvpair.get("key"))
                tags_value = kvpair.get("Value", kvpair.get("value"))
                if tags_key in tags:
                    if not isinstance(tags[tags_key], list):
                        result[tags_key] = [tags[tags_key]]
                    result[tags_key].append(tags_value)
                else:
                    result[tags_key] = tags_value
        elif isinstance(tags, dict):
            result = tags
        return result

    def _feed_from_spec(self, attr_spec):
        """Utilty to call boto3 on demand.

        Remove ResponseMetadata if needed.
        """
        method, path, param_name, param_value = attr_spec[:4]
        kwargs = {param_name: getattr(self, param_value)}
        if path:
            kwargs["query"] = path
        data = self._client.call(method, **kwargs)
        if "ResponseMetadata" in data:
            del data["ResponseMetadata"]
        return data


ArnComponents = namedtuple("ArnComponents", ["scheme", "provider", "service", "region", "account", "resource"])
