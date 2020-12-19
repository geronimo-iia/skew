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

from typing import List, Optional, Dict, Any
import os
import boto3
from functools import lru_cache
from botocore.config import Config

__all__ = [
    "get_default_region",
    "get_all_activated_regions",
    "get_caller_identity_account_id",
    "get_default_session",
    "get_session",
    "get_client",
]


@lru_cache(maxsize=10)
def get_default_region() -> str:
    """Get default AWS Region.

    Returns:
        (str): aws default region name
    """
    default_region = os.environ.get("DEFAULT_AWS_REGION", "us-east-1")
    if "gov-" in default_region:
        default_region = "us-gov-west-1"
    elif "cn-" in default_region:
        default_region = "cn-north-1"
    else:
        default_region = "us-east-1"
    return default_region


@lru_cache(maxsize=10)
def get_all_activated_regions() -> List[str]:
    """Return a list of enabled region of caller account.

    Returns:
        List(str): list of aws region
    """
    return list(
        map(
            lambda r: r["RegionName"],
            get_client(session=get_default_session(), service_name="ec2").describe_regions()["Regions"],
        )
    )


def get_session(
    region_name: Optional[str] = None,
    aws_creds: Optional[Dict[str, str]] = None,
    profile_name: Optional[str] = None,
    placebo: Optional[Any] = None,
    placebo_data_path: Optional[str] = None,
    placebo_mode: Optional[str] = "record",
) -> boto3.Session:
    """Return boto3 sesssion.

    Parameters:
        region_name (Optional[str]): optional region name
        aws_creds (Optional[Dict[str, str]]): optional dict of aws key, aws secret key
        profile_name (Optional[str]): optional profile name
        placebo (Optional[Any]): optional placebo object
        placebo_data_path (Optional[str]): optional placebo data path
        placebo_mode Optional[str]: optional placebo mode (default 'record')
    """

    params = {}

    if region_name:
        params["region_name"] = region_name

    if aws_creds:
        params = {**params, **aws_creds}
    elif profile_name:
        params["profile_name"] = profile_name

    session = boto3.Session(**params)

    # Placebo Condiguration
    if placebo and placebo_data_path:
        pill = placebo.attach(session, data_path=placebo_data_path)
        if placebo_mode == "record":
            pill.record()
        elif placebo_mode == "playback":
            pill.playback()

    return session


def get_default_session() -> boto3.Session:
    """Return boto3 sessions on default aws region."""
    return get_session(region_name=get_default_region())


def get_client(
    session: boto3.Session,
    service_name: str,
    region_name: Optional[str] = None,
    max_attempts: int = 20,
    config: Optional[Config] = None,
):
    """Return a configured boto3 client.

    By default, client is configured with an adaptive retries with 20 #attemps max.

    Parameters:
        session (boto3.Session): boto3 session
        service_name (str): service name
        region_name (Optional[str]): optional aws region name
        max_attempts (int): optional retry max attemps (default 20)
        config (Optional[Config]): optional boto3 Config instance
    """
    # see https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
    return session.client(
        service_name,
        region_name=region_name,
        config=config if config else Config(retries={"max_attempts": max_attempts, "mode": "adaptive"}),
    )


def get_caller_identity_account_id() -> str:
    """Returns aws identity of the caller."""
    return get_client(get_default_session(), service_name="sts").get_caller_identity()["Account"]
