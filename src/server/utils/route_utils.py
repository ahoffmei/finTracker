import os 
import sys 
import re 
import pandas as pd 
from pathlib import Path 
from datetime import datetime

match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from config.env_vars import * 
from LocalFinDbManager.CreditCardDB import CreditCardDB 

def dbDaterangeQuery(data : dict) -> int | str | pd.DataFrame: 
    """
    @brief      Returns basic daterange query from a request with body : {"startdate" : "%Y-%m-%d", "enddate" : "%Y-%m-%d"}
    @params     data : dict - request body
    @returns    
                status  : int          - Expected request return status 
                message : str          - Expected request return status message 
                df      : pd.DataFrame - Data if status:200 else None. See CreditCardDB.py for Dataframe info. 
    """
    status  = True 
    message = "Status good" 
    df      = None

    # Parse query  
    start_query = data.get("startdate")
    end_query   = data.get("enddate")

    if not (status := start_query):
        message = "Invalid startdate"

    elif not (status := end_query):
        message = "Invalid enddate" 

    else: 
        cc_handle = CreditCardDB(FIN_DB_PATH)
        try:
            df     = cc_handle.getDateRangeDefinedData(datetime.strptime(start_query, "%Y-%m-%d"), datetime.strptime(end_query, "%Y-%m-%d"))
            status = True 
        except Exception as e: 
            message = f"Error when processing database: {e}"
            status  = False

    return 200 if status else 500, message, df 


def jsonifyDf(df : pd.DataFrame) -> dict:
    """
    @brief      Performs necessary reformatting before Jsonify is called on a dataframe 
    """ 
    # print(df) # debug 

    # incase I suck -- TODO: This isn't very proper 
    if not pd.api.types.is_datetime64_any_dtype(df["payment_date"]):
        df["payment_date"] = pd.to_datetime(df["payment_date"])

    df["payment_date"] = df["payment_date"].dt.strftime("%Y-%m-%d") 
    return df.to_dict(orient="records")