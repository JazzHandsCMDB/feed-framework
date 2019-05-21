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

"""Utils n stuff

Helper classes for creating and manipulating JH records
"""

__author__ = 'Ryan D. Williams <rdw@drws-office.com>'


# Standard library imports
import os
import sys
import json
import logging
import datetime
from csv import reader as _reader, DictReader as _DictReader
from copy import deepcopy
from collections import OrderedDict


# Third-party imports
import jsonschema
import pkg_resources


LOG = logging.getLogger(__name__)


def csv_empty_string_to_null(reader):
    '''This is a util that will replace empty strings in CSV readers with None'''
    if isinstance(reader, type(_reader)):
        return [[val or None for val in row] for row in reader]
    else:
        if sys.version_info[:2] > (3, 5):
            return [{key: val or None for key, val in row.items()} for row in reader]
        rows = []
        for row in reader:
            new_dict = OrderedDict()
            for k, v in row.items():
                new_dict.update({k: v or None})
            rows.append(new_dict)
        return rows


class TemplatedDict(dict):
    """Dictionary that defaults to returning only keys in its template.

    Creates a dictionary that also stores a sequence to indicate
    relevant keys.  All comparison and iteration functions will only
    compare or emit keys and values contained in the template sequence.
    Must be created with a sequence record as the first argument.
    """
    def __init__(self, template, *args, **kwargs):
        """Inits TemplatedDict with provided key template.

        Args:
            template: sequence containing the keys for the template
            *args: dictionary args
            **kwargs: dictionary kwargs
        """
        self.template = template
        super(TemplatedDict, self).__init__(*args, **kwargs)

    def __iter__(self):
        for key in self.template:
            if key in self:
                yield key

    def __eq__(self, other):
        if not self.template == other.template:
            return False
        for key in self.template:
            if not dict.get(self, key) == dict.get(other, key):
                return False
        return True

    def __ne__(self, other):
        if not self.template == other.template:
            return True
        for key in self.template:
            if dict.get(self, key) != dict.get(other, key):
                return True
        return False

    def diff(self, other):
        """Accepts another TemplatedDict and emits a child with
        differences.

        Used to discover modifications needed to make self look like
        other.

        Args:
            other: TemplatedDict with same template

        Returns:
            A TemplatedDict in which the template only contains keys
            from that differ between self and other with the values from
            other. All values from self will remain except for those
            different in other. Also adds keys from other to child that
            were not found in self.
        """
        if not self.template == other.template:
            raise TemplatedDictException(
                'templates do not match: {} != {}'.format(
                    self.template, other.template))
        child = deepcopy(self)
        #fill in the missing attrs
        for key, val in self.all_iteritems():
            if key not in child:
                child[key] = val
        child.template = set()
        for key in self.template:
            if dict.get(self, key) != dict.get(other, key):
                child.template.add(key)
                child[key] = other[key]
        #add in missing keys from other
        for key, val in other.all_iteritems():
            if key not in child:
                child[key] = val
        return child

    # over_rides of the noraml dict functions to return only keys from the template

    def keys(self):
        "Returns a list of keys present here and in template"
        return [key for key in self]

    def iterkeys(self):
        "Returns a iterator that produces keys present here and in template"
        return self.__iter__()

    def all_keys(self):
        "Returns all keys"
        return dict.keys(self)

    def all_iterkeys(self):
        "Returns a generator that emits all keys"
        return dict.keys(self)

    def values(self):
        "Returns a list of values from keys found in template"
        return [self[key] for key in self]

    def itervalues(self):
        "Returns generator that produces values from keys found in template"
        for key in self:
            yield self[key]

    def all_values(self):
        "Returns a list of all values"
        return dict.values(self)

    def all_itervalues(self):
        "Returns a generator that produces all values"
        return dict.values(self)

    def items(self):
        "Returns a list of tuples containing key, value pairs from template"
        return [(key, self[key]) for key in self]

    def iteritems(self):
        "Returns a generator. Same output as items()"
        for key in self:
            yield (key, self[key])

    def all_items(self):
        "Returns a list of tuples containing all key, value pairs"
        return dict.items(self)

    def all_iteritems(self):
        "Returns a generator. Same output as all_items()"
        return dict.items(self)

    def check_attrs(self):
        """Returns a list of templated attributes that do not have values.

        Intended to be used as a check for completeness.

        Returns:
            A list of keys with empty values"""
        return [key for key in self.template if not key in self]


class TemplatedDictException(Exception):
    "Exception class for TemplatedDict type records"
    pass


