import os
import re 
import sys
import pathlib
import pandas as pd 

match = re.search(r".*fintracker\\src", os.path.abspath(__file__))
if match:
    src_path = str(pathlib.Path(match.group()))
    if src_path not in sys.path:
        sys.path.append(src_path)
    
from src.DF_Enforcement import * 


class SpendingAnalysisManager: 
    def __init__(self, spending_df) -> None:
        """
        @brief  Handles all analysis type methods for a given dataframe
        """
        DF_Validation.validate_df(spending_df)
        self.spending_df = spending_df
        self.rent        = None 
        self.utils       = None 

    # ***********************************************************************************
    # *** Private methods ***************************************************************
    # ***********************************************************************************
    # TODO 

    # ***********************************************************************************
    # *** Public methods ****************************************************************
    # ***********************************************************************************

    # *** Setters    
    def setRent(self, rent : float) -> None:
        self.rent = rent 


    def setUtils(self, utils : float) -> None:
        self.utils = utils  

    
    def setTargetDf(self, spending_df : pd.DataFrame):
        # Validate input df 
        DF_Validation.validate_df(spending_df)
        self.spending_df = spending_df


    # *** Get Report Info 
    def getTotalSpending(self): 
        """
        @brief  Returns total amount spent across the entire dataframe
        """
        total_spending = 0 
        
        if self.rent: 
            total_spending += self.rent
        
        if self.utils: 
            total_spending += self.utils
        
        if self.spending_df: 
            total_spending +=  self.spending_df['amount_paid'].sum()
            
        return total_spending

    
    def getHighestExpense(self): 
        """
        @brief  Returns the row of the highest expense in a given month
        """
        return self.spending_df.loc[[self.spending_df["sales"].idxmax()]]


    def getAverageMonthlySpending(self):
        """
        @brief  Return the average monthly spending
        """
        # Ensure 'date' is datetime
        self.spending_df["date"] = pd.to_datetime(self.spending_df["date"])

        # Get monthly avg 
        monthly_sum = self.spending_df.groupby(self.spending_df["date"].dt.to_period("M"))["amount_paid"].sum()
        return monthly_sum.mean()


    def getAverageDailySpending(self):
        """
        @brief  Return the average daily spending
        """
        # Ensure 'date' is datetime
        self.spending_df["date"] = pd.to_datetime(self.spending_df["date"])

        # Get daily avg 
        monthly_sum = self.spending_df.groupby(self.spending_df["date"].dt.to_period("D"))["amount_paid"].sum()
        return monthly_sum.mean()
        
    
    def getMostFrequentPurchase(self):
        """
        @brief      Returns the most frequent occurance of a payee 
        @return     - The name of the payee 
                    - The number of occurences 
        """ 
        highest_frequency_payee = self.spending_df["amount_paid"].value_counts().idxmax()
        frequency_count         = (self.spending_df["expense_type"] == highest_frequency_payee).sum()

        return highest_frequency_payee, frequency_count


    def getX_LargestExpenses(self, x : int):
        """
        @brief      Return the X largest expenses
        """
        return self.spending_df.nlargest(x, "amount_paid")
    

    


    


    




    


    