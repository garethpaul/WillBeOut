import pymysql


class Database:
    def __init__(self, host, database, user, password, connect=None):
        self._settings = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
        }
        self._connect = connect or pymysql.connect

    def _execute(self, statement, parameters, fetch):
        connection = self._connect(**self._settings)
        try:
            with connection.cursor() as cursor:
                rowcount = cursor.execute(statement, parameters)
                if fetch == "all":
                    return list(cursor.fetchall())
                if fetch == "one":
                    return cursor.fetchone()
                connection.commit()
                if fetch == "lastrowid":
                    return cursor.lastrowid
                return rowcount
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def query(self, statement, *parameters):
        return self._execute(statement, parameters, "all")

    def get(self, statement, *parameters):
        return self._execute(statement, parameters, "one")

    def execute(self, statement, *parameters):
        return self._execute(statement, parameters, None)

    def execute_rowcount(self, statement, *parameters):
        return self._execute(statement, parameters, None)

    def execute_lastrowid(self, statement, *parameters):
        return self._execute(statement, parameters, "lastrowid")
