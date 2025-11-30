import pandas as pd 

REQUIRED_COLUMNS = ["payment_date" , "payee", "amount_paid"] 

class DF_Validation:
    @staticmethod
    def validate_df(target_df : pd.DataFram): 
        missing = [col for col in REQUIRED_COLUMNS if col not in target_df.columns]
        if len(missing):
            raise ValueError(f"Dataframe is missing expected columns {missing}")
        