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
"""Component module."""
import logging
import re

__all__ = ["ARNComponent", "LOG"]

LOG = logging.getLogger("skew.arn")


class ARNComponent(object):
    """Arn component base class."""

    def __init__(self, pattern, arn):
        self.pattern = pattern
        # arn is Arn parent instance
        self._arn = arn

    def __repr__(self):
        return self.pattern

    def choices(self, context=None):
        """Return all choices for the value of this component.

        This method is responsible for returning all of the possible
        choices for the value of this component.

        The ``context`` can be a list of values of the components
        that precede this component.  The value of one or more of
        those previous components could affect the possible
        choices for this component.

        If no ``context`` is provided this method should return
        all possible choices.
        """
        return []

    def _match(self, pattern, context=None):
        """Return a list which match choices against pattern.

        This method returns a (possibly empty) list of strings that
        match the regular expression ``pattern`` provided.  You can
        also provide a ``context`` as described above.

        This method calls ``choices`` to get a list of all possible
        choices and then filters the list by performing a regular
        expression search on each choice using the supplied ``pattern``.
        """
        matches = []
        regex = pattern
        if regex == "*":
            regex = ".*"
        elif regex:
            # avoid match of elb and elbv2
            regex += "$"
        regex = re.compile(regex)
        for choice in self.choices(context):
            if regex.search(choice):
                matches.append(choice)
        return matches

    def matches(self, context=None):
        """Return a list which match choices against ``pattern`` attribute.

        This is a convenience method to return all possible matches
        filtered by the current value of the ``pattern`` attribute.
        """
        return self._match(self.pattern, context)

    def complete(self, prefix="", context=None):
        """Return a list of choices for the specified context and prefix."""
        return [c for c in self.choices(context) if c.startswith(prefix)]
