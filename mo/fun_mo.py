
import os
import pandas as pd
import xlwings as xl
import re 
import datetime
import sys 
from PyQt5.QtWidgets import QMessageBox

os.chdir(os.path.dirname(sys.modules[__name__].__file__) )

def get_canshu():  
    
    canshu=pd.read_excel('data.xlsx',sheet_name='参数')
    canshu.dropna(inplace=True,how='all')

    canshu=canshu[['老板简称','老板微信','业务员','月份','备注']]
    g1=canshu.groupby(canshu['老板微信'].str.lower())
    # canshu['个数']=g1.transform('size')
    canshu['个数']=(g1['老板微信'].transform('size'))
    # canshu.to_excel('test.xlsx')
    return canshu



        

