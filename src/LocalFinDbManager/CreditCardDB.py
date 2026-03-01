import os
import re 
import sys 
import pathlib 
import hashlib 
import calendar
import argparse
import pandas as pd 
from datetime import datetime 

# Import repo dependencies 
match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(pathlib.Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from DB_Interface_Base import DB_Interface_Base
from config.env_vars import * 

DB_NAME   = "finTracker.db"
DB_TABLES = ['''
CREATE TABLE credit_cards_table (
    credit_card_name    TEXT PRIMARY KEY,
    issuer              TEXT,
    card_type           TEXT
);
''',
'''
CREATE TABLE credit_card_payments (
    payment_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    hash_key            STRING NOT NULL UNIQUE, 
    credit_card_name    TEXT NOT NULL,
    payment_date        DATE NOT NULL,
    amount_paid         REAL NOT NULL,
    payee               TEXT NOT NULL,
    FOREIGN KEY (credit_card_name) REFERENCES credit_cards(credit_card_name)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
''' 
]

class CreditCardDB(DB_Interface_Base):
    def __init__(self, base_db_path : pathlib.Path):
        super().__init__(DB_NAME, base_db_path, DB_TABLES)

    
    def ___getBasicReportInfo___(self, target_df : pd.DataFrame):
        """
        TODO: maybe make public idk 
        """
        report_package = dict()
        report_package['monthly_spending'] = self.getRollupPayments(target_df)

        return report_package        


    @staticmethod
    def createSubmissionKey(name, payment_date, amount, payee):
        """
        Creates a key used for identifying payments. Used to prevent duplicate payments upon submission

        credit_card_name    TEXT NOT NULL,
        payment_date        DATE NOT NULL,
        amount_paid         REAL NOT NULL,
        payee               TEXT NOT NULL,
        """
        full_str = f"{name}|{payment_date}|{amount}|{payee}" 
        return hashlib.sha256(full_str.encode("utf-8")).hexdigest() 


    def getRequiredMappings(self):
        return [ "hash_key", "credit_card_name", "payment_date", "amount_paid", "payee" ]


    def getKeys(self):
        """
        Get all keys from the database (reduce later)
        """ 
        query = f"SELECT hash_key from credit_card_payments"

        df = self._readDb(query) 

        return df["hash_key"]

    def getDateRangeDefinedData(self, start_date : datetime, end_date : datetime):
        """
        Based on a start_date and end_date, grabs all payments from the given daterange
        """
        mdy_format = '%m-%d-%y'
        # TODO use query params 
        query = f"SELECT * FROM credit_card_payments WHERE payment_date BETWEEN '{start_date.strftime(mdy_format)}' and '{end_date.strftime(mdy_format)}'" 
        breakpoint()
        return self._readDb(query) 
        

    def getCurrentMonthCcInfo(self) -> dict:
        """
        Get report info for a given month
        """
        now   = datetime.now() 
        year  = now.year 
        month = now.month

        return self.getDateRangeDefinedData(
            datetime(year, month, 1), 
            datetime(year, month, calendar.monthrange(year, month)[1])
        )


    def dbWriteFromDf(self, df : pd.DataFrame) -> None: 
        """
        TODO
        """
        df_copy = df.__deepcopy__()
        df_copy = df_copy[['hash_key', 'credit_card_name', 'payment_date', 'amount_paid', 'payee', 'hash_key']]

        
        self._writeDf(df_copy, 'credit_card_payments')

    
    def getDbAsDf(self):
        return self._readDb("SELECT * FROM credit_card_payments") 


# Getting the vibe that this should be handled by BofaCreditCard
def cleanDbDataFromDf(df : pd.DataFrame, cc_name : str, existing_keys : list | set, column_mappings : dict): 
    df = df.__deepcopy__()

    df["credit_card_name"] = cc_name
    df["hash_key"]    = "" 
    indexes_to_drop   = []
    
    for index, row in df.iterrows():        
        key = CreditCardDB.createSubmissionKey(
            name         = cc_name, 
            payment_date = row[column_mappings["payment_date"]], 
            amount       = row[column_mappings["amount_paid"]], 
            payee        = row[column_mappings["payee"]]
        )        

        if key in existing_keys:
            indexes_to_drop.append(index)
        else:
            existing_keys.add(key)
            df.loc[index, "hash_key"] = key  

    df = df.drop(index=indexes_to_drop)
    
    return df 


def SetupOpts(): 
    parser = argparse.ArgumentParser(description = "Financial Tracker Application Database -- use for debugging")

    parser.add_argument("-e", "--export", dest = "export", action = "store_true", 
                        help = "Export database as csv" )
    
    parser.add_argument("-d", "--db-path", dest = "db_path", type = pathlib.Path, default=FIN_DB_PATH,
                        help = "Path to database directory" )

    return parser.parse_args() 


if __name__ == "__main__":
    args = SetupOpts() 

    db_handle = CreditCardDB(args.db_path)
    
    if args.export:
        db_handle.exportToCsv() 