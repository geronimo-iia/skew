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
"""Json utilities."""
import datetime
import json
import re
from typing import Dict

__all__ = ["json_dump", "custom_json_encoder", "camel_to_snake"]


def custom_json_encoder(x):
    """JSON encoder that formats datetimes as ISO8601 format."""
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, bytes):
        return x.decode()
    raise TypeError("Unknown type")


def json_dump(data, normalize=True):
    """Dump a dictionnary as json."""
    return json.dumps(
        obj=_normalize(data) if normalize else data,
        indent=4,
        sort_keys=True,
        default=custom_json_encoder,
    )


# _camel_to_snake optimisation pattern
_pattern_1 = re.compile("(.)([A-Z][a-z]+)")
_pattern_2 = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake(name: str) -> str:
    """Convert camel case string to snake case."""
    name = _pattern_1.sub(r"\1_\2", name)
    return _pattern_2.sub(r"\1_\2", name).lower()


def _normalize(data: Dict) -> Dict:
    """Normalize dictionary keys."""
    new_data = dict(map(lambda item: (camel_to_snake(item[0]), item[1]), data.items()))
    for key, value in new_data.items():
        if isinstance(value, dict):
            new_data[key] = _normalize(value)
        if isinstance(value, list):
            for i in range(len(value)):
                if isinstance(value[i], dict):
                    value[i] = _normalize(value[i])

    return new_data
