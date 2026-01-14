import os
import re 
import sys
import pathlib 
from rapidfuzz import fuzz 

# Import repo dependencies 
src_path = str(pathlib.Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from DB_Interface_Base import DB_Interface_Base
from CreditCardManager.DataCategorization.CategoryEnums import ExpenseCategories

DB_TABLES = ['''
CREATE TABLE category_map (
    category  TEXT NOT NULL,
    value     TEXT NOT NULL UNIQUE PRIMARY KEY
);
''',
'''
CREATE TABLE payee_map (
    payee  TEXT NOT NULL,
    value  TEXT NOT NULL,
    FOREIGN KEY (value) REFERENCES category_map(value) ON DELETE CASCADE 
);
''']

class DataCategorizationDb(DB_Interface_Base):
    """
    @brief      Interface class for managing data categorizations
    @param      base_db_path : Directory intending to contain database file
    """
    def __init__(self, base_db_path):
        super().__init__("dataCategorizations.db", base_db_path, DB_TABLES)
    

    def getPayeeMap(self):
        return self._readDb("SELECT payee, value FROM payee_map")
    
    
    def getCategoryMap(self):
        return self._readDb("SELECT category, value FROM category_map")


    def insertPayee(self, payee : str, value : str, category : ExpenseCategories, category_map_values : list = None): 
        # Write to category_map first to allow for FK relation
        value_list = list(self._readDb("SELECT value FROM category_map")['value']) if not category_map_values else category_map_values
        if value not in value_list:
            self._writeDb(f"INSERT INTO category_map (category, value) VALUES ('{str(category.value)}', '{str(value)}')") 
        
        # Now add category
        self._writeDb(f"INSERT INTO payee_map (payee, value) VALUES ('{payee}','{value}')") 


class DataCategorizer:
    MIN_FUZZ_RATIO = 80 

    def __init__(self, base_db_path : pathlib.Path):
        self.db_handle = DataCategorizationDb(base_db_path)


    def categorizeFromArray(self, payee_candidates : list):
        extracted_payee_map = self.db_handle.getPayeeMap()
        cur_payee_list = [] 
        # I think this bugs out but just make it a TODO 
        if not extracted_payee_map.empty:
            cur_payee_list = [x for x in extracted_payee_map]

        # use this to pass in values
        category_map_list = list(self.db_handle._readDb("SELECT value FROM category_map")['value'])
        
        # Track new payees in memory to avoid multiple reads 
        memoized_category_mappings = {}

        # Cries in O(n^2), oh wait maybe more 
        for payee in payee_candidates:
            final_payee_value = payee 

            # First check memoized dictionary for existing mappings mid-iteration 
            if payee in memoized_category_mappings:
                final_payee_value = memoized_category_mappings[payee]

            else: 
                existing_reference_exists = False   
                
                # First, check database
                for reference in cur_payee_list:
                    if fuzz.ratio(payee, reference) >= self.MIN_FUZZ_RATIO: 
                        final_payee_value         = payee
                        existing_reference_exists = True 
                        break 

                # Find references in existing category  
                if not existing_reference_exists: 
                    for reference in payee_candidates:
                        if fuzz.ratio(payee, reference) >= self.MIN_FUZZ_RATIO: 
                            # Add to dict both ways for easy search
                            memoized_category_mappings[reference] = payee 
                            memoized_category_mappings[payee]     = reference

                            # Finalize 
                            final_payee_value = payee

            # finalize push 
            self.db_handle.insertPayee(payee, final_payee_value, ExpenseCategories.PENDING, category_map_list)
            
 
    def manualCategorization(self, payee : str ): 
        """
        @brief  Super lame manual categorization || TODO 
        """
        while True: 
            category = input("Select a category")
            
        
