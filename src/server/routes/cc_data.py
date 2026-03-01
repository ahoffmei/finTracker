import os
import re 
import sys 
import pathlib 
import pandas as pd 

from io import BytesIO
from flask import Blueprint, request, jsonify

# Import repo dependencies 
match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(pathlib.Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from main import processCcDf, setupLocalDependencies
from CreditCardManager.BofaCreditCard import BofaCreditCard
from LocalFinDbManager.CreditCardDB import CreditCardDB, cleanDbDataFromDf
from config.env_vars import * 

# Begin CreditCardData Router 
cc_bp  = Blueprint("bofaCreditCardInfo", __name__)

# **** POST CC INFO ********************************************************
# Upload bofa cc data 
@cc_bp.route("/uploadBofaCcDataCsv", methods=["POST"])
def uploadBofaCcDataCsv():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]

    # Validate extension
    if not file.filename.endswith((".csv")):
        return {"error": "Invalid file type"}, 400

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file)

    # Being processing function, TODO: actually just package this all in a function --> also eventually make not sqlite
    try:
        setupLocalDependencies() 
        cc_handle = BofaCreditCard()
        db_handle = CreditCardDB(FIN_DB_PATH)
        cc_handle.setCreditCardDF(df)
        processCcDf(cc_handle=cc_handle, db_handle=db_handle)

    except Exception as E: 
        return jsonify({
            "status" : "error", 
            "message" : str(E)
        }), 500 

    # Write to db
    return jsonify({
        "status"  : "success",
        "message" : "file imported succesfully"
        }), 200 


# **** GET CC INFO ********************************************************
@cc_bp.route("/test") 
def testGet(): 
    return {"status" : 200}

@cc_bp.route("/getDaterangeBofaCcData", methods=["GET"])
def getDaterangeBasedInfo(): 
    start_query = request.args.get("startdate")
    end_query   = request.args.get("enddate")
    # TODO 


@cc_bp.route("/getMonthlyBofaCcData", methods=["GET"])
def getMonthBasedInfo(): 
    month_query = request.args.get("month")
    year_query   = request.args.get("year")
    # TODO 




