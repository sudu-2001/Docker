import pandas as pd
import numpy as np 

source_data = {
    'Transaction_ID': [101, 102, 103, 104],
    'Amount': [500.50, 600.00, 750.25, 1000.00],
    'Status': ['Success', 'Success', 'Pending', 'Success']
}

target_data = {
    'Transaction_ID': [101, 102, 103, 105],
    'Amount': [500.50, 600.00, 750.30, 1200.00],
    'Status': ['Success', 'Success', 'Pending', 'Success']
}

df_source=pd.DataFrame(source_data)
df_target=pd.DataFrame(target_data)

compare=pd.merge(df_source,df_target,on='Transaction_ID',how='outer',indicator=True)

missing_record=compare[compare['_merge']=='left_only']

orphan_record=compare[compare['_merge']=='right_only']

print(df_source)

print("================================================")

print(df_target)

print("================================================")

print(df_source.dtypes)

print("================================================")

print(compare)

print("================================================")

print(missing_record)

print("================================================")

print(orphan_record)

print("================================================")

print(f"missing_in_targets:{missing_record['Transaction_ID'].values}")

print("================================================")

print(f"orphan_in_targets:{orphan_record['Transaction_ID'].values}")
