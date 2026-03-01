import os 
import pathlib 
import argparse
import pandas as pd
from dateutil.relativedelta import relativedelta
from config.env_vars import FIN_DB_PATH, CATEGORIZATION_DB_PATH
from datetime import datetime
from LocalFinDbManager.CreditCardDB import CreditCardDB, cleanDbDataFromDf
from CreditCardManager.BofaCreditCard import BofaCreditCard
from ReportGenerator.PlotGenerator import PlotGenerator
from ReportGenerator.HtmlReportGenerator import BuildHtmlReport
from CreditCardManager.DataCategorization.DataCategorizer import DataCategorizer, DataCategorizationDb


def setupLocalDependencies():
    if not FIN_DB_PATH.exists():
        os.makedirs(FIN_DB_PATH)
    if not CATEGORIZATION_DB_PATH.exists():
        os.makedirs(CATEGORIZATION_DB_PATH) 


def processCcDf(cc_handle : BofaCreditCard, db_handle : CreditCardDB):
    """
    @brief  Handle E2E processing of creditcard dataframe
    """
    cc_rollup_df = cc_handle.getRollupPayments(cc_handle.credit_card_df)

    column_mappings = cc_handle.getDfColumnMapping() 

    # Categorize Data     
    data_categorizer_handle = DataCategorizer(CATEGORIZATION_DB_PATH)
    data_categorizer_handle.categorizeFromArray(list(cc_rollup_df['Payee']))
    
    # Clean data to remove duplicates potentially  
    df = cc_handle.getCreditCardDf()
    cc_df = cleanDbDataFromDf(df, cc_handle.CC_NAME, set(db_handle.getKeys()), column_mappings)    

    # Perform some cleanup  
    reversed_mappings = cc_handle.getDfColumnMapping(True) 
    cc_df.rename(columns = reversed_mappings, inplace = True)
    cc_df = cc_df[db_handle.getRequiredMappings()]
    
    print(f"Inserting {len(cc_df)} elements")
    # finally insert  
    db_handle.dbWriteFromDf(cc_df)


def setupOpts(): 
    parser = argparse.ArgumentParser(description = "Financial Tracker Application")

    parser.add_argument("-e", "--excel-path", dest = "excel_path", type = pathlib.Path, required=False, default=None, 
                        help = "Path to BofA excel export" )

    parser.add_argument("-d", "--debug-db", dest = "debug_db", action = "store_true")
    return parser.parse_args() 


if __name__ == "__main__":
    args = setupOpts() 
    setupLocalDependencies()
    cc_handle = BofaCreditCard()  
    db_handle = CreditCardDB(FIN_DB_PATH) 

    # Extract credit card data
    if args.excel_path:
        cc_handle.extractCreditCardFromExcelOrCsv(args.excel_path)
        processCcDf(cc_handle=cc_handle, db_handle = db_handle)

    if args.debug_db:
        db = db_handle.getDbAsDf()
        breakpoint() 
        print(db)

    # Build Report
    plot_gen_handle = PlotGenerator(FIN_DB_PATH) # For now use FIN_DB_PATH to store anything if we need
    # df = db_handle.getDbAsDf()
    a, b = datetime.now() - relativedelta(months=2) , datetime.now() 
    df = db_handle.getDateRangeDefinedData(a, b)
    breakpoint()
    fig = plot_gen_handle.createBarChartFromDf(df, 'payee', 'amount_paid', '')
    
    html_handle = BuildHtmlReport(None, f"Report Summary: {datetime.now()}")
    html_handle.appendFig(fig)
    html_handle.appendWidget("Total Monthly Spending", round(float(df['amount_paid'].sum()), 2))    
    html_handle.finalizeHtml()

    # TODO - make better 
    handle = DataCategorizer(CATEGORIZATION_DB_PATH)