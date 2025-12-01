import os
import re 
import sys 
import pathlib 
import pandas as pd 

from io import BytesIO
from flask import Blueprint, request

# Import repo dependencies 
match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(pathlib.Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from CreditCardManager.BofaCreditCard import BofaCreditCard

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

    # Call your processing function
    bofa_cc_handle = BofaCreditCard()
    bofa_cc_handle.setCreditCardDF(df) 

    # Write to db
    return {"status": "success"}




# **** GET CC INFO ********************************************************
@cc_bp.route("/test") 
def testGet(): 
    return "TODO"

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




