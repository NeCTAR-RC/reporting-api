"""Encapsulates a set of pre-defined database queries,
gathering all SQL into one place.
"""

from datetime import timedelta
from datetime import tzinfo
from reporting_api.common.dbconn import ResultSet
from reporting_api.common.dbconn import ResultSetSlice


class UTC(tzinfo):
    """A timezone representing Coordinated Universal Time (UTC).
    """

    def utcoffset(self, dt):
        """UTC is always 0 offset from UTC.
        """
        return timedelta(0)

    def dst(self, dt):
        """UTC never has a Daylight Savings Time offset.
        """
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"


class DBQueries(object):
    """Holds a set of canned database queries.
    """

    QUERY_SHOW_TABLES = 'SHOW TABLES;'
    METADATA_TABLE = 'metadata'
    METADATA_LAST_UPDATE_COLUMN = 'last_update'
    METADATA_TABLE_NAME_COLUMN = 'table_name'

    @classmethod
    def get_tables_comments(cls, dbconn, dbname, table_names):
        """Return an iterator over the SQL92 table comments for the given tables.
        """
        # In this query, schema and table names are literals,
        # so can be parameters
        query = """
        SELECT
            table_comment
        FROM
            information_schema.tables
        WHERE
            table_schema=%s
            AND table_name IN (
        """ \
            + ",".join(['%s'] * len(table_names)) \
            + ");"
        parameters = [dbname]
        parameters.extend(table_names)
        cursor = dbconn.execute(query, False, parameters)
        return ResultSetSlice(cursor, 0)

    @classmethod
    def get_table_comment(cls, dbconn, dbname, table_name):
        """Obtain a single table's SQL92 table comment.
        """
        comments = cls.get_tables_comments(dbconn, dbname, [table_name])
        return iter(comments).next()

    @classmethod
    def get_table_lastupdates(cls, dbconn, table_names):
        """Return an iterator over the last update times for the given tables.
        This is looked for in an optional table named 'metadata'.
        FIXME: Remove this knowledge about the underlying schema.
        """
        # In this query, table names are literals, so can be parameters
        query = """SELECT %(last_update)s FROM %(table)s WHERE %(column)s
                   IN %(table_names)s""" % dict(
                last_update=dbconn.escape_identifier(
                    cls.METADATA_LAST_UPDATE_COLUMN),
                table=dbconn.escape_identifier(
                    cls.METADATA_TABLE),
                column=dbconn.escape_identifier(
                    cls.METADATA_TABLE_NAME_COLUMN),
                table_names="(" + ",".join(['%s'] * len(table_names)) + ");")
        cursor = dbconn.execute(query, False, table_names)
        return ResultSetSlice(cursor, 0)

    @classmethod
    def get_table_lastupdate(cls, dbconn, table_name):
        """Obtain a single table's last update time.
        """
        rows = cls.get_table_lastupdates(dbconn, [table_name])
        try:
            row = iter(rows).next()
            return row.replace(tzinfo=UTC())
        except StopIteration:
            return None

    @classmethod
    def get_table_list(cls, dbconn):
        """Return an iterator over names of available tables.
        """
        query = cls.QUERY_SHOW_TABLES
        cursor = dbconn.execute(query, False)
        return ResultSetSlice(cursor, 0)

    @classmethod
    def filter_table(cls, dbconn, table_name, filter_args):
        """Return an iterator over the records in a resultset
        selecting all columns from the given-named table.
        The filter_args are ANDed together then used as a WHERE criterion.
        """
        # Table names cannot be parameters, so must be escaped
        query = 'SELECT * FROM ' + dbconn.escape_identifier(table_name)
        parameters = []
        if filter_args:
            query += ' WHERE '
            criteria = []
            for (key, val) in filter_args.items():
                # Column names cannot be parameters, so must escaped
                criteria.append(dbconn.escape_identifier(key) + "=%s")
                # Filter values can be parameters
                parameters.append(val[0])
            query += ' AND '.join(criteria)
        query += ';'
        cursor = dbconn.execute(query, True, parameters)
        return ResultSet(cursor)
