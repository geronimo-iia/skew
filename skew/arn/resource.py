# Copyright 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
# Copyright (c) 2020 Jerome Guibert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Resource module."""
from skew.resources import all_types, find_resource_class

from .component import LOG, ARNComponent

__all__ = ["Resource"]


class Resource(ARNComponent):
    """Resource definition."""

    def _split_resource(self, resource):
        LOG.debug("split_resource: %s", resource)
        if "/" in resource:
            resource_type, resource_id = resource.split("/", 1)
        elif ":" in resource:
            resource_type, resource_id = resource.split(":", 1)
        else:
            # TODO: Some services use ARN's that include only a resource
            # identifier (i.e. no resource type).  SNS is one example but
            # there are others.  We need to refactor this code to allow
            # the splitting of the resource part of the ARN to be handled
            # by the individual resource classes rather than here.

            # Fix resource enumeration when no resource type is define
            resource_type = "*"  # one resource type in this case per service
            resource_id = resource
        return (resource_type, resource_id)

    def _match(self, pattern, context=None):
        resource_type, _ = self._split_resource(pattern)
        return super(Resource, self)._match(resource_type, context)

    def choices(self, context=None):
        if context:
            provider, service = context[1:3]
        else:
            service = self._arn.service.pattern
            provider = self._arn.provider.pattern

        all_resources = all_types(provider, service)
        return all_resources if all_resources else ["*"]

    def enumerate(self, context, **kwargs):
        LOG.debug("Resource.enumerate %s", context)
        _, provider, service_name, region, account = context
        resource_type, resource_id = self._split_resource(self.pattern)
        LOG.debug("resource_type=%s, resource_id=%s", resource_type, resource_id)

        for resource_type in self.matches(context):
            resource_path = ".".join([provider, service_name, resource_type])
            resource_cls = find_resource_class(resource_path)
            for resource in resource_cls.enumerate(
                arn=self._arn, region=region, account=account, resource_id=resource_id, **kwargs
            ):
                yield resource
