# Importing Libraries
import pandas as pd
import numpy as np

# Create a Class
class FeatureEngineering:

    def __init__(self):
        pass
    
    # OneHot Encoder Function
    def  OneHot_En(self,df):
        ohe_df = pd.DataFrame()
        for i in df.columns:
            temp_df = pd.DataFrame(columns=df[i].unique()) # Create Datafroma using columns
            for j in temp_df.columns:
                temp_df[j] = df[i] 
                temp_df[j] = temp_df[j].apply(lambda x : 1 if x == j else 0) # Assign values
            ohe_df = pd.concat([ohe_df,temp_df],axis=1)
        return(ohe_df) 
    
    # Lable Encoder Fuction
    def Lable_En(self,df):
        for i in df.columns:
            df[i] = df[i].map(
                dict(
                    zip(pd.DataFrame(df[i].unique(),columns=['uni']).uni,pd.DataFrame(df[i].unique(),columns=['uni']).index) # Assign values to unique values
                    )
                )
        return df
    
    # Order Encoder Function
    def Order_En(self,o_list,df):
        o_list_dict={}
        for o in o_list:
            o_list_dict = o_list_dict | dict(zip(pd.DataFrame(o,columns=['ord']).ord,pd.DataFrame(o,columns=['ord']).index)) # Create Order List

        for i in df.columns:
            df[i] = df[i].map(    # Assign values by order list
                o_list_dict
                )
        return df
    
    # Target Encoder Function
    def Target_En(self,df,Target_column_df):
        temp_df = pd.DataFrame()
        for i in df.columns:
            cal_df = pd.concat([df[i],Target_column_df[Target_column_df.columns[0]]],axis=1).groupby(i)[Target_column_df.columns[0]].mean().sort_values(ascending=False).reset_index() # Create Dataframe for target encoder using target value
            cal_df.columns = [i,Target_column_df.columns[0]]
            df[i] = df[i].map(dict(zip(cal_df[cal_df.columns[0]],cal_df.index))) # Assign the values 
            temp_df = pd.concat([temp_df,df[i]],axis=1)
        return temp_df
    
    # Freq Encoder Function
    def Freq_En(self,df):
        for i in df.columns:
            df[i] = df[i].map(
                dict(
                    zip(pd.DataFrame(df[i].value_counts()).reset_index()[i],pd.DataFrame(df[i].value_counts()).reset_index().index)   # using value count find the frequency and assign the values
                    )
                )
        return df
    
    # Bin Encoder Function
    def Bin_En(self,df):
        # Binary Tranformation Function
        def bin_num(num):
            b = []
            if num != 0:
                while num >0:
                    b.append(str(num%2))
                    num = num//2
                return "".join(b[::-1])
            else:
                b.append(str(0))
                return "".join(b[::-1])

        for i in df.columns:
            df[i] = df[i].map(
                dict(
                    zip(pd.DataFrame(df[i].unique(),columns=['col']).col,[bin_num(i) for i in pd.DataFrame(df[i].unique(),columns=['col']).index]
                    )
                )) # Assign binary values
        return df
    
    # Standard Scaler Function
    def Stannd_Scale(self,df):
        # Standard Scaler Formula
        def stand_formula(x,std,mean):
            return round(((x-mean)/std),2)
        
        temp_df = pd.DataFrame()

        for i in df.columns:
            std = np.std(df[i].values)
            mean = np.mean(df[i].values)
            temp_df = pd.concat([temp_df,pd.DataFrame([stand_formula(j,std,mean) for j in df[i].values],columns=[i])],axis=1) # Assign the values
        return temp_df
    
    # Normal Scaler Function
    def Normm_Scale(self,df):
        # Normal Scaler Formula
        def norm_formula(x,i_min,i_max):
            return round((x-i_min)/(i_max-i_min),2)
        
        temp_df = pd.DataFrame()

        for i in df.columns:
            i_min = min(df[i].values)
            i_max = max(df[i].values)
            temp_df = pd.concat([temp_df,pd.DataFrame([norm_formula(j,i_min,i_max) for j in df[i].values],columns=[i])],axis=1) # Assign the values
        return temp_df