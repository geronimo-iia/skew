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
"""Boto3 utility."""
from .client import AWSClient
from .utility import (
    get_default_region,
    get_default_region,
    get_all_activated_regions,
    get_caller_identity_account_id,
    get_default_session,
    get_session,
    get_client,
)


__all__ = [
    "AWSClient",
    "get_default_region",
    "get_all_activated_regions",
    "get_caller_identity_account_id",
    "get_default_session",
    "get_session",
    "get_client",
]
