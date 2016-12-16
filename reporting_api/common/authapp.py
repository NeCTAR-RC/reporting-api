"""
An Application which uses Keystone for authorisation using RBAC.
"""

import ConfigParser
from keystonemiddleware.auth_token import filter_factory as auth_filter_factory
from reporting_api.common.application import Application
import six


@six.add_metaclass
class KeystoneApplication(Application):
    """An Application which uses Keystone for authorisation using RBAC.
    """

    INI_SECTION = 'keystone_authtoken'

    def __init__(self, configuration):
        super(KeystoneApplication, self).__init__(configuration)
        self.required_role = self.config.get('authorisation', 'required_role')
        if self.required_role is None:
            raise ValueError("No required role supplied")

    @classmethod
    def _headers(cls):
        """Return a list of ('Header-Name', 'Header-Value') tuples,
        which should be added as HTTP headers to every response.

        Our responses depend on whether or not correct authentication was
        performed, yielding  a token, and if it was, whether that token
        authorises access to the given data.
        The token is passed in via the X-Auth-Token header,
        so our responses depend on it.
        """
        headers = super(KeystoneApplication, cls)._headers()
        headers.append(('Vary', 'X-Auth-Token'))
        return headers

    def _check_auth(self, req):
        if not self.required_role:
            return True
        if 'HTTP_X_ROLES' in req.environ:
            user_roles = req.environ['HTTP_X_ROLES'].split(',')
            return self.required_role in user_roles
        return False


def keystone_auth_filter_factory(global_config, **local_config):
    """A factory function which produces Keystone authentication
    WSGI filters.
    """
    global_config.update(local_config)
    config_file_name = global_config.get('config_file')
    if not config_file_name:
        raise ValueError('No config_file directive')
    config_file = ConfigParser.SafeConfigParser()
    if not config_file.read(config_file_name):
        raise ValueError("Cannot read config file '%s'" % config_file_name)
    global_config.update(config_file.items(KeystoneApplication.INI_SECTION))
    return auth_filter_factory(global_config)
