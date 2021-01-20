--
-- Copyright (c) 2021 Bernard Jech
-- All rights reserved.
-- 
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
-- 
--      http://www.apache.org/licenses/LICENSE-2.0
-- 
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--

DO $$
DECLARE
        _tal INTEGER;
BEGIN
        select count(*)
        from pg_catalog.pg_namespace
        into _tal
        where nspname = 'feed_recsynclib';
        IF _tal = 0 THEN
                DROP SCHEMA IF EXISTS feed_recsynclib;
                CREATE SCHEMA feed_recsynclib AUTHORIZATION jazzhands;
		REVOKE ALL ON SCHEMA feed_recsynclib FROM public;
		COMMENT ON SCHEMA feed_recsynclib IS 'part of jazzhands';
        END IF;
END;
$$;

/*******************************************************************************

Returns the value of the jh-recsynclib_rec_def property of the specified name

*******************************************************************************/

CREATE OR REPLACE FUNCTION feed_recsynclib.get_record_definition
(
	property_name	property.property_name%TYPE
) RETURNS jsonb AS $$
DECLARE
	rv jsonb;
BEGIN
	SELECT property_value_json INTO rv FROM property p
	WHERE property_type = 'jh-recsynclib_rec_def'
	AND p.property_name = get_record_definition.property_name;

	RETURN rv;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path TO jazzhands;


REVOKE ALL ON SCHEMA feed_recsynclib FROM public;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA feed_recsynclib FROM public;

GRANT USAGE ON SCHEMA feed_recsynclib TO ro_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA feed_recsynclib TO ro_role;
