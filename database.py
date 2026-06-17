import pymysql


class TransactionUnavailableError(RuntimeError):
    pass


class Database:
    TRANSACTIONAL_ENGINES = frozenset(("INNODB",))

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

    def execute_transaction(self, table_name, statements):
        connection = self._connect(**self._settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT ENGINE FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s""",
                    (table_name,),
                )
                table = cursor.fetchone()
                engine = table.get("ENGINE") if isinstance(table, dict) else None
                if not engine or str(engine).upper() not in self.TRANSACTIONAL_ENGINES:
                    raise TransactionUnavailableError(
                        "Availability storage does not support transactions"
                    )
                for statement, parameters in statements:
                    cursor.execute(statement, parameters)
                connection.commit()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass
            try:
                connection.close()
            except Exception:
                pass
            raise
        connection.close()
