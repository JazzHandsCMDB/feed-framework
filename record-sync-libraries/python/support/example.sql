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

-- Setup the val_property foo so you can create actual properties
INSERT INTO val_property
    (property_type, property_name, description, property_data_type, property_value_json_schema)
VALUES
    ('jh-recsynclib_rec_def', 'department','Representation of a Department', 'json',
    '{
        "$schema": "http://json-schema.org/draft-06/schema#",
        "title": "jh-recsynclib_rec_def",
        "description": "A JazzHands Record Definition",
        "type": "object",
        "required": ["required_attributes", "optional_attributes", "primary_keys"],
        "properties": {
            "required_attributes": {
                "type": "array",
                "items": {"type": "string"}
            },
            "optional_attributes": {
                "type": "array",
                "items": {"type": "string"}
            },
            "primary_keys": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }'::JSONB);

INSERT INTO property
    (property_type, property_name, property_value_json)
VALUES
    ('jh-recsynclib_rec_def', 'department', '{
        "required_attributes": ["dept_code", "account_collection_name"],
        "optional_attributes": ["cost_center_name", "cost_center_number", "is_active"],
        "primary_keys": ["dept_code"]
    }'::JSONB);