class JHRecord(TemplatedDict):
    """JH Object class.

    Subclass of TemplatedDict. Represents a JH record, looks a lot
    like a TemplatedDict but has information about the primary key.
    """
    def __init__(self, conf, *args, **kwargs):
        """Inits a JHRecord with the given configuration

        Args:
            conf: dict (req) - JH Record configuration dict
                {
                    'record_type': str (req) - JH record type
                    'primary_keys': list (req) - primary key(s) of the record
                    'attribute_template': list (req) - attributes to include in template
                    'required_attributes': list (opt) - attributes required to create a new record
                    'factory': JHRecordFactory (opt) - reference to the factory that created
                        the record
                }
            *args: dict args
            **kwargs: dict kwargs

        Returns:
            JHRecord with any fields passed as args and kwargs assigned
        """
        vconf = JHRecordSyncConfigValidator('record')
        vconf.validate_conf(conf)
        self._conf = conf
        super(JHRecord, self).__init__(conf['attribute_template'], *args, **kwargs)

    @property
    def record_type(self):
        """returns the record type"""
        return self._conf['record_type']

    @property
    def factory(self):
        """returns the factory that created the record"""
        return self._conf['factory']

    @property
    def primary_keys_attributes(self):
        """returns the attributes used to build a primary key"""
        return self._conf['primary_keys']

    @property
    def required_attributes(self):
        """returns required attributes if set"""
        return self._conf.get('required_attributes')

    @property
    def primary_key(self):
        """returns the computed primary key using the primary key attributes"""
        pkeys = self._conf['primary_keys']
        if len(pkeys) == 1:
            return self[pkeys[0]]
        return (self[attr] for attr in pkeys)

    def __hash__(self):
        return hash(self.primary_key)

    def check_req_attrs(self):
        """Checks for the record for the attributes labeled as required in jh.

        Returns:
            List of missing attributes
        """
        if not self.required_attributes and not self.factory:
            raise JHRecordException(
                'Cannot determine required attrs. both required_attributes and factory are None')
        if not self.required_attributes:
            self._conf['required_attributes'] = self.factory.required_attributes
        return [key for key in self.required_attributes if key not in self]


class JHRecordException(Exception):
    """Exception class for JHRecord issues"""
    pass


class JHRecordFactory(object):
    """Creates JHRecords and sets configuration from JH.

    Helper class that creates a JHRecord with primary key pulled from
    JH based on the object_type supplied
    """

    def __init__(self, record_type, rec_def=None, db_handle=None, def_dir=None):
        """Inits JHRecordFactory to produce JHRecord objects.

        Uses record definition to create JHRecord objects. Record type must
        be included and either a definition dictionary OR EITHER an appauthal app name
        OR filesystem directory can be provided and the definition will be retrieved from
        JazzHands or the filesystem.

        Args:
            record_type: string (req) - The abstract record type
            rec_def: dict (optional) - Record definition
            db_handle: object (optional) - JHDBI or similiar object that implements
                .get_cursor and has the ability to connect JH to retreive the record definition.
            def_dir: string (optional) - Path to directory containing record definition files
                formated in json and using the .json extension.

        Returns:
            JHRecordFactory

        Examples:
            jrf = JHRecordFactory('openldap_user', rec_def={
                'required_attributes': ['id', 'name'],
                'optional_attributes': [],
                'primary_keys': ['id']})

            jrf = JHRecordFactory(record_type='openldap_user', app_name='ldap_sync')

            jrf = JHRecordFactory(record_type='openldap_user', def_dir='/etc/example')
        """
        self.record_type = record_type
        if rec_def:
            self._rec_def = rec_def
        elif db_handle:
            dbh = db_handle
            self._rec_def = self._get_record_definition_jh(dbh)
            dbh.close()
        elif def_dir:
            if not os.path.isdir(def_dir):
                raise JHRecordFactoryException('def_dir not a valid directory: {}'.format(def_dir))
            rec_def_file = os.path.join(def_dir, '{}.json'.format(self.record_type))
            self._rec_def = self._get_record_definition_fs(rec_def_file)
        self._validate_def()

    @property
    def primary_keys(self):
        """The record types primary key(s). Returned as list"""
        return self._rec_def['primary_keys']

    @property
    def attribute_template(self):
        """The record types attribute template"""
        return self._rec_def['optional_attributes'] + self._rec_def['required_attributes']

    @property
    def required_attributes(self):
        """The record types required attributes"""
        return self._rec_def['required_attributes']

    def _validate_def(self):
        vconf = JHRecordSyncConfigValidator('record_definition')
        vconf.validate_conf(self._rec_def)

    def _get_record_definition_jh(self, dbh):
        """Returns the record definition from JazzHands"""
        dbc = dbh.get_cursor()
        qry = """
            SELECT
                property_value_json
            FROM
                property
            WHERE
                property_type = 'jh-recsynclib_rec_def'
                AND
                property_name = %s
        """
        dbc.execute(qry, (self.record_type,))
        try:
            return dbc.fetchone()[0]
        except TypeError:
            raise JHRecordFactoryException(
                'no jh-recsynclib_rec_def found for {}'.format(self.record_type))

    @staticmethod
    def _get_record_definition_fs(rec_def_file):
        """returns the record definition from the filesystem"""
        with open(rec_def_file, 'r') as _fh:
            return json.load(_fh)

    def create(self, *args, **kwargs):
        """Creates a JHRecord from JH info.

        Uses the configuration pulled from JH to build JHRecord.

        Args:
            *args: dictionary args
            **kwargs: dictionary kwargs

        Returns:
            JHRecord
        """
        conf = {
            'record_type': self.record_type, 'primary_keys': self.primary_keys,
            'attribute_template': self.attribute_template, 'factory': self,
            'required_attributes': self.required_attributes}
        return JHRecord(conf, *args, **kwargs)


