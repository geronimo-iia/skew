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
"""Account module."""
from skew.config import get_accounts

from .component import LOG, ARNComponent

__all__ = ["Account"]


class Account(ARNComponent):
    """Account definition."""

    def __init__(self, pattern, arn):
        super(Account, self).__init__(pattern, arn)
        self._accounts = get_accounts()

    def choices(self, context=None):
        return list(self._accounts.keys())

    def enumerate(self, context, **kwargs):
        LOG.debug("Account.enumerate %s", context)
        for match in self.matches(context):
            context.append(match)
            for resource in self._arn.resource.enumerate(context, **kwargs):
                yield resource
            context.pop()
