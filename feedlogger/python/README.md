# Python Interface

``` python
#!/usr/bin/env python2.7

from jazzhands_feedlogger import FeedLogger

#for feeding systems that support transactions
conf = {
    'source_subsystem': 'HRIS',
    'destination_subsystem': 'JazzHands',
}

flgr = FeedLogger(conf)
flgr.log_event('ExecutionStarted', 'info', 'HRIS feed started')
flgr.commit()
attributes = [
    {
        'entity_name': 'Department',
        'entity_location': 'source',
        'attribute_name': 'deptartment-code',
        'key_type': 'primary',
        'attribute_value': 'EXEC'
    },
    {
        'entity_name': 'account_collection',
        'entity_location': 'destination',
        'attribute_name': 'account_collection_id',
        'key_type': 'primary',
        'attribute_value': 10000
    },
    {
        'entity_name': 'department',
        'entity_location': 'destination',
        'attribute_name': 'dept_code',
        'key_type': 'alternate',
        'attribute_value': 'EXEC'
    },
    {
        'entity_name': 'department',
        'entity_location': 'destination',
        'attribute_name': 'cost_center_number',
        'key_type': 'not_a_key',
        'attribute_value': 100,
        'attribute_new_value': 110
    },
    {
        'entity_name': 'account_collection',
        'entity_location': 'destination',
        'attribute_name': 'account_collection_name',
        'key_type': 'not_a_key',
        'attribute_value': 'Executives',
        'attribute_new_value': 'Corporate Executives'
    }
]
flgr.log_event(
    'RecordModifySucceeded',
    'info',
    'Modified EXEC. Changed cost_center_number from 100 to 100, account_collection_name from Executives to Corporate Executives',
    attributes)
flgr.log_event('ExecutionStopped', 'info', 'HRIS feed completed successfully')
flgr.end_session()

#With partial updates enabled.  for feeds that interact with systems that do not have transactions. commits all logs immiedately
conf = {
    'source_subsystem': 'JazzHands',
    'destination_subsystem': 'OpenLDAP',
    'allow_partial_updates': True
}

flgr = FeedLogger(conf)
flgr.log_event('ExecutionStarted', 'info', 'OpenLDAP feed started')
attributes = [
    {
        'entity_name': 'person',
        'entity_location': 'source',
        'attribute_name': 'person_id',
        'key_type': 'primary',
        'attribute_value': '100'
    },
    {
        'entity_name': 'uid=jimbo,ou=people,dc=jazzhands,dc=com',
        'entity_location': 'destination',
        'attribute_name': 'dn',
        'key_type': 'primary',
        'attribute_new_value': 'uid=jimbo,ou=people,dc=jazzhands,dc=com'
    },
    {
        'entity_name': 'uid=jimbo,ou=people,dc=jazzhands,dc=com',
        'entity_location': 'destination',
        'attribute_name': 'jazzHandsAccountId',
        'key_type': 'alternate',
        'attribute_new_value': 100
    },
    {
        'entity_name': 'uid=jimbo,ou=people,dc=jazzhands,dc=com',
        'entity_location': 'destination',
        'attribute_name': 'uid',
        'key_type': 'not_a_key',
        'attribute_new_value': 'jimbo'
    }
]
flgr.log_event(
    event_type='RecordAddSucceeded',
    event_priority='info',
    message='Added jimbo to OpenLDAP at uid=jimbo,ou=people,dc=jazzhands,dc=com',
    event_attrs=attributes)
flgr.log_event('ExecutionStopped', 'info', 'OpenLDAP feed completed successfully')
flgr.end_session()

#failure feed without event
conf = {
    'source_subsystem': 'JazzHands',
    'destination_subsystem': 'PostgreSQL',
    'destination_subsystem_instance': 'postgres.jazzhands.com'
}

flgr = FeedLogger(conf)
flgr.log_event('ExecutionStarted', 'info', 'Postgres feed started')
flgr.commit()
attributes = [
    {
        'entity_name': 'account',
        'entity_location': 'source',
        'attribute_name': 'login',
        'key_type': 'alternate',
        'attribute_value': 'jimbo'
    },
    {
        'entity_name': 'role',
        'entity_location': 'destination',
        'attribute_name': 'name',
        'key_type': 'primary',
        'attribute_value': 'jimbo'
    },
    {
        'entity_name': 'grants',
        'entity_location': 'destination',
        'attribute_name': 'role',
        'key_type': 'not_a_key',
        'attribute_new_value': 'jazzhands_ro,jazzhands_rw'
    }
]
try:
    flgr.log_event('RecordModifyHappy', 'info', 'Roles for jimbo changed to jazzhands_ro,jazzhands_rw')
except Exception as e:
    flgr.rollback()
    flgr.log_event('ExecutionFailed', 'error', str(e).splitlines()[0])
    flgr.commit()
flgr.end_session()

```
