# Copyright 2010 United States Government as represented by the
#   Administrator of the National Aeronautics and Space Administration.
#   All Rights Reserved.
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

"""Session Handling for SQLAlchemy backend."""

from oslo.config import cfg
from oslo.db.sqlalchemy import session

from designate.openstack.common import log as logging


LOG = logging.getLogger(__name__)

CONF = cfg.CONF


_FACADES = {}


def _create_facade_lazily(name):
    if name not in _FACADES:
        _FACADES[name] = session.EngineFacade(
            cfg.CONF[name].connection,
            **dict(cfg.CONF[name].iteritems()))

    return _FACADES[name]


def get_engine(name):
    facade = _create_facade_lazily(name)
    return facade.get_engine()


def get_session(name, **kwargs):
    facade = _create_facade_lazily(name)
    return facade.get_session(**kwargs)
