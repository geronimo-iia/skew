# Copyright 2015 Mitch Garnaat
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
from typing import Optional, Dict, Any
import logging
import time

import datetime
import jmespath
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import botocore

from .utility import get_client, get_session

LOG = logging.getLogger("skew.awsclient")

__all__ = ["AWSClient"]


class AWSClient(object):
    """Manage AWS Client."""

    def __init__(
        self,
        service_name: str,
        account_id: str,
        region_name: Optional[str] = None,
        aws_creds: Optional[Dict[str, str]] = None,
        profile_name: Optional[str] = None,
        placebo: Optional[Any] = None,
        placebo_data_path: Optional[str] = None,
        placebo_mode: Optional[str] = "record",
        max_attempts: int = 20,
        config: Optional[Config] = None,
        max_attempts_on_client_error: int = 10,
    ):
        """Build a new instance of AWSClient.

        By default, client is configured with an adaptive retries with 20 #attemps max.

        Parameters:
            service_name (str): aws service name
            region_name (str): aws region name
            account_id (str): aws account identifier
            aws_creds: optional aws credentials
            placebo: optional placebo instance
            placebo_dir: optional placebo diectory
            placebo_mode: optional placebo mode (default "record")
            max_attempts (int): optional retry max attemps (default 20)
            config (Optional[Config]): optional boto3 Config instance (overide max_attempts parameter)
            max_attempts_on_client_error (int): optional limit of retry on client error (default 10)

        """
        self._service_name = service_name
        self._region_name = region_name
        self._account_id = account_id
        self._max_attempts_on_client_error = max_attempts_on_client_error

        # Build a clojure in order to recreate boto3 client if needed

        def _create_client(service: str = None):
            return get_client(
                session=get_session(
                    aws_creds=aws_creds,
                    profile_name=profile_name,
                    placebo=placebo,
                    placebo_data_path=placebo_data_path,
                    placebo_mode=placebo_mode,
                ),
                service_name=service if service else service_name,
                region_name=region_name,
                max_attempts=max_attempts,
                config=config,
            )

        # set client factory
        self.create_client = _create_client

        # Build boto3 client
        self._client = self.create_client()

    @property
    def service_name(self):
        return self._service_name

    @property
    def region_name(self):
        return self._region_name

    @property
    def account_id(self):
        return self._account_id

    def call(self, op_name, query=None, **kwargs):
        """
        Make a request to a method in this client.  The response data is
        returned from this call as native Python data structures.

        This method differs from just calling the client method directly
        in the following ways:

          * It automatically handles the pagination rather than
            relying on a separate pagination method call.
          * You can pass an optional jmespath query and this query
            will be applied to the data returned from the low-level
            call.  This allows you to tailor the returned data to be
            exactly what you want.

        :type op_name: str
        :param op_name: The name of the request you wish to make.

        :type query: str
        :param query: A jmespath query that will be applied to the
            data returned by the operation prior to returning
            it to the user.

        :type kwargs: keyword arguments
        :param kwargs: Additional keyword arguments you want to pass
            to the method when making the request.
        """
        LOG.debug(kwargs)

        data = {}
        if self._client.can_paginate(op_name):
            paginator = self._client.get_paginator(op_name)
            results = paginator.paginate(**kwargs)
            data = results.build_full_result()
        else:
            operator = getattr(self._client, op_name)
            done = False
            retry = self._max_attempts_on_client_error
            while not done:
                try:
                    data = operator(**kwargs)
                    done = True
                except ClientError as e:
                    LOG.debug(e, kwargs)
                    if "Throttling" in str(e):
                        time.sleep(1)
                    elif "AccessDenied" in str(e):
                        done = True
                    elif "UnrecognizedClientException" in str(e):
                        LOG.error(e)
                        self._client = self.create_client()
                    elif "NoSuchTagSet" in str(e):
                        done = True
                    else:
                        # Avoid infinite loop
                        done = True
                    # avoid infinte loop
                    if not done:
                        retry -= 1
                        if retry < 0:
                            raise e

                except Exception:
                    done = True
        if query:
            return jmespath.compile(query).search(data)
        return data