class JHRecordFactoryException(Exception):
    """For JHRecordFactory exceptions"""
    pass


class JHRecordSyncConfigValidator(object):
    """JHRecordSyncConfigValidator Class

    We use JSON Schema validation to ensure configuration dictionaries have the
    required parameters.

    Examples:
        confv = JHRecordSyncConfigValidator('record_definition')
        confv.verify({'test': 'value'})

    Raises:
        ConfigError
    """
    def __init__(self, config_type):
        """Inits a JHRecordSyncConfigValidator

        Args:
            config_type: string. the config type you are attempting to validate

        Returns:
            JHRecordSyncConfigValidator object
        """
        self._config_type = config_type
        schema_file = 'json_schema/{}.json'.format(config_type)
        if pkg_resources.resource_exists('jh_recsynclib', schema_file):
            self._schema_file = pkg_resources.resource_filename('jh_recsynclib', schema_file)
        else:
            self._schema_file = os.path.join(
                os.path.split(__file__)[0], '{}.json'.format(config_type))
        with open(self._schema_file, 'r') as _fh:
            self.schema = json.load(_fh)

    def validate_conf(self, conf):
        """Takes a conf dict and compares it against the schema declared in init"""
        try:
            jsonschema.validate(conf, self.schema)
        except jsonschema.ValidationError as exc:
            raise ConfigError(exc)


class ConfigError(Exception):
    """ConfigError stuff"""
    def __init__(self, exc, *args, **kwargs):
        """Processes jsonvalidator exception and produces more useful error message"""
        message = 'Config validation failure. '
        if exc.validator == 'required':
            message += 'Missing required key(s): {}'.format(', '.join(
                val for val in exc.validator_value if val not in exc.instance))
        elif exc.validator == 'type':
            key_base = exc.absolute_path.popleft()
            message += 'Incorrect type found for key: {}; expected: {}; found: {}'.format(
                '{}{}'.format(key_base, ''.join('[{}]'.format(val) for val in exc.absolute_path)),
                exc.validator_value, type(exc.instance).__name__)
        else:
            message = str(exc)
        super(ConfigError, self).__init__(message, *args, **kwargs)


class DictReader(_DictReader):
    '''This is a wrapper for DictReader on systems running Python versions 3.5 or earlier'''
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect="excel", *args, **kwds):
        super(DictReader, self).__init__(f, fieldnames, restkey, restval, dialect, *args, **kwds)

    def __next__(self):
        if self.line_num == 0:
            self.fieldnames
        row = next(self.reader)
        self.line_num = self.reader.line_num
        while row == []:
            row = next(self.reader)
        d = OrderedDict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


