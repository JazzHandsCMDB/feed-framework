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

\c feedlogs feedlogs

DROP SCHEMA IF EXISTS feedlogs;
CREATE SCHEMA feedlogs AUTHORIZATION feedlogs;
COMMENT ON SCHEMA feedlogs IS 'jazzhands extension';

SET search_path = feedlogs;

CREATE TABLE val_event_priority (
    event_priority  VARCHAR(64) PRIMARY KEY,
    description     TEXT
);

CREATE TABLE val_event_type (
    event_type      VARCHAR(64) PRIMARY KEY,
    description     TEXT
);
 
CREATE TABLE val_subsystem (
    subsystem       VARCHAR(64) PRIMARY KEY,
    description     TEXT
);

CREATE TABLE session (
    session_id                      SERIAL PRIMARY KEY,
    source_subsystem                VARCHAR(64) REFERENCES val_subsystem,
    source_subsystem_instance       VARCHAR,
    destination_subsystem           VARCHAR(64) REFERENCES val_subsystem,
    destination_subsystem_instance  VARCHAR,
    program_name                    VARCHAR(64) NOT NULL,
    username                        VARCHAR(64) NOT NULL,
    pid                             INTEGER NOT NULL,
    host_name                       VARCHAR NOT NULL,
    session_start                   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    session_end                     TIMESTAMP WITH TIME ZONE
);
CREATE INDEX session_ssub_index ON session (source_subsystem ASC);
CREATE INDEX session_ssubi_index ON session (source_subsystem_instance ASC);
CREATE INDEX session_dsub_index ON session (destination_subsystem ASC);
CREATE INDEX session_dsubi_index ON session (destination_subsystem_instance ASC);

CREATE TABLE event (
    event_id            SERIAL PRIMARY KEY,
    session_id          INTEGER REFERENCES session,
    event_type          VARCHAR(64) NOT NULL REFERENCES val_event_type,
    event_priority      VARCHAR(64) REFERENCES val_event_priority DEFAULT 'info',
    event_time          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message             TEXT
);
CREATE INDEX event_sid_index ON event (session_id ASC);
CREATE INDEX event_etype_index ON event (event_type ASC);

CREATE TABLE event_attribute (
    event_id            INTEGER NOT NULL REFERENCES event,
    entity_name         VARCHAR(1024) NOT NULL,
    entity_location     VARCHAR(11) CHECK (entity_location IN ('source', 'destination')),
    attribute_name      VARCHAR(1024) NOT NULL,
    key_type            VARCHAR(9) CHECK (key_type IN ('primary', 'alternate', 'not_a_key')),
    attribute_value     VARCHAR(1024),
    attribute_new_value VARCHAR(1024)
);
CREATE INDEX event_attr_eid_index ON event_attribute (event_id ASC);
