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

--feedlogs stuff
--init
\c feedlogs feedlogs
SET search_path = 'feedlogs';
--priority types
INSERT INTO val_event_priority (event_priority)
VALUES ('fatal'),('error'),('warn'),('info'),('debug'),('trace');
--event types
INSERT INTO val_event_type VALUES('ExecutionStarted', 'Execution of a script or feed started');
INSERT INTO val_event_type VALUES('ExecutionStopped', 'A script or feed completed execution successfully');
INSERT INTO val_event_type VALUES('ExecutionFailed', 'A script or feed failed');
INSERT INTO val_event_type VALUES('RecordAdded', 'Transaction based feed, record added');
INSERT INTO val_event_type VALUES('RecordRemoved', 'Transaction based feed, record removed');
INSERT INTO val_event_type VALUES('RecordModified', 'Transaction based feed, record modified');
INSERT INTO val_event_type VALUES('RecordAddSucceeded', 'Partial feed, record added successfully');
INSERT INTO val_event_type VALUES('RecordRemoveSucceeded', 'Partial feed, record removed successfully');
INSERT INTO val_event_type VALUES('RecordModifySucceeded', 'Partial feed, record modified successfully');
INSERT INTO val_event_type VALUES('RecordAddFailed', 'Partial feed, record addition failed');
INSERT INTO val_event_type VALUES('RecordRemoveFailed', 'Partial feed, record removal failed');
INSERT INTO val_event_type VALUES('RecordModifyFailed', 'Partial feed, record modification failed');
INSERT INTO val_event_type VALUES('ExecutionError', 'Major execution error');
--subsystems - uncomment to add
--INSERT INTO val_subsystem VALUES ('PostgreSQL');
--INSERT INTO val_subsystem VALUES ('MySQL');
--INSERT INTO val_subsystem VALUES ('Vertica');
--INSERT INTO val_subsystem VALUES ('OpenLDAP');
--INSERT INTO val_subsystem VALUES ('Active Directory');

--grants
\c feedlogs postgres
SET search_path = feedlogs;
CREATE USER feedlogger PASSWORD '<PASS GOES HERE>';
ALTER USER feedlogger SET search_path = feedlogs;
GRANT INSERT ON event, event_attribute, session TO feedlogger;
GRANT UPDATE (session_end) ON session TO feedlogger;
GRANT SELECT (event_id) ON event TO feedlogger;
GRANT SELECT (session_id) ON session TO feedlogger;
GRANT UPDATE ON event_event_id_seq, session_session_id_seq TO feedlogger;
GRANT feedlogs_usage_role TO feedlogger;
