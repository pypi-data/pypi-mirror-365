import pandas as pd 


class ReadData:
    def __init__(self): 
        self.df = None 

    def read_csv(self, csv_path: str, **params) -> pd.DataFrame:
        self.df = pd.read_csv(csv_path, **params)
        return self.df
    
    def read_excel(self, excel_path: str, **params) -> pd.DataFrame: 
        self.df = pd.read_excel(excel_path, **params)
        return self.df