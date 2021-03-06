# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Kiall Mac Innes <kiall@hp.com>
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
import copy
import threading

from oslo.config import cfg
from oslo.db import options
from oslo.utils import excutils
from sqlalchemy.sql import select

from designate.openstack.common import log as logging
from designate import exceptions
from designate.i18n import _LC
from designate.backend import base
from designate.backend.impl_powerdns import tables
from designate.sqlalchemy import session

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def _map_col(keys, col):
    return dict([(keys[i], col[i]) for i in range(len(keys))])


class PowerDNSBackend(base.PoolBackend):
    __plugin_name__ = 'powerdns'

    @classmethod
    def _get_common_cfg_opts(cls):
        opts = copy.deepcopy(options.database_opts)

        # Overide the default DB connection path in order to avoid name
        # conflicts between the Designate and PowerDNS databases.
        for opt in opts:
            if opt.name == 'connection':
                opt.default = 'sqlite:///$state_path/powerdns.sqlite'

        return opts

    def __init__(self, *args, **kwargs):
        super(PowerDNSBackend, self).__init__(*args, **kwargs)

        self.local_store = threading.local()

    @property
    def session(self):
        # NOTE: This uses a thread local store, allowing each greenthread to
        #       have it's own session stored correctly. Without this, each
        #       greenthread may end up using a single global session, which
        #       leads to bad things happening.
        global LOCAL_STORE

        if not hasattr(self.local_store, 'session'):
            self.local_store.session = session.get_session(self.name)

        return self.local_store.session

    def _create(self, table, values):
        query = table.insert()

        resultproxy = self.session.execute(query, values)

        # Refetch the row, for generated columns etc
        query = select([table])\
            .where(table.c.id == resultproxy.inserted_primary_key[0])
        resultproxy = self.session.execute(query)

        return _map_col(query.columns.keys(), resultproxy.fetchone())

    def _get(self, table, id_, exc_notfound, id_col=None):
        if id_col is None:
            id_col = table.c.id

        query = select([table])\
            .where(id_col == id_)

        resultproxy = self.session.execute(query)

        results = resultproxy.fetchall()

        if len(results) != 1:
            raise exc_notfound()

        # Map col keys to values in result
        return _map_col(query.columns.keys(), results[0])

    def _delete(self, table, id_, exc_notfound, id_col=None):
        if id_col is None:
            id_col = table.c.id

        query = table.delete()\
            .where(id_col == id_)

        resultproxy = self.session.execute(query)

        if resultproxy.rowcount != 1:
            raise exc_notfound()

    # Domain Methods
    def create_domain(self, context, domain):
        try:
            self.session.begin()

            domain_values = {
                'designate_id': domain['id'],
                'name': domain['name'].rstrip('.'),
                'master': ','.join(CONF['backend:powerdns'].masters),
                'type': 'SLAVE',
                'account': context.tenant
            }

            self._create(tables.domains, domain_values)
        except Exception:
            with excutils.save_and_reraise_exception():
                self.session.rollback()
        else:
            self.session.commit()

    def delete_domain(self, context, domain):
        try:
            self._get(tables.domains, domain['id'], exceptions.DomainNotFound,
                      id_col=tables.domains.c.designate_id)
        except exceptions.DomainNotFound:
            # If the Domain is already gone, that's ok. We're deleting it
            # anyway, so just log and continue.
            LOG.critical(_LC('Attempted to delete a domain which is '
                             'not present in the backend. ID: %s') %
                         domain['id'])
            return

        self._delete(tables.domains, domain['id'],
                     exceptions.DomainNotFound,
                     id_col=tables.domains.c.designate_id)
