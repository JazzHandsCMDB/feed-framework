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

"""Record syncing helpers

Classes to support syncing records between datasources.
"""

__author__ = 'Ryan D. Williams <rdw@drws-office.com>'

# Standard library imports
import json
import logging
import argparse

from builtins import str as text

# Local imports
from jh_recsynclib import PackageError


LOG = logging.getLogger(__name__)


class SyncOptions(object):
    """Class provides an extensible arguments parser with defaults required
    by all feeds."""

    def __init__(self, conf_file=None, *args, **kwargs):
        """Inits a SyncOptions argument parser

        During initialization can be given one additional argparse option to
        add to the parser.  If addtional options are required, they must be
        added after init via the add_option method.

        Args:
            *args: positional arguments for argparser.add_argument
            **kwargs: key word arguments for argparser.add_argument
        """
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-n', '--no', dest='dry_run', action='store_true',
            default=False, help='set this for dry-run')
        self.parser.add_argument(
            '-v', '--verbose', dest='verbose',
            action='store_true', default=False,
            help='run the script in verbose mode')
        self.parser.add_argument(
            '-d', '--debug', dest='debug', action='store_true',
            default=False, help='run the script in debug mode')
        self.parser.add_argument(
            '-m', '--max', dest='max_percent', default=None,
            help='max allowed percent change')
        self.parser.add_argument(
            '--force', dest='force', action='store_true', default=False,
            help='overrides percentage calculation, sets max num of changes')
        self.parser.add_argument(
            '--conf-file', dest='conf_file', default=conf_file,
            help='path to configuration json configuration file')
        self.parser.add_argument(
            '--logging-conf', dest='logging_conf',
            help='override default AN syslogger conf file.')
        if args:
            self.parser.add_argument(*args, **kwargs)

    def add_option(self, *args, **kwargs):
        "addes option parser. see argparse add_argument"
        self.parser.add_argument(*args, **kwargs)

    def parse_opts(self, *args, **kwargs):
        "Returns argparse namespace object"
        return self.parser.parse_args(*args, **kwargs)


class SafetyLimiter(object):
    """Class for controlling the safety limit foo

    Total number of records to compare changes against must be set before
    using this classes check_changes feature.  You must either set this
    when instantiating or before using by calling set_total_records

    Example:
        sl = SafetyLimiter(max_p=15, t_rec=150)
            (or sl = SafetyLimiter()
                sl.set_total_records(150))
        sl.add_changes()            #increments by 1
        sl.add_changes([1, 2, 3])   #increments by 3
        if sl.check_changes():
            db.commit()
        else:
            db.rollback()
            LOG.error(sl.err_str)
    """

    DEFAULT_MAX = 10
    DEFAULT_MIN = 10

    def __init__(self, max_p=None, t_rec=None, min_=None, force=False):
        """Inits the SafetyLimiter class.

        Args:
            max_p: optional. max percent used to calculate the max number of
                changes allowed as percentage of total records. pulls default
                from jh in property table _feed_max_percent
            t_rec: optional. total number of records, used in conjunction with
                max_percent
            min_: the minimum number of total records to care about.  if the
                number of changes is less than this, ignore % safety limits.
                pulls default from property table _feed_safety_min
            force: optional.  ignore all safety limits

        """
        self._force = force
        self._max_percent = self.DEFAULT_MAX if not max_p else max_p
        self._min = self.DEFAULT_MIN if not min_ else min_
        self.max_changes = 0
        if t_rec:
            self.set_total_records(t_rec)
        self.current_changes = 0

    def set_total_records(self, total_recs):
        """Sets the total record count. Used to calculate allowed
        changes.

        Args:
            total_recs: int. number of records in destination
        """
        self._total_recs = total_recs
        self._calculate_total_changes()
        if not self._force:
            LOG.info('Total changes set to: %s', self.max_changes)
        else:
            LOG.info('Total changes ingored. Force flag given')

    def add_changes(self, changes=1):
        "Takes an integer and adds it to the counter. defaults to 1"
        self.current_changes += changes
        LOG.debug(
            '%s changes out of %s', self.current_changes, self.max_changes)

    def check_changes(self):
        "Checks if the changes are within the number allowed"
        if not self._total_recs:
            raise _SafetyLimiterException(
                'Total number of records has not been set.')
        return bool(
            self._force or self.current_changes <= self._min
            or self.current_changes <= self.max_changes)

    def get_error_str(self):
        "Returns a message explaining the fail"
        return (
            'Attempting too many changes. Allowed: {} Changes'
            ' attempted: {}'.format(self.max_changes, self.current_changes))

    def _calculate_total_changes(self):
        "Calculates and stores num of permited changes from total and percent"
        self.max_changes = int(self._total_recs * float(self._max_percent)/100)


