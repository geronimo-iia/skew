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
"""Arn module."""
import logging
from typing import Optional

import jmespath
from six.moves import zip_longest

from .account import Account
from .provider import Provider
from .region import Region
from .resource import Resource
from .scheme import Scheme
from .service import Service

__all__ = ["ARN"]


class ARN(object):
    """ARN definition."""

    ComponentClasses = [Scheme, Provider, Service, Region, Account, Resource]

    def __init__(self, arn_string="arn:aws:*:*:*:*", **kwargs):
        self.query: Optional[str] = None
        (
            self._scheme,
            self._provider,
            self._service,
            self._region,
            self._account,
            self._resource,
        ) = self._build_components_from_string(arn_string)
        self.kwargs = kwargs

    def __repr__(self):
        return ":".join(
            [
                str(c)
                for c in [
                    self._scheme,
                    self._provider,
                    self._service,
                    self._region,
                    self._account,
                    self._resource,
                ]
            ]
        )

    def debug(self):
        """Set debug mode on."""
        self.set_logger("skew", logging.DEBUG)

    def set_logger(self, logger_name, level=logging.DEBUG):
        """Initialize a logger.

        Convenience function to quickly configure full debug output
        to go to the console.
        """
        log = logging.getLogger(logger_name)
        log.setLevel(level)

        ch = logging.StreamHandler(None)
        ch.setLevel(level)

        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        log.addHandler(ch)

    def _build_components_from_string(self, arn_string):
        if "|" in arn_string:
            arn_string, query = arn_string.split("|")
            self.query = jmespath.compile(query)
        pairs = zip_longest(self.ComponentClasses, arn_string.split(":", 5), fillvalue="*")
        return [c(n, self) for c, n in pairs]

    @property
    def scheme(self) -> Scheme:
        """Return sheme components."""
        return self._scheme

    @property
    def provider(self) -> Provider:
        """Return provider components."""
        return self._provider

    @property
    def service(self) -> Service:
        """Return service components."""
        return self._service

    @property
    def region(self) -> Region:
        """Return region components."""
        return self._region

    @property
    def account(self) -> Account:
        """Return account components."""
        return self._account

    @property
    def resource(self) -> Resource:
        """Return resource components."""
        return self._resource

    def __iter__(self):
        context = []
        for scheme in self.scheme.enumerate(context, **self.kwargs):
            yield scheme
