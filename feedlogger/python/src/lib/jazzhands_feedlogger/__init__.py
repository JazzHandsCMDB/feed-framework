# Copyright 2017 Ryan D. Williams
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

"""Implements the JazzHands:Extension-FeedLogger client

Classes:
    FeedLogger - provides functionality for interacting with the FeedLogger database

Exceptions:
    FeedLoggerException - General module exceptions
"""


import os
import re
import sys
import socket
import getpass
import logging


from builtins import str as text


from jazzhands_appauthal.db import DatabaseConnection
from .db_functions import build_ins_query, add_nulls_to_vals


DEFAULT_APPAUTHAL_NAME = 'feedlogger'


LOG = logging.getLogger(__name__ + '.FeedLogger')


class FeedLogger(object):
    """Class to log feed events to the feedlogs DB

    Must be passed a configuration dictionary when initializing.

    Examples:
        conf = {
            'source_subsystem': 'JazzHands',
            'destination_subsystem': 'OpenLDAP',
            'allow_partial_updates': True
        }
        flgr = FeedLogger(conf)
        flgr.log_event('ExecutionStarted', 'info', 'HRIS feed started')
        flgr.commit()
    """


    SESSION_COLUMNS = [
        'source_subsystem', 'source_subsystem_instance', 'destination_subsystem',
        'destination_subsystem_instance', 'program_name', 'username', 'pid', 'host_name']
    EVENT_COLUMNS = ['session_id', 'event_type', 'event_priority', 'message']
    EVENT_ATTRIBUTE_COLUMNS = [
        'event_id', 'entity_name', 'entity_location', 'attribute_name',
        'key_type', 'attribute_value', 'attribute_new_value']


    def __init__(self, conf):
        """Requires a config dictionary

        Args:
            conf (dict): configuration dictionary

        Configuration:
            source_subsystem (str): the subsystem where the data is being synced from.
            destination_subsystem (str): the subsystem where the data is being synced to.
            source_subsystem_instance (str, optional): the specific instance of the subsystem being
                synced from. default None
            destination_subsystem (str, optional): the specific destination of the subsystem being
                synced to. default None
            appauthal_app_name (str, optional) - apauthal application name override.
                Default app_event_logger
            dry_run (bool, optional): setting dry run prevents any writes to the database.
                Default False
            allow_partial_updates (bool, optional): instructs the logger to log events immiedately.
                Turns on autocommit. Default False
            log_queries (bool, optional): logs queries to syslog. default False
            start_session: (bool, optional): tells the FeedLogger to start the session upon init.
                Default True
        """
        self._conf = conf
        try:
            self._src_subsys = conf['source_subsystem']
            self._dst_subsys = conf['destination_subsystem']
        except KeyError as exc:
            raise FeedLoggerException(
                'Configuration dictionary must include: {}'.format(exc))
        appauthal_app_name = conf.get('appauthal_app_name', DEFAULT_APPAUTHAL_NAME)
        LOG.debug('connecting to DB using AppAuthAL: %s', appauthal_app_name)
        self._dbh = DatabaseConnection(appauthal_app_name).connect()
        self._dry_run = bool(conf.get('dry_run', False))
        self._log_qry = bool(conf.get('log_queries', False))
        if self._dry_run:
            LOG.debug('set to dry_run mode, no changes will be commited to the DB')
        #turn on autocommit only if requested AND NOT dry_run flagged
        if conf.get('allow_partial_updates') and not self._dry_run:
            self._dbh.rollback()
            self._dbh.autocommit = True
            LOG.debug('set to allow partial updates. will commit all events immiedately')
        if self._conf.get('start_session', True):
            self._session_id = self.start_session()
        else:
            self._session_id = None

    def commit(self):
        """Commits all open statements to JazzHands"""
        #never commit when in dry run mode
        if not self._dry_run:
            self._dbh.commit()
            if not self._dbh.autocommit:
                LOG.debug('Commited current transaction to the DB')

    def rollback(self):
        """Rolls back current transaction"""
        if not self._dry_run:
            LOG.debug('Rolling back current transaction')
            return self._dbh.rollback()

    def _syslog_qry(self, qry):
        """sanatizes a formated query for printing in a log"""
        if self._log_qry:
            LOG.debug(u'Executing query: %s', re.sub(r'\s+', ' ', qry))

    def _check_session(self):
        if not self._session_id:
            raise FeedLoggerException(
                'No session_id found. You must run start_session() before other actions')

    def start_session(self):
        """Starts a new feed session and returns the session_id from the DB"""
        LOG.debug('starting a new session')
        qry = build_ins_query('session', self.SESSION_COLUMNS, ['session_id'])
        vals = {
            'source_subsystem': self._src_subsys,
            'source_subsystem_instance': self._conf.get('source_subsystem_instance'),
            'destination_subsystem': self._dst_subsys,
            'destination_subsystem_instance': self._conf.get('destination_subsystem_instance'),
            'program_name': os.path.basename(sys.argv[0]),
            'username': getpass.getuser(),
            'pid': os.getpid(),
            'host_name': socket.getfqdn()
        }
        dbc = self._dbh.cursor()
        dbc.execute(qry, vals)
        self._syslog_qry(dbc.query)
        session_id = dbc.fetchone()[0]
        LOG.debug('Feed session started. session_id: %s', session_id)
        dbc.close()
        self.commit()
        return session_id

    def end_session(self):
        """Ends the current session. Records the current timestamp in the session table"""
        self._check_session()
        qry = 'UPDATE session SET session_end = NOW() WHERE session_id = %s'
        dbc = self._dbh.cursor()
        dbc.execute(qry, (self._session_id,))
        self._syslog_qry(dbc.query)
        LOG.debug('Feed session ended. session_id: %s', self._session_id)
        self.commit()
        dbc.close()

    def log_event(self, event_type, event_priority, message, event_attrs=None):
        """Logs an event to the database.

        Args:
            event_type (str): must exist in db val_event_type
            event_priority (str): must exist in db val_event_priority. think sysloger levels.
            message (str): the actual message to log. make it meaningful
            event_attrs (list of dict, optional): sequence containing attribute describing
                dictionaries attribute dictionary can only contain these keys:
                    entity_name, entity_location, attribute_name, key_type
                    attribute_value, attribute_new_value
        """
        self._check_session()
        if not event_attrs:
            event_attrs = list()
        event_qry = build_ins_query('event', self.EVENT_COLUMNS, ['event_id'])
        event_vals = {
            'session_id': self._session_id,
            'event_type': event_type,
            'event_priority': event_priority,
            'message': message
        }
        attr_qry = build_ins_query('event_attribute', self.EVENT_ATTRIBUTE_COLUMNS)
        dbc = self._dbh.cursor()
        dbc.execute(event_qry, event_vals)
        self._syslog_qry(dbc.query)
        event_id = dbc.fetchone()[0]
        LOG.debug('Adding event to log. event_id: %s, message: %s', event_id, message)
        for attr in event_attrs:
            attr = add_nulls_to_vals(self.EVENT_ATTRIBUTE_COLUMNS, attr)
            #this is a bit of a hack to deal with python2/3 unicode sillyness
            log_msg = 'Adding attribute: {} current_value: {} new_value: {} event_id: {}'.format(
                attr['attribute_name'], attr.get('attribute_value'),
                attr.get('attribute_new_value'), event_id)
            try:
                log_msg = text(log_msg)
            except UnicodeDecodeError:
                log_msg = log_msg.decode('utf-8')
            LOG.debug(log_msg)
            attr.update({'event_id': event_id})
            dbc.execute(attr_qry, attr)
            self._syslog_qry(dbc.query)


class FeedLoggerException(Exception):
    """For all FeedLogger exceptions"""
    pass
