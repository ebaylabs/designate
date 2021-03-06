# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Graham Hayes <graham.hayes@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from designate.objects import base


class ZoneTransferAccept(base.DictObjectMixin, base.PersistentObjectMixin,
                         base.DesignateObject):
    FIELDS = {
        'zone_transfer_request_id': {},
        'tenant_id': {},
        'status': {},
        'key': {},
        'domain_id': {},
    }


class ZoneTransferAcceptList(base.ListObjectMixin, base.DesignateObject):
    LIST_ITEM_TYPE = ZoneTransferAccept