class Transformer(object):

    def __init__(self, config):
        self.conf = config
        if 'appauthal_app_name' in self.conf:
            from db import JHDBTransformerInterface
            self._drt = JHDBTransformerInterface(self.conf['appauthal_app_name'])
        else:
            self _drt = None
    
    def get_value(self, _dict, path):
        """takes a nested dict and a list representing the key path needed to
        retrieve the value needed"""
        cur_val = _dict.get(path[0])
        if not cur_val:
            LOG.debug('requested key not found: %s', path[0])
            return
        if len(path) == 1:
            return cur_val
        return self.get_value(cur_val, path[1:])

    def split_string(self, _str, delimiter):
        """splits the supplied string on the delimiter"""
        try:
            return _str.split(delimiter)
        except AttributeError:
            return [_str]
    
    def get_index(self, _list, _index):
        """returns the list item at the requested index"""
        if not _list:
            return _list
        return _list[_index]
    
    def prep_date_filter(self, date_obj):
        """takes the date_obj from a filter definition and returns a datetime object to compare
        something against"""
        if 'date' in date_obj:
            return datetime.datetime.strptime(date_obj['date'], '%Y-%m-%d')
        else:
            return datetime.datetime.now() + datetime.timedelta(**date_obj)

    def apply_rule_set(self, record, rule_set, label=None):
        """take a list of rules and apply them to the record in order to return a processed
        value"""
        #return the string or None if the rule_set isn't a rule_set but a static value
        _rec = record
        if isinstance(rule_set, str) or not rule_set:
            return rule_set
        # convience feature. allows for calling a single rule without the array if you want
        if isinstance(rule_set, dict):
            rule_set = [rule_set]
        for rule in rule_set:
            if len(rule.keys()) != 1:
                raise TransformerException("rule definitions must contain one and only one property") 
            _key = list(rule.keys())[0]
            _rec = getattr(self, 'rule_{}'.format(_key))(_rec, rule[_key])
        if label:
            record['_processed_fields'][label] = _rec
        return _rec
    
    def rule_function(self, _rec, args):
        """does the thing for function rules. this is pretty generic"""
        if isinstance(args, str):
            return getattr(self, args)(_rec)
        return getattr(self, args[0])(_rec, *args[1:])
    
    def rule_nested_value(self, _dict, path):
        """takes the nested dict to retrieve a value from and a list of strings that represent
        the path to the desired value transversing over the nested dicts"""
        LOG.debug('rule: nested_value')
        if not _dict:
            LOG.debug('_dict empty, returning')
            return
        return self.get_value(_dict, path)
    
    def rule_map(self, _val, _map):
        """take value and looks up its mapped value from the passed _map"""
        return self.conf['maps'][_map].get(_val)
    
    def rule_copy(self, record, field):
        """takes a worker and a processed field to copy/return"""
        if field in record['_processed_fields']:
            return record['_processed_fields'][field]
        return self.apply_rule_set(record, self.conf['rule_set'][field])
    
    def rule_coalesce(self, _rec, rule_sets):
        """takes an object and applies the rule sets in order. returns the first non None value"""
        for _rs in rule_sets:
            result = self.apply_rule_set(_rec, _rs)
            if result:
                return result
    
    def rule_default(self, _cur_val, _default_val):
        """just returns what was passed in"""
        if _cur_val:
            return _cur_val
        else:
            return _default_val

    def rule_multiply(self, _val, _multiple):
        """multiplies the values, converts to int and returns"""
        LOG.debug('rule_multiply: _val: %s, _multiple: %s', _val, _multiple)
        if not _val:
            LOG.debug('_val empty, returning')
            return
        return int(float(_val) * float(_multiple))
    
    def rule_drt(self, _val, _drt_field):
        """takes the supplied value and looks up agains the supplied field map from DRT"""
        if not self._drt:
            raise TransformerException('DRT rule requested but no DB connection configured')
        self._drt.get_value_from_map(_drt_field, _val)
    
    def rule_filter(self, worker, filters):
        """takes a worker and returns them if they don't match the filter provided.
        
        filter: list of dicts
            {'key': rule_set, 'values': ['things_to_match']}
        """
        LOG.debug('filter rule')
        for _filter in filters:
            _filter_hit = False
            if ('match' in _filter and
                    self.apply_rule_set(worker, _filter['rules']) in _filter['match']):
                _filter_hit = True
            elif ('not_match' in _filter and
                    self.apply_rule_set(worker, _filter['rules']) not in _filter['not_match']):
                _filter_hit = True
            elif 'after' in _filter or 'before' in _filter:
                term_date = self.apply_rule_set(worker, _filter['rules'])
                if term_date:
                    term_date = datetime.datetime.strptime(term_date, '%Y-%m-%d')
                    if _filter.get('after'):
                        if term_date > self.prep_date_filter(_filter['after']):
                            _filter_hit = True
                    elif _filter.get('before'):
                        if term_date < self.prep_date_filter(_filter['before']):
                            _filter_hit = True
            if _filter_hit:
                LOG.debug('hit filter. filter: %s', _filter)
                if _filter['action'] == 'keep':
                    return
                elif _filter['action'] == 'remove':
                    raise FilterMatch(worker)


class FilterMatch(Exception):
    """This exception is raised when the filter rule of the Transformer removes a record"""
    pass


class TransformerException(Exception):
    pass