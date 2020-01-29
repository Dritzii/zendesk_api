import psycopg2
import psycopg2.extras
import os
import sys



class db_credentials():
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                    dbname = "olinqua_zendesk",
                    user = "olinquazendesk",
                    password = "Olinqua1234@",
                    host = 'olinquazendesk.database.windows.net',
                    port = "1443")
            logging.info("Connection opened successfully.")
            self.connection.autocommit = True
        except psycopg2.DatabaseError as e:
            logging.error(e)
            

    def execute_query(self,query):
        self.cursor = self.connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
        self.cursor.execute(query)

    def execute_checkpostgis(self):
        try:
            db = database_credentials()
            db.execute_query(""" SELECT * from tickets; """)
            details = db.cursor.fetchall()
            print(details)
        except psycopg2.DatabaseError as e:
            print(e,sys.stderr)



if __name__ == "__main__":
    db_credentials()