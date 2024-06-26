import pytest
from bofhound.local import LocalBroker
from tests.test_data import *

KNOWN_DOMAIN_SIDS = [
    "S-1-5-21-1308756548-3893869957-2915408613"
]


def test_import_netloggedon_objects(netloggedon_redania_objects):
    local_broker = LocalBroker()
    local_broker.import_objects(netloggedon_redania_objects, KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.privileged_sessions) == 1


def test_import_netsession_netapi_objects(netsession_redania_netapi_objects):
    local_broker = LocalBroker()
    local_broker.import_objects(netsession_redania_netapi_objects, KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.sessions) == 1


def test_import_netsession_netapi_anonymous():
    anonymous = {"ObjectType": "Session", "User": "anonymous logon", "ComputerName": "TRETOGOR", "ComputerDomain": "REDANIA"}
    local_broker = LocalBroker()
    local_broker.import_objects([anonymous], KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.sessions) == 0


def test_import_netsession_dns_objects(netsession_redania_dns_objects):
    local_broker = LocalBroker()
    local_broker.import_objects(netsession_redania_dns_objects, KNOWN_DOMAIN_SIDS)

    assert len(local_broker.sessions) == 1


def test_import_netsession_dns_anonymous():
    anonymous = {"ObjectType": "Session", "User": "anonymous logon", "PTR": "tretogor.redania.local"}
    local_broker = LocalBroker()
    local_broker.import_objects([anonymous], KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.sessions) == 0


def test_import_netlocalgroup_objects(netlocalgroup_redania_objects):
    local_broker = LocalBroker()
    local_broker.import_objects(netlocalgroup_redania_objects, KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.local_group_memberships) == 3


def test_import_netlocalgroup_invalid_group():
    bad_group = {"ObjectType": "LocalGroupMembership", "Member": "Administrator", "Host": "oxenfurt.redania,local", "Group": "BadGroup"}
    local_broker = LocalBroker()
    local_broker.import_objects([bad_group], KNOWN_DOMAIN_SIDS)
    
    assert len(local_broker.local_group_memberships) == 0


def test_import_regsession_objects(regsession_redania_objects):
    local_broker = LocalBroker()
    local_broker.import_objects(regsession_redania_objects, KNOWN_DOMAIN_SIDS)

    assert len(local_broker.registry_sessions) == 3


def test_objects_with_ip_as_host():
    priv_session = {
        "ObjectType": "PrivilegedSession",
        "Username": "Administrator",
        "Domain": "REDANIA",
        "Host": "192.168.0.235"
    }
    registry_session = {
        "ObjectType": "RegistrySession",
        "UserSid": "S-1-5-21-1308756548-3893869957-2915408613-500",
        "Host": "192.168.0.215"
    }
    local_group_membership = {
        "ObjectType": "LocalGroupMembership",
        "Host": "192.168.0.215",
        "Group": "Administrators",
        "Member": "REDANIA\\Domain Admins",
        "MemberSid": "S-1-5-21-1308756548-3893869957-2915408613-512",
        "MemberSidType": "Group"
    }

    # Sessions resolved through NetSessionEnum will not have an IP host

    local_broker = LocalBroker()
    local_broker.import_objects(
        [
            priv_session,
            registry_session,
            local_group_membership
        ],
        KNOWN_DOMAIN_SIDS
    )

    assert len(local_broker.privileged_sessions) == 0
    assert len(local_broker.registry_sessions) == 0
    assert len(local_broker.local_group_memberships) == 0