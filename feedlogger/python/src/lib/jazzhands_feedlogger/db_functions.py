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

"""Module containing helper functions for common tasks related to interacting
with the FeedLogs DB

Functions:
    add_nulls_to_vals - replace values that evaluate to false with None
    build_ins_query - builds an insert query
"""

def add_nulls_to_vals(columns, vals):
    """Takes a list of columns to be inserted/updated and a value dictionary.  Any columns
    that are not present in the dictionary keys will be added with a None value, translating
    to Null in the db. Used to help input dictionarys

    Args:
        columns (list of str): column names
        vals: (dict of str): keys = column names, values = their values

    Returns:
        dict: where columns not found in vals.keys() are added with a None value
    """
    new_vals = vals.copy()
    new_vals.update({col: None for col in columns if col not in vals})
    return new_vals

def build_ins_query(table, columns, returns=None):
    """Takes a table name, a list of columns and optional colunns to return after the
    insert is complete

    Args:
        table (str): table to insert into
        columns (list of str): ordered list of column names
        return (list of str): inserted column values you wish to return

    Returns:
        str: formated query
    """
    qry = 'INSERT INTO {table} {columns_str} VALUES {values_str}'
    qry_strs = {
        'columns_str': '(' + ','.join(columns) + ')',
        'values_str': '(' + ','.join(('%(' + col + ')s' for col in columns)) + ')'
    }
    if returns:
        qry += ' RETURNING {returns_str}'
        qry_strs['returns_str'] = '(' + ','.join(returns) + ')'
    fmtd_qry = qry.format(table=table, **qry_strs)
    return fmtd_qry
