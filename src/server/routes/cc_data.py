import os
import re 
import sys 
import pandas as pd 
from pathlib import Path 
from datetime import datetime

from io import BytesIO
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin, CORS

# Import repo dependencies 
match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from config.env_vars import * 
from server.utils import route_utils
from main import processCcDf, setupLocalDependencies
from CreditCardManager.BofaCreditCard import BofaCreditCard
from LocalFinDbManager.CreditCardDB import CreditCardDB 
from DataAnalysis.SpendingAnalysisLayer import SpendingAnalysisManager

# Begin CreditCardData Router 
cc_bp = Blueprint("bofaCreditCardInfo", __name__)
CORS(cc_bp, origins = ["http://localhost:5173"])

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

    return jsonify({
        "status"  : "success",
        "message" : "file imported succesfully"
        }), 200 


# **** GET CC INFO ********************************************************
@cc_bp.route("/test") 
def testGet(): 
    return {"status" : 200}


@cc_bp.route("/getDaterangeBofaCcData", methods=["POST"])
def getDaterangeBasedInfo(): 
    data = request.get_json() 

    status, message, df = route_utils.dbDaterangeQuery(data=data)

    if status != 200: 
        return jsonify({
            "status"  : status,
            "message" : message
        }, status)    

    print(df.columns)
    return jsonify({
        "status" : 200,
        "body"   : route_utils.jsonifyDf(df)
    })


@cc_bp.route("/getMonthlyRollup", methods=["POST"])
def getMonthBasedInfo(): 
    data = request.get_json() 

    status, message, df = route_utils.dbDaterangeQuery(data=data)

    if status != 200: 
        return jsonify({
            "status"  : status,
            "message" : message
        }, status)    

    spending_analysis = SpendingAnalysisManager(df)
    monthly_df = spending_analysis.getMonthlySummary()

    return jsonify({
        "status" : 200,
        "body"   : route_utils.jsonifyDf(monthly_df)
    })