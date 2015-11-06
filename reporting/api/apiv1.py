import ConfigParser
import webob.exc
from reporting.common.apiversion import APIVersion
from reporting.common.dbconn import DBConnection
from reporting.api.dbqueries import DBQueries
from wsgiref.handlers import format_date_time
from time import mktime


class APIv1App(APIVersion):

    def __init__(self, configuration):
        super(APIVersion, self).__init__(configuration)
        self.dbname = self.config.get('database', 'dbname')
        self.dbhost = self.config.get('database', 'hostname')
        self.dbuser = self.config.get('database', 'username')
        self.dbpass = self.config.get('database', 'password')

    def _connect_db(self):
        return DBConnection(
            host=self.dbhost,
            user=self.dbuser,
            password=self.dbpass,
            database=self.dbname
        )

    @classmethod
    def _version_identifier(cls):
        return "v1"

    @classmethod
    def _get_links(cls):
        # TODO: Obtain this from the Swagger specification(s)
        return dict(
            reports = '/v1/reports'
        )

    @classmethod
    def _get_report_links(cls, report):
        # TODO: Obtain this from the Swagger specification(s)
        return dict(
            self = '/v1/reports/' + report
        )

    def _get_report_details(self, dbconn, report_name):
        return dict(
                name=report_name,
                description=DBQueries.get_table_comment(
                    dbconn, self.dbname, report_name
                ),
                lastUpdated=DBQueries.get_table_lastupdate(
                    dbconn, report_name
                ),
                links=self._get_report_links(report_name)
            )

    def ReportsList(self, req, args):
        dbconn = self._connect_db()
        report_name_iter = DBQueries.get_table_list(dbconn)
        # The current resultset must be entirely read before another query
        # can be performed on the same connection.
        # This means we must either finish reading all report names before
        # reading all report details, or must use multiple connections.
        report_names = [report_name for report_name in report_name_iter]
        return ([
            self._get_report_details(dbconn, report_name)
            for report_name in report_names
        ], None)

    def ReportResultSet(self, req, args):
        dbconn = self._connect_db()
        table_name = args['report']
        del args['report']
        server_modified = DBQueries.get_table_lastupdate(dbconn, table_name)
        headers = [(
            'Last-Modified',
            format_date_time(mktime(server_modified.timetuple()))
        )]
        # Handle conditional requests
        if not args:
            if req.if_modified_since and req.if_modified_since >= server_modified:
                return ( webob.exc.HTTPNotModified(), headers )
        try:
            result_set = DBQueries.filter_table(dbconn, table_name, args)
        except:
            # Don't leak information about the database
            return (webob.exc.HTTPBadRequest(), [])
        return (result_set, headers)

APIVersion.version_classes.append(APIv1App)


def app_factory(global_config, **local_config):
    global_config.update(local_config)
    config_file_name = global_config.get('config_file')
    if not config_file_name:
        raise ValueError('No config_file directive')
    config_file = ConfigParser.SafeConfigParser()
    if not config_file.read(config_file_name):
        raise ValueError("Cannot read config file '%s'" % config_file_name)
    return APIv1App(config_file)
