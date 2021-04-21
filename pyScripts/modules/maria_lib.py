'''Library class that holds general database-related functionality
'''
import os
import mariadb


class DbLib:
    def __init__(self):
        self.conn = None
        self.connect()
        self.cur = self.conn.cursor()

    def connect(self):
        '''Connect to MariaDB database based on credentials available via
           env vars.
        '''
        try:
            self.conn = mariadb.connect(
                user=os.environ.get("USER"),
                password=os.environ.get("PASS"),
                host=os.environ.get("HOST")
            )
            print("Successful connection")
        except (Exception, mariadb.Error) as error:
            print(f"Failed connection: {error}")
            sys.exit(1)


    def use_db(self, db):
        try:
            self.cur.execute(f"USE {db}")
            print(f"Using database {db}.")
        except (Exception, mariadb.Error) as error:
            print(f"Failed database use: {error}")

        
    def list_tables(self, content="all"):
        tables = []

        try:
            self.cur.execute("SHOW TABLES")

            for (table,) in self.cur.fetchall():
                if content == "all":
                    tables.append(table)
                else:
                    if content in table:
                        tables.append(table)

            return tables
        except (Exception, mariadb.Error) as error:
            print(f"Failed listing tables: {error}")


    def get_field_info(self):
        '''Retrieves the field info associated with a cursor.'''
        field_info = mariadb.fieldinfo()
        field_info_dict = {}

        for column in self.cur.description:
            column_name = column[0]
            column_type = field_info.type(column)
            column_flags = field_info.flag(column)

            field_info_dict[column_name] = {"type": column_type, "flags": column_flags}

        return field_info_dict


    def get_table_field_info(self, table):
        '''Retrieves the field info associated with a table.'''
        try:
            self.cur.execute(f"SELECT * FROM {table} LIMIT 1")

            field_info = self.get_field_info()
            return field_info
        except (Exception, mariadb.Error) as error:
            print(f"Failed retrieving field info: {error}")


    def disconnect(self):
        '''Disconnect from the database'''
        if self.conn is not None:
            self.conn.close()
            print("Successful disconnection")