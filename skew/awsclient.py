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
"""aws client module."""
from typing import Any, Dict, Optional

from botocore.config import Config

from skew.boto import AWSClient
from skew.config import get_credentials, get_profile

__all__ = ["get_awsclient"]


def get_awsclient(
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
    **kwargs,  # ignore extra arguments
):
    """Return a configured aws client."""
    # credential management
    if profile_name is None:
        aws_creds = get_credentials(account_id=account_id)
        if aws_creds is None:
            profile_name = get_profile(account_id=account_id)

    return AWSClient(
        service_name=service_name,
        account_id=account_id,
        region_name=None if region_name == "" else region_name,
        aws_creds=aws_creds,
        profile_name=profile_name,
        placebo=placebo,
        placebo_data_path=placebo_data_path,
        placebo_mode=placebo_mode,
        max_attempts=max_attempts,
        config=config,
        max_attempts_on_client_error=max_attempts_on_client_error,
    )
