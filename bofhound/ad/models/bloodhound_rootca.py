from bloodhound.ad.utils import ADUtils
from .bloodhound_object import BloodHoundObject
from bofhound.logger import OBJ_EXTRA_FMT, ColorScheme
import logging


class BloodHoundRootCA(BloodHoundObject):

    COMMON_PROPERTIES = [
        'domain', 'name', 'distinguishedname', 'domainsid', 'isaclprotected',
        'description', 'whencreated', 'certthumbprint', 'certname', 'certchain',
        'hasbasicconstraints', 'basicconstraintpathlength'
    ]

    def __init__(self, object):
        super().__init__(object)

        self._entry_type = "RootCA"
        self.ContainedBy = []
        self.IsACLProtected = False
        self.IsDeleted = False
        self.x509Certificate = None

        if 'objectguid' in object.keys():
            self.ObjectIdentifier = object.get("objectguid")

        if 'distinguishedname' in object.keys():
            domain = ADUtils.ldap2domain(object.get('distinguishedname')).upper()
            self.Properties['domain'] = domain
            self.Properties['distinguishedname'] = object.get('distinguishedname').upper()

        if 'description' in object.keys():
            self.Properties['description'] = object.get('description')
        else:
            self.Properties['description'] = None

        if 'name' in object.keys():
            if 'domain' in self.Properties.keys():
                self.Properties['name'] = object.get('name').upper() + "@" + self.Properties['domain'].upper()

        if 'cacertificate' in object.keys():
            self.parse_cacertificate(object)
            # root CA certificates are self-signed
            self.Properties['certchain'] = [ self.Properties['certthumbprint'] ]

  
    def to_json(self, only_common_properties=True):
        self.Properties['isaclprotected'] = self.IsACLProtected
        data = super().to_json(only_common_properties)
        data['IsACLProtected'] = self.IsACLProtected
        data['IsDeleted'] = self.IsDeleted
        data["ObjectIdentifier"] = self.ObjectIdentifier
        data["ContainedBy"] = self.ContainedBy
        data["Aces"] = self.Aces

        if "domainsid" in self.Properties:
            data["DomainSID"] = self.Properties["domainsid"]

        return data