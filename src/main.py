import pathlib 
import argparse
from config.basic_config import * 
from datetime import datetime
from FinDbManager.CreditCardDB import CreditCardDB
from CreditCardManager.BofaCreditCard import BofaCreditCard
from ReportGenerator.PlotGenerator import PlotGenerator
from ReportGenerator.HtmlReportGenerator import BuildHtmlReport
from CreditCardManager.DataCategorization.DataCategorizer import DataCategorizer, DataCategorizationDb

def SetupOpts(): 
    parser = argparse.ArgumentParser(description = "Financial Tracker Application")

    parser.add_argument("-e", "--excel-path", dest = "excel_path", type  = pathlib.Path, required=True,  
                        help = "Path to BofA excel export" )

    return parser.parse_args() 


if __name__ == "__main__":
    args = SetupOpts() 
    
    # Extract credit card data
    cc_handle = BofaCreditCard(args.excel_path)  
    cc_handle.extractCreditCardFromExcelOrCsv(args.excel_path)
    cc_rollup_df = cc_handle.getRollupPayments(cc_handle.credit_card_df)

    # Categorize Data     
    data_categorizer_handle = DataCategorizer(CATEGORIZATION_DB_PATH)
    data_categorizer_handle.categorizeFromArray(list(cc_rollup_df['Payee']))
    # TODO - eventually feed categorizations into spendings report somehow  
    
    # basic_report_info = cc_handle.getBasicReportInfoForMonth(datetime.now().month, datetime.now().month) 
    
    # Insert Data Into DB
    cc_df = cc_handle.getCreditCardDf()
    cc_db_handle = CreditCardDB(FIN_DB_PATH) 
    cc_db_handle.dbWriteFromDf(cc_df)


    breakpoint() 

    # Build Report
    plot_gen_handle = PlotGenerator(FIN_DB_PATH) # For now use FIN_DB_PATH to store anything if we need
    fig = plot_gen_handle.createBarChartFromDf(cc_rollup_df, 'Payee', 'Amount', '')
    
    html_handle = BuildHtmlReport(None, f"Report Summary: {datetime.now()}")
    html_handle.appendFig(fig)
    html_handle.appendWidget("Total Monthly Spending", round(float(cc_rollup_df['Amount'].sum()), 2))    
    html_handle.finalizeHtml()

    

    # handle = DataCategorizer(CATEGORIZATION_DB_PATH)