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

"""Interact with JazzHands database

Classes for interacting with JazzHands database
"""

__author__ = 'Ryan D. Williams <rdw@drws-office.com>'

# Standard library imports
from copy import deepcopy

# Third-party imports
from jazzhands_appauthal.db import DatabaseConnection

# Local imports
from jh_recsynclib.utils import JHRecordFactory


class JHDBI(object):
    """This class contains all the functions for interacting with JazzHands"""

    def __init__(self, app_name, **kwargs):
        """kwargs can represent additional options passed to DB driver.
        kwargs are stored with this object and used for all subsequent connects"""
        self._app_name = app_name
        self._appauthal_db = DatabaseConnection(self._app_name)
        self._args = kwargs
        self.connect_db()

    def connect_db(self):
        """connects to the db and stores the handle in a private variable"""
        self._dbh = self._appauthal_db.connect(**self._args)

    def copy(self):
        """copies this connection and initiates new handle"""
        new_db = deepcopy(self)
        new_db.connect_db()
        return new_db

    def commit(self):
        "Commit transaction to DB"
        self._dbh.commit()

    def rollback(self):
        "Rollback transaction"
        self._dbh.rollback()

    def close(self):
        "Close Connection to DB"
        self._dbh.close()

    def _check_db_handle(self):
        if self._dbh.closed:
            self.connect_db()

    def _set_session_user(self, user):
        "Sets the jazzhands.appuser session variable for auditing"
        dbc = self.get_cursor()
        dbc.execute('SET LOCAL jazzhands.appuser TO %s', (user,))

    def get_cursor(self, calling_user=None):
        "Returns a psycopg2 DB cursor"
        self._check_db_handle()
        if calling_user:
            self._set_session_user(calling_user)
        return self._dbh.cursor()


class JHDBRecordInterface(JHDBI):
    """Superclass of JHDBI adding helper functions for working with
    JHRecords"""

    def __init__(self, app_name, record_type=None, table_map=None, **kwargs):
        """Inits a JHDBRecordInterface.

        Args:
            app_name: appauthal application name to use for connection to JH
            record_type: optional. JHRecord type
            table_map: optional. table_map dictionary. see set_table_map
        """
        self.record_type = record_type
        self._table_map = None
        self.set_table_map(table_map)
        kwargs.update({
            'psycopg2_cursor_factory': 'DictCursor'
        })
        super(JHDBRecordInterface, self).__init__(app_name, **kwargs)

    def set_table_map(self, table_map=None):
        """Sets the attribute map

        Currently requires a dictionary to be passed.  This should go away
        in favor of a db stored map.  Maybe it stays.

        Args:
            table_map: dictionary. currently rquired.

        Example:
            attr_endpoint_map = {
                "department": {
                    "account_collection_name": "account_collection",
                    "dept_code": "department",
                    "cost_center_name": "department",
                    "cost_center_number": "department"
                }
            }
        """
        self._table_map = table_map

    def query_jh_record(self, qry, record_type=None):
        """Queries JH and returns a set of JHRecords

        Args:
            qry: String. The query you wish to execute, column names must
                match attribute names in the output JHRecord
            record_type: Optional string. object type of the JHRecords to
                be created. defaults to one set during init

        Returns:
            A set of JHRecords using the values returned from the query
        """
        if not record_type:
            record_type = self.record_type
        dbc = self.get_cursor()
        dbc.execute(qry)
        new_dbh = JHDBRecordInterface(self._app_name, record_type=self.record_type, table_map=self._table_map)
        rec_factory = JHRecordFactory(record_type, db_handle=new_dbh)
        records = {rec_factory.create(row) for row in dbc.fetchall()}
        dbc.close()
        self.commit()
        return records

    def update_jh_record(self, rec, table_map=None, calling_user=None):
        """Updates JHRecord in JH

        Best to use the JHRecord produced by the diff method. Can either
        set the table map at init, using the set_table_map method or just
        supply one when calling this function

        Args:
            rec: JHRecord with the attrs you wish to update.
            table_map: optional. dictionary. see set_table_map.
            calling_user: optional. to be used when user initating action is not the db user

        Returns:
            number of rows affected
        """
        if not self._table_map and not table_map:
            raise JHDBIException('You must set the table_map')
        tmap = table_map if table_map else self._table_map
        upd = self._get_table_upd_dict(rec, tmap)
        dbc = self.get_cursor(calling_user)
        for table, avt in upd.items():
            fqry, val_arr = self._prep_qry(table, avt, rec)
            dbc.execute(fqry, val_arr)
            if dbc.rowcount != 1:
                self.rollback()
                raise JHDBIException('update effected more than one row.')

    @staticmethod
    def _get_table_upd_dict(rec, table_map):
        update = {}
        for attr, val in rec.items():
            update[table_map[attr]] = (
                update.get(table_map[attr], []) + [(attr, val)])
        return update

    def _prep_qry(self, table, avt, rec):
        """Takes table, attribute/value tuple and the object and
        returns a formated query and value array
        """
        qry = 'UPDATE {t_name} SET {a_names} = {vals} WHERE {w}'
        val_arr = []
        t_pkeys = self._get_table_pkeys(table)
        if len(avt) == 1:
            atr_str = avt[0][0]
            val_str = '%s'
            val_arr.append(avt[0][1])
        else:
            atr_str = '(' + ','.join((i[0] for i in avt)) + ')'
            val_str = '(' + ('%s,'*len(avt))[:-1] + ')'
            val_arr += [i[1] for i in avt]
        if len(t_pkeys) == 0:
            t_pkeys.append(self._args['conf']['default_pkey'])
        if len(t_pkeys) == 1:
            pkey = t_pkeys[0]
            w_str = '{} = %s'.format(pkey)
            val_arr.append(rec[pkey])
        else:
            w_l = []
            for pkey in t_pkeys:
                w_l.append('{} = %s'.format(pkey))
                val_arr.append(rec[pkey])
            w_str = ' AND '.join(w_l)
        fqry = qry.format(t_name=table, a_names=atr_str, vals=val_str, w=w_str)
        return fqry, val_arr

    def _get_table_pkeys(self, t_name):
        qry = """
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                 AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary"""
        dbc = self.get_cursor()
        dbc.execute(qry, (t_name,))
        return [r[0] for r in dbc.fetchall()]


class JHDBTransformerInterface(JHDBI):

    def __init__(self, app_name, config, **kwargs):
        self._config = config
        self._map = self._get_map()
        super(JHDBTransformerInterface, self).__init__(app_name, **kwargs)
    
    def _get_map(self):
        _map = dict()
        dbc = self._dbh.get_cursor()
        queries = self._config.get('queries', QUERIES)
        for field, qry in queries.items():
            dbc.execute(qry)
            _map[field] = {row[0]: row[1] for row in dbc.fetchall()}
        return _map
    
    def get_value_from_map(self, map_name, _key):
        """takes a map name and the key to retrieve.  Gets the value from the requested
        map"""
        if map_name not in self._map:
            raise JHDBTransformerInterfaceError('Requested map: {} not found'.format(map_name))
        return self._map[map_name].get(_key)


class JHDBIException(Exception):
    "JHDBIException class"
    pass


class JHDBTransformerInterfaceError(JHDBIException):
    "JHDBTransformerInterfaceError class"
    pass
