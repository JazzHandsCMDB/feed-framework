table_pkeys_map = {
    "account": [
        "account_id"
    ],
    "account_assignd_cert": [
        "account_id",
        "x509_cert_id",
        "x509_key_usg"
    ],
    "account_auth_log": [
        "account_id",
        "account_auth_ts",
        "auth_resource",
        "account_auth_seq"
    ],
    "account_coll_type_relation": [
        "account_collection_type",
        "account_collection_relation"
    ],
    "account_collection": [
        "account_collection_id"
    ],
    "account_collection_account": [
        "account_id",
        "account_collection_id"
    ],
    "account_collection_hier": [
        "account_collection_id",
        "child_account_collection_id"
    ],
    "account_password": [
        "account_id",
        "account_realm_id",
        "password_type"
    ],
    "account_realm": [
        "account_realm_id"
    ],
    "account_realm_acct_coll_type": [
        "account_realm_id",
        "account_collection_type"
    ],
    "account_realm_company": [
        "account_realm_id",
        "company_id"
    ],
    "account_realm_password_type": [
        "password_type",
        "account_realm_id"
    ],
    "account_ssh_key": [
        "account_id",
        "ssh_key_id"
    ],
    "account_token": [
        "account_token_id"
    ],
    "account_unix_info": [
        "account_id"
    ],
    "appaal": [
        "appaal_id"
    ],
    "appaal_instance": [
        "appaal_instance_id"
    ],
    "appaal_instance_device_coll": [
        "appaal_instance_id",
        "device_collection_id"
    ],
    "appaal_instance_property": [
        "app_key",
        "appaal_group_name",
        "appaal_group_rank",
        "appaal_instance_id"
    ],
    "approval_instance": [
        "approval_instance_id"
    ],
    "approval_instance_item": [
        "approval_instance_item_id"
    ],
    "approval_instance_link": [
        "approval_instance_link_id"
    ],
    "approval_instance_step": [
        "approval_instance_step_id"
    ],
    "approval_instance_step_notify": [
        "approv_instance_step_notify_id"
    ],
    "approval_process": [
        "approval_process_id"
    ],
    "approval_process_chain": [
        "approval_process_chain_id"
    ],
    "asset": [
        "asset_id"
    ],
    "badge": [
        "card_number"
    ],
    "badge_type": [
        "badge_type_id"
    ],
    "certificate_signing_request": [
        "certificate_signing_request_id"
    ],
    "chassis_location": [
        "chassis_location_id"
    ],
    "circuit": [
        "circuit_id"
    ],
    "company": [
        "company_id"
    ],
    "company_collection": [
        "company_collection_id"
    ],
    "company_collection_company": [
        "company_id",
        "company_collection_id"
    ],
    "company_collection_hier": [
        "child_company_collection_id",
        "company_collection_id"
    ],
    "company_type": [
        "company_type",
        "company_id"
    ],
    "component": [
        "component_id"
    ],
    "component_property": [
        "component_property_id"
    ],
    "component_type": [
        "component_type_id"
    ],
    "component_type_component_func": [
        "component_function",
        "component_type_id"
    ],
    "component_type_slot_tmplt": [
        "component_type_slot_tmplt_id"
    ],
    "contract": [
        "contract_id"
    ],
    "contract_type": [
        "contract_id",
        "contract_type"
    ],
    "department": [
        "account_collection_id"
    ],
    "device": [
        "device_id"
    ],
    "device_collection": [
        "device_collection_id"
    ],
    "device_collection_assignd_cert": [
        "device_collection_id",
        "x509_cert_id",
        "x509_key_usg"
    ],
    "device_collection_device": [
        "device_id",
        "device_collection_id"
    ],
    "device_collection_hier": [
        "device_collection_id",
        "child_device_collection_id"
    ],
    "device_collection_ssh_key": [
        "device_collection_id",
        "ssh_key_id",
        "account_collection_id"
    ],
    "device_encapsulation_domain": [
        "device_id",
        "encapsulation_type"
    ],
    "device_layer2_network": [
        "layer2_network_id",
        "device_id"
    ],
    "device_management_controller": [
        "manager_device_id",
        "device_id"
    ],
    "device_note": [
        "note_id"
    ],
    "device_ssh_key": [
        "ssh_key_id",
        "device_id"
    ],
    "device_ticket": [
        "ticketing_system_id",
        "device_id",
        "ticket_number"
    ],
    "device_type": [
        "device_type_id"
    ],
    "device_type_module": [
        "device_type_module_name",
        "device_type_id"
    ],
    "device_type_module_device_type": [
        "device_type_module_name",
        "device_type_id",
        "module_device_type_id"
    ],
    "dns_change_record": [
        "dns_change_record_id"
    ],
    "dns_domain": [
        "dns_domain_id"
    ],
    "dns_domain_collection": [
        "dns_domain_collection_id"
    ],
    "dns_domain_collection_dns_dom": [
        "dns_domain_collection_id",
        "dns_domain_id"
    ],
    "dns_domain_collection_hier": [
        "child_dns_domain_collection_id",
        "dns_domain_collection_id"
    ],
    "dns_domain_ip_universe": [
        "dns_domain_id",
        "ip_universe_id"
    ],
    "dns_record": [
        "dns_record_id"
    ],
    "dns_record_relation": [
        "dns_record_id",
        "related_dns_record_id",
        "dns_record_relation_type"
    ],
    "encapsulation_domain": [
        "encapsulation_type",
        "encapsulation_domain"
    ],
    "encapsulation_range": [
        "encapsulation_range_id"
    ],
    "encryption_key": [
        "encryption_key_id"
    ],
    "inter_component_connection": [
        "inter_component_connection_id"
    ],
    "ip_universe": [
        "ip_universe_id"
    ],
    "ip_universe_visibility": [
        "visible_ip_universe_id",
        "ip_universe_id"
    ],
    "kerberos_realm": [
        "krb_realm_id"
    ],
    "klogin": [
        "klogin_id"
    ],
    "klogin_mclass": [
        "device_collection_id",
        "klogin_id"
    ],
    "l2_network_coll_l2_network": [
        "layer2_network_collection_id",
        "layer2_network_id"
    ],
    "l3_network_coll_l3_network": [
        "layer3_network_id",
        "layer3_network_collection_id"
    ],
    "layer2_connection": [
        "layer2_connection_id"
    ],
    "layer2_connection_l2_network": [
        "layer2_connection_id",
        "layer2_network_id"
    ],
    "layer2_network": [
        "layer2_network_id"
    ],
    "layer2_network_collection": [
        "layer2_network_collection_id"
    ],
    "layer2_network_collection_hier": [
        "child_l2_network_coll_id",
        "layer2_network_collection_id"
    ],
    "layer3_network": [
        "layer3_network_id"
    ],
    "layer3_network_collection": [
        "layer3_network_collection_id"
    ],
    "layer3_network_collection_hier": [
        "layer3_network_collection_id",
        "child_l3_network_coll_id"
    ],
    "logical_port": [
        "logical_port_id"
    ],
    "logical_port_slot": [
        "logical_port_id",
        "slot_id"
    ],
    "logical_volume": [
        "logical_volume_id"
    ],
    "logical_volume_property": [
        "logical_volume_property_id"
    ],
    "logical_volume_purpose": [
        "logical_volume_purpose",
        "logical_volume_id"
    ],
    "mlag_peering": [
        "mlag_peering_id"
    ],
    "netblock": [
        "netblock_id"
    ],
    "netblock_collection": [
        "netblock_collection_id"
    ],
    "netblock_collection_hier": [
        "netblock_collection_id",
        "child_netblock_collection_id"
    ],
    "netblock_collection_netblock": [
        "netblock_collection_id",
        "netblock_id"
    ],
    "network_interface": [
        "network_interface_id"
    ],
    "network_interface_netblock": [
        "network_interface_id",
        "device_id",
        "netblock_id"
    ],
    "network_interface_purpose": [
        "network_interface_purpose",
        "device_id"
    ],
    "network_range": [
        "network_range_id"
    ],
    "network_service": [
        "network_service_id"
    ],
    "operating_system": [
        "operating_system_id"
    ],
    "operating_system_snapshot": [
        "operating_system_snapshot_id"
    ],
    "person": [
        "person_id"
    ],
    "person_account_realm_company": [
        "account_realm_id",
        "person_id",
        "company_id"
    ],
    "person_auth_question": [
        "person_id",
        "auth_question_id"
    ],
    "person_company": [
        "company_id",
        "person_id"
    ],
    "person_company_attr": [
        "person_company_attr_name",
        "company_id",
        "person_id"
    ],
    "person_company_badge": [
        "company_id",
        "person_id",
        "badge_id"
    ],
    "person_contact": [
        "person_contact_id"
    ],
    "person_image": [
        "person_image_id"
    ],
    "person_image_usage": [
        "person_image_usage",
        "person_image_id"
    ],
    "person_location": [
        "person_location_id"
    ],
    "person_note": [
        "note_id"
    ],
    "person_parking_pass": [
        "person_id",
        "person_parking_pass_id"
    ],
    "person_vehicle": [
        "person_vehicle_id"
    ],
    "physical_address": [
        "physical_address_id"
    ],
    "physical_connection": [
        "physical_connection_id"
    ],
    "physicalish_volume": [
        "physicalish_volume_id"
    ],
    "private_key": [
        "private_key_id"
    ],
    "property": [
        "property_id"
    ],
    "property_collection": [
        "property_collection_id"
    ],
    "property_collection_hier": [
        "property_collection_id",
        "child_property_collection_id"
    ],
    "property_collection_property": [
        "property_collection_id",
        "property_type",
        "property_name"
    ],
    "pseudo_klogin": [
        "pseudo_klogin_id"
    ],
    "rack": [
        "rack_id"
    ],
    "rack_location": [
        "rack_location_id"
    ],
    "service_environment": [
        "service_environment_id"
    ],
    "service_environment_coll_hier": [
        "child_service_env_coll_id",
        "service_env_collection_id"
    ],
    "service_environment_collection": [
        "service_env_collection_id"
    ],
    "shared_netblock": [
        "shared_netblock_id"
    ],
    "shared_netblock_network_int": [
        "shared_netblock_id",
        "network_interface_id"
    ],
    "site": [
        "site_code"
    ],
    "slot": [
        "slot_id"
    ],
    "slot_type": [
        "slot_type_id"
    ],
    "slot_type_prmt_comp_slot_type": [
        "slot_type_id",
        "component_slot_type_id"
    ],
    "slot_type_prmt_rem_slot_type": [
        "slot_type_id",
        "remote_slot_type_id"
    ],
    "snmp_commstr": [
        "snmp_commstr_id"
    ],
    "ssh_key": [
        "ssh_key_id"
    ],
    "static_route": [
        "static_route_id"
    ],
    "static_route_template": [
        "static_route_template_id"
    ],
    "sudo_acct_col_device_collectio": [
        "sudo_alias_name",
        "account_collection_id",
        "device_collection_id"
    ],
    "sudo_alias": [
        "sudo_alias_name"
    ],
    "svc_environment_coll_svc_env": [
        "service_environment_id",
        "service_env_collection_id"
    ],
    "sw_package": [
        "sw_package_id"
    ],
    "ticketing_system": [
        "ticketing_system_id"
    ],
    "token": [
        "token_id"
    ],
    "token_collection": [
        "token_collection_id"
    ],
    "token_collection_hier": [
        "token_collection_id",
        "child_token_collection_id"
    ],
    "token_collection_token": [
        "token_collection_id",
        "token_id"
    ],
    "token_sequence": [
        "token_id"
    ],
    "unix_group": [
        "account_collection_id"
    ],
    "val_account_collection_relatio": [
        "account_collection_relation"
    ],
    "val_account_collection_type": [
        "account_collection_type"
    ],
    "val_account_role": [
        "account_role"
    ],
    "val_account_type": [
        "account_type"
    ],
    "val_app_key": [
        "appaal_group_name",
        "app_key"
    ],
    "val_app_key_values": [
        "app_value",
        "app_key",
        "appaal_group_name"
    ],
    "val_appaal_group_name": [
        "appaal_group_name"
    ],
    "val_approval_chain_resp_prd": [
        "approval_chain_response_period"
    ],
    "val_approval_expiration_action": [
        "approval_expiration_action"
    ],
    "val_approval_notifty_type": [
        "approval_notify_type"
    ],
    "val_approval_process_type": [
        "approval_process_type"
    ],
    "val_approval_type": [
        "approval_type"
    ],
    "val_attestation_frequency": [
        "attestation_frequency"
    ],
    "val_auth_question": [
        "auth_question_id"
    ],
    "val_auth_resource": [
        "auth_resource"
    ],
    "val_badge_status": [
        "badge_status"
    ],
    "val_cable_type": [
        "cable_type"
    ],
    "val_company_collection_type": [
        "company_collection_type"
    ],
    "val_company_type": [
        "company_type"
    ],
    "val_company_type_purpose": [
        "company_type_purpose"
    ],
    "val_component_function": [
        "component_function"
    ],
    "val_component_property": [
        "component_property_name",
        "component_property_type"
    ],
    "val_component_property_type": [
        "component_property_type"
    ],
    "val_component_property_value": [
        "component_property_name",
        "valid_property_value",
        "component_property_type"
    ],
    "val_contract_type": [
        "contract_type"
    ],
    "val_country_code": [
        "iso_country_code"
    ],
    "val_device_auto_mgmt_protocol": [
        "auto_mgmt_protocol"
    ],
    "val_device_collection_type": [
        "device_collection_type"
    ],
    "val_device_mgmt_ctrl_type": [
        "device_mgmt_control_type"
    ],
    "val_device_status": [
        "device_status"
    ],
    "val_diet": [
        "diet"
    ],
    "val_dns_class": [
        "dns_class"
    ],
    "val_dns_domain_collection_type": [
        "dns_domain_collection_type"
    ],
    "val_dns_domain_type": [
        "dns_domain_type"
    ],
    "val_dns_record_relation_type": [
        "dns_record_relation_type"
    ],
    "val_dns_srv_service": [
        "dns_srv_service"
    ],
    "val_dns_type": [
        "dns_type"
    ],
    "val_encapsulation_mode": [
        "encapsulation_type",
        "encapsulation_mode"
    ],
    "val_encapsulation_type": [
        "encapsulation_type"
    ],
    "val_encryption_key_purpose": [
        "encryption_key_purpose",
        "encryption_key_purpose_version"
    ],
    "val_encryption_method": [
        "encryption_method"
    ],
    "val_filesystem_type": [
        "filesystem_type"
    ],
    "val_image_type": [
        "image_type"
    ],
    "val_ip_namespace": [
        "ip_namespace"
    ],
    "val_iso_currency_code": [
        "iso_currency_code"
    ],
    "val_key_usg_reason_for_assgn": [
        "key_usage_reason_for_assign"
    ],
    "val_layer2_network_coll_type": [
        "layer2_network_collection_type"
    ],
    "val_layer3_network_coll_type": [
        "layer3_network_collection_type"
    ],
    "val_logical_port_type": [
        "logical_port_type"
    ],
    "val_logical_volume_property": [
        "filesystem_type",
        "logical_volume_property_name"
    ],
    "val_logical_volume_purpose": [
        "logical_volume_purpose"
    ],
    "val_logical_volume_type": [
        "logical_volume_type"
    ],
    "val_netblock_collection_type": [
        "netblock_collection_type"
    ],
    "val_netblock_status": [
        "netblock_status"
    ],
    "val_netblock_type": [
        "netblock_type"
    ],
    "val_network_interface_purpose": [
        "network_interface_purpose"
    ],
    "val_network_interface_type": [
        "network_interface_type"
    ],
    "val_network_range_type": [
        "network_range_type"
    ],
    "val_network_service_type": [
        "network_service_type"
    ],
    "val_operating_system_family": [
        "operating_system_family"
    ],
    "val_os_snapshot_type": [
        "operating_system_snapshot_type"
    ],
    "val_ownership_status": [
        "ownership_status"
    ],
    "val_package_relation_type": [
        "package_relation_type"
    ],
    "val_password_type": [
        "password_type"
    ],
    "val_person_company_attr_dtype": [
        "person_company_attr_data_type"
    ],
    "val_person_company_attr_name": [
        "person_company_attr_name"
    ],
    "val_person_company_attr_value": [
        "person_company_attr_value",
        "person_company_attr_name"
    ],
    "val_person_company_relation": [
        "person_company_relation"
    ],
    "val_person_contact_loc_type": [
        "person_contact_location_type"
    ],
    "val_person_contact_technology": [
        "person_contact_technology",
        "person_contact_type"
    ],
    "val_person_contact_type": [
        "person_contact_type"
    ],
    "val_person_image_usage": [
        "person_image_usage"
    ],
    "val_person_location_type": [
        "person_location_type"
    ],
    "val_person_status": [
        "person_status"
    ],
    "val_physical_address_type": [
        "physical_address_type"
    ],
    "val_physicalish_volume_type": [
        "physicalish_volume_type"
    ],
    "val_processor_architecture": [
        "processor_architecture"
    ],
    "val_production_state": [
        "production_state"
    ],
    "val_property": [
        "property_type",
        "property_name"
    ],
    "val_property_collection_type": [
        "property_collection_type"
    ],
    "val_property_data_type": [
        "property_data_type"
    ],
    "val_property_type": [
        "property_type"
    ],
    "val_property_value": [
        "valid_property_value",
        "property_name",
        "property_type"
    ],
    "val_pvt_key_encryption_type": [
        "private_key_encryption_type"
    ],
    "val_rack_type": [
        "rack_type"
    ],
    "val_raid_type": [
        "raid_type"
    ],
    "val_service_env_coll_type": [
        "service_env_collection_type"
    ],
    "val_shared_netblock_protocol": [
        "shared_netblock_protocol"
    ],
    "val_slot_function": [
        "slot_function"
    ],
    "val_slot_physical_interface": [
        "slot_function",
        "slot_physical_interface_type"
    ],
    "val_snmp_commstr_type": [
        "snmp_commstr_type"
    ],
    "val_ssh_key_type": [
        "ssh_key_type"
    ],
    "val_sw_package_type": [
        "sw_package_type"
    ],
    "val_token_collection_type": [
        "token_collection_type"
    ],
    "val_token_status": [
        "token_status"
    ],
    "val_token_type": [
        "token_type"
    ],
    "val_volume_group_purpose": [
        "volume_group_purpose"
    ],
    "val_volume_group_relation": [
        "volume_group_relation"
    ],
    "val_volume_group_type": [
        "volume_group_type"
    ],
    "val_x509_certificate_file_fmt": [
        "x509_file_format"
    ],
    "val_x509_certificate_type": [
        "x509_certificate_type"
    ],
    "val_x509_key_usage": [
        "x509_key_usg"
    ],
    "val_x509_key_usage_category": [
        "x509_key_usg_cat"
    ],
    "val_x509_revocation_reason": [
        "x509_revocation_reason"
    ],
    "volume_group": [
        "volume_group_id"
    ],
    "volume_group_physicalish_vol": [
        "volume_group_id",
        "physicalish_volume_id"
    ],
    "volume_group_purpose": [
        "volume_group_id",
        "volume_group_purpose"
    ],
    "x509_key_usage_attribute": [
        "x509_cert_id",
        "x509_key_usg"
    ],
    "x509_key_usage_categorization": [
        "x509_key_usg_cat",
        "x509_key_usg"
    ],
    "x509_key_usage_default": [
        "x509_key_usg",
        "x509_signed_certificate_id"
    ],
    "x509_signed_certificate": [
        "x509_signed_certificate_id"
    ]
}