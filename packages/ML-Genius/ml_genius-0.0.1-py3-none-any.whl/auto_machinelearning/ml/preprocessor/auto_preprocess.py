import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


class AutoPreprocessor:
    def __init__(self, df: pd.DataFrame, target_column: str=None):
        self.df = df
        self.target_column = target_column
        self.encoder = LabelEncoder()
        self.scaler = StandardScaler()


    # def column_removal(self, df: pd.DataFrame) -> pd.DataFrame: 
    #     remove_col_list = []
    #     df_copy = df.copy()
    #     nan_val = df.isna().sum()

    #     for key, value in dict(nan_val).items():
    #         percentage = value/df_copy.shape[0] * 100
    #         if percentage > 30: 
    #             remove_col_list.append(key)

    #     updated_df = df_copy.drop(columns = remove_col_list)

    #     return updated_df
    
    def convert_cat_to_num(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy() 
        categorical_columns = df_copy.select_dtypes(include=['object', 'category']).columns.tolist()

        for col in df.columns: 
            if col in categorical_columns: 
                df_copy[col] = self.encoder.fit_transform(df_copy[col].astype(str))
        
        return df_copy
    
    def scale_dataframe(self, df: pd.DataFrame) -> pd.DataFrame: 
        df_copy = df.copy()
        scale_cols = [col for col in df_copy.columns if col != self.target_column]
        if scale_cols:
            df_copy[scale_cols] = self.scaler.fit_transform(df_copy[scale_cols])

        return df_copy
    
    def transform_new_data(self, new_df: pd.DataFrame) -> pd.DataFrame:
        df_copy = new_df.copy()

        # Use already-fitted encoder and scaler
        df_copy = self.convert_cat_to_num(df_copy)
        df_copy = self.scale_dataframe(df_copy)

        return df_copy
    
    def run_preprocessing(self): 
        # updated_df = self.column_removal(self.df)
        encoded_df = self.convert_cat_to_num(self.df)
        scaled_df = self.scale_dataframe(encoded_df)

        return scaled_df, self.encoder, self.scaler

