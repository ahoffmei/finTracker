import os
import re 
import sys 
import pathlib 
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
    
    
    def getDateRangeDefinedData(self, start_date : datetime, end_date : datetime):
        """
        TODO
        """
        query = f"SELECT * FROM credit_card_payments WHERE payment_date BETWEEN '{start_date.strftime('%Y-%m-%d')}' and '{end_date.strftime('%Y-%m-%d')}'" 
        
        return self._readDb(query) 
        

    def getBasicReportInfoForMonth(self, month : int, year : int) -> dict:
        """
        TODO
        """
        month_df = self.getDateRangeDefinedData(
            datetime(year, month, 1), 
            datetime(year, month, calendar.monthrange(year, month)[1])
        )

        return month_df.___getBasicReportInfo___()


    def dbWriteFromDf(self, df : pd.DataFrame) -> None: 
        """
        TODO
        """
        df_copy = df.__deepcopy__()
        df_copy = df_copy[['credit_card_name', 'payment_date', 'amount_paid', 'payee']]

        self._writeDf(df_copy, 'credit_card_payments')


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