# -*- coding: utf-8 -*-
"""
Created on Thu May  9 13:52:52 2024

@author: cqrcb
"""
import pandas as pd
"""
note:用来制作多层透视结果
从第一层到第N层透视同时在一个表中展示
"""
def ngroupby(df,gfield,vfield,gfunction):
    data = pd.DataFrame()
    for i in range(len(gfield)):
        name = []
        aa = df.groupby(gfield[:i+1])[vfield].agg(gfunction)
        for j in aa.columns:
            temp = ''
            for k in j:
                temp=temp+k
            name.append(temp) 
        aa.columns = name #重命名列名，使用原列名+函数名作为新列名
        aa=aa.reset_index()
        data=pd.concat([data,aa])
        del aa
    data = data[gfield+name]
    data=data.sort_values(by=gfield,na_position='first').fillna('All')
    return data

 
