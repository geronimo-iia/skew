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

from .component import ARNComponent, LOG

__all__ = ["Region"]


class Region(ARNComponent):
    _all_region_names = [
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "eu-west-1",
        "eu-west-2",
        "eu-west-3",
        "eu-central-1",
        "eu-north-1",
        "eu-south-1",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ap-northeast-2",
        "ap-south-1",
        "ap-east-1",
        "af-south-1",
        "ca-central-1",
        "sa-east-1",
        "me-south-1",
        "cn-north-1",
        "cn-northwest-1",
    ]

    _no_region_required = [""]

    _service_region_map = {
        "glacier": [
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-south-1",
            "ap-southeast-2",
            "ca-central-1",
            "eu-central-1",
            "eu-west-1",
            "eu-west-2",
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
        ],
        "cloudfront": _no_region_required,
        "iam": _no_region_required,
        "route53": _no_region_required,
        "cloudsearch": [
            "us-east-1",
            "us-west-2",
            "us-west-1",
            "eu-west-1",
            "eu-central-1",
            "sa-east-1",
            "ap-southeast-1",
            "ap-northeast-1",
            "ap-southeast-2",
        ],
        "opsworks": [
            "us-east-2",
            "us-west-1",
            "us-east-1",
            "us-west-2",
            "eu-central-1",
            "eu-west-1",
            "ap-southeast-1",
            "ap-northeast-1",
            "ap-southeast-2",
        ],
    }

    def choices(self, context=None):
        if context:
            service = context[2]
        else:
            service = self._arn.service
        return self._service_region_map.get(service, self._all_region_names)

    def enumerate(self, context, **kwargs):
        LOG.debug("Region.enumerate %s", context)
        for match in self.matches(context):
            context.append(match)
            for account in self._arn.account.enumerate(context, **kwargs):
                yield account
            context.pop()
