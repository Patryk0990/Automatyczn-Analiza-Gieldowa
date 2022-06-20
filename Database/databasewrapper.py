import Database.config as db_config
from pathlib import Path
import pandas as pd
import csv
from io import StringIO
import psycopg2


class DatabaseWrapper:

    def __init__(self, config=db_config):
        self.__username = config.USERNAME
        self.__password = config.PASSWORD
        self.__host = config.HOST
        self.__port = config.PORT
        self.__database_name = config.DATABASE_NAME

    def __connect(self):
        try:
            connection = psycopg2.connect(
                user=self.__username,
                password=self.__password,
                host=self.__host,
                port=self.__port,
                database=self.__database_name
            )
            connection.autocommit = True
            return connection
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        return None

    def create_database_schema(self):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    path = str(Path(__file__).parent.absolute())
                    cursor.execute(open((path + "\\Database_schemas\\users.sql"), "r").read())
                    cursor.execute(open((path + "\\Database_schemas\\users_interface_settings.sql"), "r").read())
                    cursor.execute(open((path + "\\Database_schemas\\users_api_settings.sql"), "r").read())
                    cursor.execute(open((path + "\\Database_schemas\\stocks.sql"), "r").read())
                except Exception as error:
                    print("Error while creating database schema", error)

    def bulk_create(self, table, list_of_dicts):
        df = pd.DataFrame(list_of_dicts)
        sio = StringIO()
        csv.writer(sio, delimiter=";").writerows(df.values)
        sio.seek(0)

        cols = ""
        loop_counter = 0
        for col in df.columns:
            if loop_counter != 0:
                cols += ", "
            cols += col
            loop_counter += 1

        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "COPY %s({}) FROM STDIN CSV HEADER DELIMITER AS ';';".format(cols) % table
                    cursor.copy_expert(
                        sql=sql,
                        file=sio
                    )
                    return True
                except Exception as error:
                    print("Error while bulk inserting into %s" % table, error)
        return None

    def create(self, table, **kwargs):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "INSERT INTO %s(" % table
                    loop_counter = 0
                    columns = ""
                    values = ""
                    for key in kwargs:
                        if loop_counter > 0:
                            columns += ", "
                            values += ", "
                        columns += ("%s" % key)
                        values += "%s"
                        loop_counter += 1
                    sql += columns + ") VALUES(" + values + ")" + " RETURNING id"
                    cursor.execute(sql, tuple(kwargs.values()))
                    return cursor.fetchone()[0]
                except Exception as error:
                    print("Error while inserting into %s" % table, error)
        return None

    def read(self, table, order_by=None, order_direction='ASC', limit='ALL', offset=None, **kwargs):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "SELECT * FROM %s" % table
                    loop_counter = 0
                    for key in kwargs:
                        if loop_counter == 0:
                            sql += " WHERE "
                        elif loop_counter > 0:
                            sql += " AND "
                        if str(kwargs.get(key)).startswith("%") and str(kwargs.get(key)).endswith("%"):
                            sql += ("{} LIKE %s".format(key))
                        else:
                            sql += ("{}=%s".format(key))
                        loop_counter += 1
                    if order_by is not None:
                        sql += f" ORDER BY {order_by} {order_direction}"
                    sql += f" LIMIT {limit}"
                    if offset is not None:
                        sql += f"OFFSET {offset}"

                    cursor.execute(sql, tuple(kwargs.values()))
                    return cursor.fetchall()
                except Exception as error:
                    print("Error while searching from %s" % table, error)
        return None

    def update(self, table, primary_key, **kwargs):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "UPDATE %s SET " % table
                    loop_counter = 0
                    for key in kwargs:
                        if loop_counter > 0:
                            sql += ", "
                        sql += ("{}=%s".format(key))
                        loop_counter += 1
                    if table == "users_interface_settings" or table == "users_api_settings":
                        sql += f" WHERE user_id={primary_key}"
                    else:
                        sql += f" WHERE id={primary_key}"
                    cursor.execute(sql, tuple(kwargs.values()))
                    return cursor.rowcount
                except Exception as error:
                    print("Error while updating in %s" % table, error)
        return None

    def delete(self, table, primary_key):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = "DELETE FROM %s" % table
                    if table == "users_interface_settings" or table == "users_api_settings":
                        sql += f" WHERE user_id={primary_key}"
                    else:
                        sql += f" WHERE id={primary_key}"
                    cursor.execute(sql)
                    return cursor.rowcount
                except Exception as error:
                    print("Error while deleting from %s" % table, error)
        return None

    def truncate(self, table):
        with self.__connect() as connection:
            with connection.cursor() as cursor:
                try:
                    sql = f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"
                    cursor.execute(sql)
                    return True
                except Exception as error:
                    print("Error while truncating from %s" % table, error)
        return None
