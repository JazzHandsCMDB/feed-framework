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

-- feedlogs grants
\c feedlogs postgres
SET search_path = feedlogs;
GRANT feedlogs_usage_role TO feedlogs_ro_role;
GRANT USAGE ON SCHEMA feedlogs TO feedlogs_usage_role;
GRANT SELECT ON ALL TABLES IN SCHEMA feedlogs TO feedlogs_ro_role;