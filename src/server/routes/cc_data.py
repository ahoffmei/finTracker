import os
import re 
import sys 
import pathlib 

from flask import Blueprint, request

# Import repo dependencies 
match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(pathlib.Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)

from src.

# Begin CreditCardData Router 

cc_bp  = Blueprint("bofaCreditCardInfo", __name__)

# **** POST CC INFO ********************************************************
# Upload bofa cc data 
@cc_bp.route("/uploadBofaCcData", methods=["POST"])
def creditCard():
    return "TODO" 


# **** GET CC INFO ********************************************************
@cc_bp.route("/test") 
def testGet(): 
    return "TODO"

@cc_bp.route("/getDaterangeBofaCcData", methods=["GET"])
def getDaterangeBasedInfo(): 
    start_query = request.args.get("startdate")
    end_query   = request.args.get("enddate")


@cc_bp.route("/getMonthlyBofaCcData", methods=["GET"])
def getMonthBasedInfo(): 
    month_query = request.args.get("month")
    year_query   = request.args.get("year")





