-- Copyright 2017 Ryan D. Williams
-- 
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
-- 
--     http://www.apache.org/licenses/LICENSE-2.0
-- 
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- prep
\c feedlogs
SET search_path = feedlogs;

--successful feed example
WITH _session AS (
    INSERT INTO session
        (source_subsystem, destination_subsystem, program_name, username, pid, host_name)
    VALUES
        ('HRIS', 'JazzHands', 'hris-feed', 'hris_feed', 1000, 'hris-feed.jazzhands.com')
    RETURNING session_id
), _event AS (
    INSERT INTO event
        (session_id, event_type, event_priority, message)
    VALUES
        ((SELECT session_id FROM _session), 'ExecutionStarted', 'info', 'HRIS feed started'),
        ((SELECT session_id FROM _session), 'RecordModifySucceeded', 'info', 'Modified EXEC. Changed cost_center_number from 100 to 100, account_collection_name from Executives to Corporate Executives'),
        ((SELECT session_id FROM _session), 'ExecutionStopped', 'info', 'HRIS completed successfully')
    RETURNING event_id, event_type
)
INSERT INTO event_attribute
    (event_id, entity_name, entity_location, key_type, attribute_name, attribute_value, attribute_new_value)
VALUES
    ((SELECT event_id FROM _event WHERE event_type = 'RecordModifySucceeded'), 'Department', 'source', 'primary', 'department-code', 'EXEC', NULL),
    ((SELECT event_id FROM _event WHERE event_type = 'RecordModifySucceeded'), 'account_collection', 'destination', 'primary', 'account_collection_id', 10000, NULL),
    ((SELECT event_id FROM _event WHERE event_type = 'RecordModifySucceeded'), 'department', 'destination', 'alternate', 'dept_code', 'EXEC', NULL),
    ((SELECT event_id FROM _event WHERE event_type = 'RecordModifySucceeded'), 'department', 'destination', 'not_a_key', 'cost_center_number', 100, 110),
    ((SELECT event_id FROM _event WHERE event_type = 'RecordModifySucceeded'), 'account_collection', 'destination', 'not_a_key', 'account_collection_name', 'Executives', 'Corporate Executives');
