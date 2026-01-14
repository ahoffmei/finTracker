import os 
import pathlib 
import argparse
from config.basic_config import FIN_DB_PATH, CATEGORIZATION_DB_PATH
from datetime import datetime
from LocalFinDbManager.CreditCardDB import CreditCardDB
from CreditCardManager.BofaCreditCard import BofaCreditCard
from ReportGenerator.PlotGenerator import PlotGenerator
from ReportGenerator.HtmlReportGenerator import BuildHtmlReport
from CreditCardManager.DataCategorization.DataCategorizer import DataCategorizer, DataCategorizationDb


def setupLocalDependencies():
    if not FIN_DB_PATH.exists():
        os.makedirs(FIN_DB_PATH)
    if not CATEGORIZATION_DB_PATH.exists():
        os.makedirs(CATEGORIZATION_DB_PATH) 


def setupOpts(): 
    parser = argparse.ArgumentParser(description = "Financial Tracker Application")

    parser.add_argument("-e", "--excel-path", dest = "excel_path", type  = pathlib.Path, required=False, default=None, 
                        help = "Path to BofA excel export" )

    return parser.parse_args() 


if __name__ == "__main__":
    args = setupOpts() 
    
    setupLocalDependencies()
    cc_handle = BofaCreditCard()  
    
    # Extract credit card data
    if args.excel_path:
        cc_handle.extractCreditCardFromExcelOrCsv(args.excel_path)
        cc_rollup_df = cc_handle.getRollupPayments(cc_handle.credit_card_df)

        # Categorize Data     
        data_categorizer_handle = DataCategorizer(CATEGORIZATION_DB_PATH)
        data_categorizer_handle.categorizeFromArray(list(cc_rollup_df['Payee']))
        
    # Insert Data Into DB
    cc_df = cc_handle.getCreditCardDf()
    cc_db_handle = CreditCardDB(FIN_DB_PATH) 
    cc_db_handle.dbWriteFromDf(cc_df)

    # Build Report
    plot_gen_handle = PlotGenerator(FIN_DB_PATH) # For now use FIN_DB_PATH to store anything if we need
    fig = plot_gen_handle.createBarChartFromDf(cc_rollup_df, 'Payee', 'Amount', '')
    
    html_handle = BuildHtmlReport(None, f"Report Summary: {datetime.now()}")
    html_handle.appendFig(fig)
    html_handle.appendWidget("Total Monthly Spending", round(float(cc_rollup_df['Amount'].sum()), 2))    
    html_handle.finalizeHtml()

    

    # handle = DataCategorizer(CATEGORIZATION_DB_PATH)