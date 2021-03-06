# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from designate.objects import base


class ValidationError(base.DesignateObject):
    FIELDS = {
        'relative_path': {},
        'absolute_path': {},
        'message': {},
        'validator': {},
        'validator_value': {},
    }

    @classmethod
    def from_js_error(cls, js_error):
        """Convert a JSON Schema ValidationError instance into a
        ValidationError instance.
        """

        e = cls()
        e.relative_path = ".".join([str(x) for x in js_error.relative_path])
        e.absolute_path = ".".join([str(x) for x in js_error.absolute_path])
        e.message = js_error.message
        e.validator = js_error.validator
        e.validator_value = js_error.validator_value

        return e


class ValidationErrorList(base.ListObjectMixin, base.DesignateObject):
    LIST_ITEM_TYPE = ValidationError
