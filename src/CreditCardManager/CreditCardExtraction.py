import os 
import pathlib 
import pandas as pd 
from io import BytesIO
from typing import Union
from abc import ABC, abstractmethod


class CreditCardExtractorBase(ABC): 
    def __init__(self, issuer : str):
        self.issuer         = issuer 
        self.credit_card_df = None 


    @abstractmethod
    def ___payemntDataProcessing___(self) -> None:
        '''
        @brief  Apply post extraction processing to self.credit_card_df
        '''
        pass  


    @abstractmethod
    def getDfColumnMapping(self) -> dict:
        '''
        @brief  Get a dictionary mapping of which dataframe columns map to which value in the database
        '''
        pass  


    def getCreditCardDF(self) -> pd.DataFrame: 
        return self.credit_card_df


    def setCreditCardDF(self, cc_df) -> None:
        self.credit_card_df = cc_df


    def extractCreditCardFromExcelOrCsv(self, table_path : pathlib.Path) -> None:
        ''' 
        @brief      Conert excel or csv to df
        @param      table_path: path to *.xlsx or *.csv file 
        ''' 
        # Extract csv or xlsx data 
        if os.path.exists(table_path):
            if table_path.suffix.lower() == ".csv": 
                self.credit_card_df = pd.read_csv(table_path)
            elif table_path.suffix.lower() == ".xlsx": 
                self.credit_card_df = pd.read_excel(table_path)
            else:
                raise ValueError(f"Unsupported file: {table_path}. Must be csv of xlsx.")
        else:
            raise FileExistsError(f"Excel path {table_path} DNE")
        # Apply post processing 
        self.___payemntDataProcessing___() 
    
