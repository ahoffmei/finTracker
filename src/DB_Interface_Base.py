import os
import pathlib 
import sqlite3 
import traceback
import pandas as pd 
from datetime import datetime 
from abc import ABC, abstractmethod

class DB_Interface_Base(ABC):
    def __init__(self, db_name : str, base_db_path : pathlib.Path, db_tables : list):
        # Init variables
        self.db_name        = db_name
        self.base_db_path   = base_db_path
        self.db_path        = os.path.join(base_db_path, self.db_name)
        self.db_tables      = db_tables 

        # Private variables for db access 
        self.__connection   = None 
        self.__cursor       = None

        self.___validateInputs___() 

        # Init db 
        self.___connect___() 
        self.___initTable___()
        self.___close___() 


    def ___validateInputs___(self):
        if not os.path.exists(self.base_db_path):
            raise FileNotFoundError(f"Directory path DNE: {self.base_db_path}")
        
        if not os.path.isdir(self.base_db_path):
            raise NotADirectoryError(f"Input base_db_path is not a directory: {self.base_db_path}")


    # def __del__(self):
    #     self.___close___()


    def ___connect___(self): 
        """
        @brief  Connect to SQLite3 db 
        """
        try: 
            self.__connection = sqlite3.connect(self.db_path)
            self.__cursor     = self.__connection.cursor()
        except sqlite3.Error as err: 
            print(f"Connection error: {err}") 


    def ___initTable___(self): 
        """
        @brief  Create table 
        """
        try: 
            for table in self.db_tables: 
                self.__cursor.execute(table)
            self.__connection.commit()
        except sqlite3.Error as err: 
            self.__connection.rollback()


    def ___close___(self):
        """
        @brief  Closes db connection 
        """
        if not self.__connection:
            print("[Warning] No valid connection to close")
        else: 
            try: 
                self.__connection.close()
            except sqlite3.Error as err:
                print(f"Error closing connection: {err}") 


    def _readDb(self, query: str, params : dict = None) -> pd.DataFrame: 
        """
        @brief  Protected function for handling read queries
        @param  query  : sql query in string form 
        @param  params : dictionary of :keyword to parameter value
        """ 
        self.___connect___()
        results = pd.DataFrame()
        try:
            if params: 
                results = pd.read_sql_query(query, self.__connection, params=params)
            else:
                results = pd.read_sql_query(query, self.__connection, params=params)
        except sqlite3.Error as e:
            traceback.print_exc()
            raise Exception(f"DB error occured with query: {query}")
        finally:
            self.___close___()
        
        return results


    def _writeDb(self, query : str, params : dict = None) -> None:
        """
        @brief  Function to handle db write queries
        @param  query  : sql query in string form 
        @param  params : dictionary of :keyword to parameter value
        """
        self.___connect___()
        cursor = self.__connection.cursor()

        try:
            if params: 
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.__connection.commit()
        except sqlite3.Error as e:
            traceback.print_exc()
            raise Exception(f"DB error occured with query: {query}")
        finally:
            self.___close___()

    
    def _writeDf(self, df : pd.DataFrame, table_name : str) -> None: 
        self.___connect___()
        
        try:
            df.to_sql(
                name      = table_name,  
                con       = self.__connection,          
                if_exists = "append", 
                index     = False         
            )
        except sqlite3.Error as e: 
            traceback.print_exc()
            raise Exception(f"DB error when writing df to {table_name}")
        finally:
            self.___close___()




    def exportToCsv(self):
        """
        @brief  Export a table from the SQLite DB to a CSV file. Primarily for debugging. 
        @param  table_name  : Name of the table to export
        @param  output_path : Path to save the CSV file
        """
        self.___connect___() 
        
        # Grab data for export  
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cur_table = "NO_TABLE_SELECTED_YET" 

        try:
            # Get all table names
            self.__cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in self.__cursor.fetchall()]

            for table in tables:
                query       = f"SELECT * FROM {table}"
                cur_table   = table 
                df          = pd.read_sql_query(query, self.__connection)
                output_path = os.path.join(self.base_db_path, f"{table}_{timestamp}.csv")

                # Export csv
                df.to_csv(output_path, index=False)
                print(f"[Success] Exported '{table}' to '{output_path}'")

        except Exception as err:
            print(f"[Error] Failed to export {cur_table}: {err}")
        
        self.___close___()