class _SafetyLimiterException(Exception):
    pass


class SyncBase(object):                     # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Base for any JH sync classes.

    Must be subclassed and each subclass must implement the functions that
    are not yet coded.

    Configuration Dictionary Options:
        {
            'record_sync_logger_conf': dict - required (unless overriden when instantiating
                the class using the record_sync_logger_key param)
                Event logger configuration dict
            'sync_type': str - ['changes', 'full'] - defaults to 'changes'.
                This flag is used to indicate if the sync is supposed to compare
                the data in the source against the destination and only change
                necassary records in the destination. a full type sync takes the
                source data and forces the full set into the destination.
            'allow_partial_updates': bool - defaults to False
                Should be used to indicate if you would like to commit (or must)
                commit updates to be commited.
            'use_jazzhands_db': bool - defaults to False
                Used to indicate that this sync interacts with JazzHands. If you enable this
                you must also provide appauthal_app_name
            'appauthal_app_name': str - required only with use_jazzhands_db flag
        }
    """

    def __init__(self, record_type, args, record_sync_logger_key='record_sync_logger_conf'):
        """Inits a Sync.

        Args:
            args: argparse namespace object (should come from SyncOptions)
        """
        self.record_type = record_type
        self._dry_run = args.dry_run
        self._max_percent = args.max_percent
        self._force = args.force
        self._conf_file = args.conf_file
        self._req_attrs = None
        self._record_sync_logger_key = record_sync_logger_key
        self._sl = SafetyLimiter(max_p=self._max_percent, force=self._force)
        self._conf = self._load_conf(self._conf_file)
        if self._conf.get('use_jazzhands_db', False):
            try:
                # local import - have to do this here so there is no hard dependency on JH
                try:
                    from jh_recsynclib.db import JHDBRecordInterface
                except ImportError:
                    raise PackageError('DB functionality requires jazzhands_appauthal package')
                self.dbh = JHDBRecordInterface(
                    self._conf['appauthal_app_name'], record_type, conf=self._conf)
            except KeyError:
                raise SyncException(
                    'use_jazzhands_db option requires you to provide appauthal_app_name as well')
        else:
            self.dbh = None
        self._feedlgr = self._init_event_logger()
        self._sync_type = self._conf.get('sync_type', 'changes')

    def run_sync(self, sync_type=None, operations=('add', 'remove', 'modify')):
        """Runs the sync process.

        Args:
            sync_type: string - [ changes | full ] uses the class default set via
                configuration dictionary unless specified here.
                default default is 'changes'
            operations: list - ['add', 'remove', 'modify'] - specify which operations
                to complete for a "changes" sync type. sometimes you only want to do
                adds or deletes or mods. this is how. defaults to all three.
        """
        if not sync_type:
            sync_type = self._sync_type
        if sync_type == 'changes':
            return self._changes_sync(operations)
        elif sync_type == 'full':
            return self._full_sync()
        else:
            raise SyncException(
                'Not a valid sync_type: {}, must be changes or full'.format(
                    self._sync_type))
    
    def get_conf_key(self, key):
        """Returns the values of the requested key from the configuration dict.

        Args:
            key: string - the configuration key your requesting

        Returns:
            value from configuration dict
        """
        return self._conf.get(key)

    def _full_sync(self):
        """commences a full sync, taking all the data from the source and
        pushing it into the destination.  Object level data will not be logged
        as this would be needlessly noisy and not provide useful info"""
        self._feedlgr.start()
        try:
            records = self._get_source_dataset()
            LOG.debug('source dataset contains %s records', len(records))
            LOG.debug('attempting to update destination')
            self._update_destination(records)
            LOG.debug('update complete')
        except Exception as exc:
            LOG.exception(exc)
            LOG.debug('Rolling back any uncommited changes')
            self.rollback()
            self._feedlgr.fail(exc)
            raise exc
        if not self._dry_run:
            self.commit()
            LOG.info('Successfully updated: %s', len(records))
        else:
            self.rollback()
            LOG.info('Dry Run. Would have updated: %s', len(records))
        self._feedlgr.success()
        return True

    def _changes_sync(self, operations):
        """commences a change based sync that looks at the data in the source
        and destination, updating the destination with only differences for the
        operations passed. looks for ['add', 'remove', 'modify']"""
        #mark the start of execution in the db
        self._feedlgr.start()
        try:
            LOG.debug('operations requested: %s', operations)
            src = self._get_source_dataset()
            LOG.debug('source dataset contains %s records', len(src))
            dst = self._get_destination_dataset()
            LOG.debug('destination dataset contains %s records', len(dst))
            dos = JHRecordSyncer(src, dst)
            if 'add' in operations:
                adds = dos.get_additions()
                LOG.debug('%s records to be added', len(adds))
            else:
                adds = set()
            if 'remove' in operations:
                rms = dos.get_removals()
                LOG.debug('%s records to be removed', len(rms))
            else:
                rms = set()
            if 'modify' in operations:
                mods = dos.get_modifications()
                LOG.debug('%s records to be modified', len(mods))
            else:
                mods = set()
            self._sl.set_total_records(len(dst))
            self._sl.add_changes(len(adds) + len(rms) + len(mods))
            if not self._sl.check_changes():
                raise SyncException(self._sl.get_error_str())
            #run operations and collect any failures
            if not (adds or rms or mods):
                LOG.info('No changes found. Exiting')
                self._feedlgr.success()
                return True
            if 'add' in operations:
                LOG.debug('attempting to add new records')
                self._add_records(adds)
                LOG.debug('additions complete')
            if 'remove' in operations:
                LOG.debug('attempting to remove records')
                self._rm_records(rms)
                LOG.debug('removals complete')
            if 'modify' in operations:
                LOG.debug('attempting to modify records')
                self._modify_records(mods)
                LOG.debug('modifications complete')
        except Exception as exc:
            LOG.exception(exc)
            LOG.debug('Rolling back any uncommited changes')
            self.rollback()
            self._feedlgr.fail(exc)
            raise exc
        if not self._dry_run:
            self.commit()
            LOG.info(
                'Successfully added: %s, modified: %s, removed: %s',
                len(adds), len(mods), len(rms))
        else:
            self.rollback()
            LOG.info(
                'Dry Run. Would have added: %s, modified: %s,'
                ' removed: %s', len(adds), len(mods), len(rms))
        self._feedlgr.success()
        return True

    def throw_exception(self, exception):
        """This function takes an Exception, logs it and then raises it.  Used to handle
        and log exceptions outside of the canned functions.  useful for sublcasses to bail
        """
        self._feedlgr.fail(exception.message)
        raise exception

    def _init_event_logger(self):
        """Initializes the event and syslog logger. Requires that the
        sync configuration dictionary has been loaded and contains a
        recsync_logger_conf section."""
        conf = self._conf[self._record_sync_logger_key]
        if self._dry_run:
            conf['dry_run'] = True
        return JHRecordSyncLogger(conf)

    def _check_recs_req_attrs(self, records):
        """Verifies if a set of JHRecords have the fields required
        to feed them successfully into a destination system

        Args:
            records: sequence of JHRecords to check required fields on.

        Returns:
            A sequence of records that are missing
        """
        missing_req = []
        for record in records:
            if not self._req_attrs:
                factory = record.factory
                self._req_attrs = factory.get_rec_req_attrs()
            for attr in self._req_attrs:
                if not record.get(attr):
                    missing_req.append(record)
        return missing_req

    @staticmethod
    def _load_conf(conf_file):
        LOG.debug('Loading conf file from %s', conf_file)
        with open(conf_file, 'r') as cfh:
            return json.load(cfh)

    def _handle_op_exception(self, opr, obj, exc):
        "takes an operation and an exception and handles it"
        LOG.error(u'Failed to %s: %s', opr, obj)
        LOG.exception(exc)
        self.rollback()
        if self._conf.get('allow_partial_updates'):
            return
        raise exc

    def _check_partial(self):
        return bool(self._conf.get('allow_partial_updates') and not self._dry_run)

    def _commit_if_partial(self):
        "if allow_partial_updates is True, commit events immiedately"
        if self._check_partial():
            LOG.debug('allow_partial_updates true, commiting last change')
            self.commit()

    def _add_records(self, records):
        "Add a set of records into the destination."
        for s_rec in records:
            if not self._dry_run:
                try:
                    #create a new object and store the result in a temporary variable
                    d_rec = self._add_record(s_rec)
                    if not d_rec:
                        raise SyncException('No object returned from self._add_record(obj)')
                except Exception as exc:                                # pylint: disable=broad-except
                    self._handle_op_exception('add', s_rec, exc)
            else:
                d_rec = s_rec
            self._feedlgr.add_record(s_rec, d_rec)
            self._commit_if_partial()

    def _rm_records(self, records):
        "Remove a set of records from the destination."
        for d_rec in records:
            if not self._dry_run:
                try:
                    self._rm_record(d_rec)
                except Exception as exc:                                # pylint: disable=broad-except
                    self._handle_op_exception('rm', d_rec, exc)
            self._feedlgr.rm_record(d_rec)
            self._commit_if_partial()

    def _modify_records(self, records):
        """Update a set of records in the destination using a tuple of
        JHRecords. (source_record, destination_record)"""
        for o_t in records:
            s_rec, d_rec = o_t
            record = d_rec.diff(s_rec)
            if not self._dry_run:
                try:
                    self._modify_record(record)
                except Exception as exc:                                # pylint: disable=broad-except
                    self._handle_op_exception('modify', record, exc)
            self._feedlgr.modify_record(s_rec, d_rec)
            self._commit_if_partial()

    def commit(self):
        """Commit changes. Generally will just be used with self.dbh.commit()
        for database feeds.  This class is meant to be overloaded if you have
        a requirement to implement some custom commit foo.  Check out the
        Centerstone feed for an example"""
        if self.dbh:
            self.dbh.commit()
        self._feedlgr.commit()

    def rollback(self):
        """Rollback changes. Generally will just be self.dbh.rollback() for
        database feeds. This class is meant to be overloaded if you have to
        implement your own transactional endpoint"""
        if self.dbh:
            self.dbh.rollback()
        self._feedlgr.rollback()

    def _get_source_dataset(self):
        "Get set of JHRecords from the sync source.  Must be implemented"
        raise NotImplementedError

    def _get_destination_dataset(self):
        "Get set of JHRecords from the sync destination. Must be implemented"
        raise NotImplementedError

    def _add_record(self, obj):
        """Add a set of records into the destination. Must be implemented

        Must return the record that was just added
        """
        raise NotImplementedError

    def _rm_record(self, obj):
        "Remove a set of records from the destination. Must be implemented"
        raise NotImplementedError

    def _modify_record(self, obj):
        "Update a set of records in the destination. Must be implemented"
        raise NotImplementedError

    def _update_destination(self, records):
        """Replace all records in the destination. Only used with full syncs.
        Must be implemented"""
        raise NotImplementedError


class JHRecordSyncLogger(object):
    """Logs JHRecord changes to JH.  Also logs to the default
    logger as INFO.

    Example usage:
        rec_attr_map = {
            'department': {
                'dept_code': 'department',
                'cost_center_name': 'department',
                'cost_center_number': 'department',
                'account_collection_name': 'account_collection'
            }
        }
        l = JHRecordSyncLogger('JH', rec_attr_map)
        l.add_record(JHRecord)
        l.rm_record(JHRecord)
        l.modify_record(s_rec=JHRecord, d_rec=JHRecord)
        l.commit()
    """

    DEFAULT_APP_NAME = 'record_sync_logger'

    EVENT_TYPE_MAP = {
        'full': {
            'add': 'RecordAdded',
            'modify': 'RecordModified',
            'remove': 'RecordRemoved'
        },
        'partial': {
            'add': 'RecordAddSucceeded',
            'modify': 'RecordModifySucceeded',
            'remove': 'RecordRemoveSucceeded'
        }
    }

    def __init__(self, conf):
        """Inits a JHRecordSyncLogger

        Args:
            conf: recsync_logger_conf configuration dictionary

        Required Keys:
            source_subsystem: string. Source subsystem type.
            destination_subsystem: string. Destination subsystem type.

        Optional Keys:
            dblog: bool. defaults to True, sends messages to Sync Logs DB
            rec_attr_map: record attribute map dictionary.
            source_subsystem_instance: source subsystem instance name
            destination_subsystem_instance: source subsystem instance name
            app_name: string. appauthal application name
            syslog: bool. defaults to True, sends message to syslog
            dry_run: bool. setting dry run prevents any writes to the database. default False
            priority: string. default priority level to assign to events
                can be override on calls
            allow_partial_updates: bool - instructs the logger to log events immiedately. turns
                on autocommit.

        Object Attribute Map Dictionary:
            {
                'record_type': {
                    'attribute_name': 'entity_name'
                }
            }

        """
        self._conf = conf
        self._dblog = self._conf.get('dblog', True)
        if self._dblog:
            try:
                from jazzhands_feedlogger import FeedLogger, FeedLoggerException
            except ImportError:
                raise PackageError('DB functionality requires jazzhands_feedlogger package')
            if 'appauthal_app_name' not in self._conf:
                self._conf['appauthal_app_name'] = self.DEFAULT_APP_NAME
            try:
                self._feedlgr = FeedLogger(self._conf)
            except FeedLoggerException as exc:
                raise _JHRecordSyncLoggerException(
                    'Logging dictionary missing values. Message from FeedLogger: {}'.format(exc))
            self._rec_attr_map = self._conf.get('rec_attr_map')
            if not self._rec_attr_map:
                raise _JHRecordSyncLoggerException(
                    'Logging configuration dictionary missing: rec_attr_map')
        if self._conf.get('destination_subsystem_instance'):
            self._full_dest_subsys_name = '.'.join((
                self._conf['destination_subsystem'],
                self._conf['destination_subsystem_instance']))
        else:
            self._full_dest_subsys_name = self._conf['destination_subsystem']
        self._syslog = conf.get('syslog', True)
        self._priority = conf.get('priority', 'info')
        self._partial = self._conf.get('allow_partial_updates')

    def add_record(self, s_rec, d_rec):
        """takes source and destination JH record and logs addtion to subsystem
        Args:
            s_rec: source JHRecord
            d_rec: The record from destination system after inserting
        """
        msg = 'Added {}:{} to {}'.format(
            d_rec.record_type,
            d_rec.primary_key,
            self._full_dest_subsys_name)
        self._log_event(self._get_etype('add'), self._priority, msg, 'add', s_rec, d_rec)

    def rm_record(self, d_rec):
        """takes a JH record and logs removal to subsystem"""
        msg = 'Removed {}:{} from {}'.format(
            d_rec.record_type,
            d_rec.primary_key,
            self._full_dest_subsys_name)
        self._log_event(self._get_etype('remove'), self._priority, msg, 'remove', d_rec=d_rec)

    def modify_record(self, s_rec, d_rec):
        """takes two JH records and logs the modifications being made.

        Args:
            s_rec: source JHRecord who's data will be overwriting the
                destination records attributes
            d_rec: destination JHRecord.  original record in subsystem
                that is being modified
        """
        msg = 'Modified {}:{} in {}'.format(
            s_rec.record_type,
            s_rec.primary_key,
            self._full_dest_subsys_name)
        self._log_event(self._get_etype('modify'), self._priority, msg, 'modify', s_rec, d_rec)

    def commit(self):
        """commit log entries to JH"""
        if self._dblog:
            self._feedlgr.commit()

    def rollback(self):
        """rollback log entries to JH"""
        if self._dblog:
            self._feedlgr.rollback()

    def start(self):
        """Log a the start of a feed run"""
        self._log_event('ExecutionStarted', self._priority, 'Sync Execution Started')
        if self._dblog:
            self._feedlgr.commit()

    def fail(self, msg=None):
        """Log failure and rollback any uncommited events"""
        if not msg:
            msg = 'Sync Execution Failed'
        LOG.error('Rolling back uncommited changes.')
        self.rollback()
        self._log_event('ExecutionFailed', self._priority, str(msg))
        self.commit()
        if self._dblog:
            self._feedlgr.end_session()

    def success(self):
        """Commit any open event log items and an ExecutionStopped event"""
        self._log_event(
            'ExecutionStopped', self._priority, 'Sync Execution Completed Successfully')
        self.commit()
        if self._dblog:
            self._feedlgr.end_session()

    def _get_etype(self, action):
        if self._partial:
            return self.EVENT_TYPE_MAP['partial'][action]
        return self.EVENT_TYPE_MAP['full'][action]

    @staticmethod
    def _get_update_fields(s_rec, d_rec):
        s_rec = d_rec.diff(s_rec)
        return {attr: {'from': d_rec[attr], 'to': s_rec[attr]} for attr in s_rec}

    def _get_rec_attrs(self, action, s_rec=None, d_rec=None):
        """builds a dict to pass to save_attribute with proper fields"""
        attr_array = []
        if action == 'add':
            if not s_rec and not d_rec:
                raise _JHRecordSyncLoggerException(
                    'cannot log an addition without both s_rec and d_rec')
            # add the source key first
            attr_array = list(self._build_key_attr_dicts(s_rec, 'source').values())
            # build the rest of the entries. destination keys will be found automagically
            e_loc = 'destination'
            for attr_n, attr_v in d_rec.items():
                attr_array.append({
                    'entity_name': self._get_entity_name(d_rec, e_loc, attr_n),
                    'entity_location': e_loc,
                    'attribute_name': self._get_attribute_name(d_rec, e_loc, attr_n),
                    'key_type': self._get_key_type(d_rec, e_loc, attr_n),
                    'attribute_new_value': attr_v})
        elif action == 'remove':
            if not d_rec:
                raise _JHRecordSyncLoggerException(
                    'cannot log a removal without d_rec')
            # the only attributes that need to be added to a remove event are the destination keys
            attr_array = list(self._build_key_attr_dicts(d_rec, 'destination').values())
        elif action == 'modify':
            if not s_rec and not d_rec:
                raise _JHRecordSyncLoggerException(
                    'cannot log a modification without both s_rec and d_rec')
            # queue up keys to be added to the attribute array.  necassary to wait
            # on these until the rest of the attributes are processed to avoid
            # duplicates on key attributes that change
            attr_dict = {
                'source': self._build_key_attr_dicts(s_rec, 'source'),
                'destination': self._build_key_attr_dicts(d_rec, 'destination')
            }
            # using JHRecord diff to eliminate attributes that won't change
            s_rec = d_rec.diff(s_rec)
            e_loc = 'destination'
            for attr_n, attr_v in s_rec.items():
                attr_dict[e_loc].update({attr_n: {
                    'entity_name': self._get_entity_name(s_rec, e_loc, attr_n),
                    'entity_location': e_loc,
                    'attribute_name': self._get_attribute_name(s_rec, e_loc, attr_n),
                    'key_type': self._get_key_type(s_rec, e_loc, attr_n),
                    'attribute_value': d_rec.get(attr_n),
                    'attribute_new_value': attr_v}})
            # convert the attr_dict to a list and add to attr_array
            attr_array += list(attr_dict['source'].values())
            attr_array += list(attr_dict['destination'].values())
        return attr_array

    def _build_key_attr_dicts(self, record, entity_location):
        """Takes record and entity_location and builds a list of attribute dictionarys for use with
        a FeedLogger.  Only used on modify operations to setup the key entries.  use the more
        General _build_attr_dict for building the records for add/remove and the rest of a mods
        attrs"""
        key_attrs = {}
        ent_loc_conf = self._rec_attr_map[record.record_type][entity_location]
        for key in ent_loc_conf['keys']:
            key_attrs[key] = {
                'entity_location': entity_location,
                'attribute_name': ent_loc_conf.get('attr_map', {}).get(key, key),
                'key_type': ent_loc_conf['keys'].get(key, 'not_a_key'),
                'attribute_value': record[key]
            }
            if '*' in ent_loc_conf['entity_map']:
                key_attrs[key].update({'entity_name': ent_loc_conf['entity_map']['*']})
            else:
                key_attrs[key].update({'entity_name': ent_loc_conf['entity_map'][key]})
        return key_attrs

    def _get_entity_name(self, record, entity_location, attr_name):
        "Returns entity_name from record attribute map"
        wild = self._rec_attr_map[record.record_type][entity_location]['entity_map'].get('*')
        if wild:
            return wild
        return self._rec_attr_map[
            record.record_type][entity_location]['entity_map'][attr_name]

    def _get_attribute_name(self, record, entity_location, attr_name):
        "Returns attribute_name from record attribute map"
        return self._rec_attr_map[record.record_type][entity_location].get(
            'attr_map', {}).get(attr_name, attr_name)

    def _get_key_type(self, record, entity_location, attr_name):
        "Returns attribute_name from record attribute map"
        return self._rec_attr_map[record.record_type][entity_location]['keys'].get(
            attr_name, 'not_a_key')

    @staticmethod
    def _sanitize_sequence(value):
        """checks if value provided is a list or set and returns value in
        a list if its not"""
        if isinstance(value, (set, list)):
            return value
        return [value]

    def _log_event(self, event_type, priority, message, action=None, s_rec=None, d_rec=None):
        if self._dblog:
            if action:
                attrs = self._get_rec_attrs(action, s_rec, d_rec)
            else:
                attrs = None
            self._feedlgr.log_event(event_type, priority, message, attrs)
        if self._syslog:
            self._log_message(message)
            if action == 'modify':
                attrs = self._get_update_fields(s_rec, d_rec)
                for attr, vals in attrs.items():
                    i_msg = '{}.{} has changed from {} to {}'.format(
                        s_rec.primary_key, attr, vals['from'], vals['to'])
                    self._log_message(i_msg)

    @staticmethod
    def _log_message(message):
        try:
            message = text(message)
        except UnicodeDecodeError:
            message = message.decode('utf-8')
        LOG.info(message)


class JHRecordSyncer(object):
    """General class for comparing sets of JHRecords"""

    def __init__(self, source, dest):
        """Inits JHRecordSyncer

        Must be initialized with a source and destination set.

        Args:
            source: Set of source JHRecords.
            dest: Set of destination JHRecords.
        """
        self._source = source
        self._s_pk_dict = self._create_pkey_dict(source)
        self._s_pk_set = set(self._s_pk_dict.keys())
        self._dest = dest
        self._d_pk_dict = self._create_pkey_dict(dest)
        self._d_pk_set = set(self._d_pk_dict.keys())

    def get_additions(self):
        """Finds records that need to be added

        Determines set of JHRecords that are present in source and not
        in the destination. These records need to be inserted.

        Returns:
            A set of JHRecords that need to be added to the destination
        """
        k_set = self._s_pk_set - self._d_pk_set
        return {self._s_pk_dict[key] for key in k_set}

    def get_removals(self):
        """Finds records that need to be removed.

        Determines set of JHRecords that are not present in source but are
        present in the destination.  These records need to be deleted.

        Returns:
            A set of JHRecords that need to be added to the destination
        """
        k_set = self._d_pk_set - self._s_pk_set
        return {self._d_pk_dict[key] for key in k_set}

    def get_modifications(self):
        """Finds records that need to be modified.

        Determines set of JHRecords that have different attributes in the
        source than in the destination.  These records need to be modified.

        Returns:
            A set of tuples containing the source and destination JHRecords
            that need to be modified in the destination.
        """
        k_set = self._s_pk_set & self._d_pk_set
        r_set = {
            (self._s_pk_dict[k], self._d_pk_dict[k])
            for k in k_set
            if self._s_pk_dict[k] != self._d_pk_dict[k]}
        return r_set

    @staticmethod
    def _create_pkey_dict(set_):
        return {i.primary_key: i for i in set_}


class SyncException(Exception):
    "SyncException logs exception message as error"
    def __init__(self, message):
        LOG.error(message)
        super(SyncException, self).__init__(message)


class _JHRecordSyncLoggerException(Exception):
    pass
