import pandas as pd
import numpy as np
import itertools
import os
from dateutil.parser import parse
from pandas.tseries.offsets import Day, MonthEnd

res=[]
pds=pd.DataFrame()
pd1=pd.DataFrame()
pd2=pd.DataFrame()
print(os.listdir('.'))
shoukuan=pd.read_excel(r"./data/系统支出表.xlsx",sheet_name='付款明细')
yinhanliushui=pd.read_excel(r'data/农商行流水账单.xls',sheet_name='银行流水')
# yinhanliushui.set_index('交易日期',inplace=True)
yinhanliushui=yinhanliushui[(yinhanliushui['借贷标志']=='借') & (yinhanliushui['交易日期']<=pd.to_datetime('2021-4-30'))].copy()
yinhanliushui.reset_index(drop=True,inplace=True)

shoukuan['付款日期']=pd.to_datetime(shoukuan['发送时间'].astype('str'))

shoukuan=shoukuan[shoukuan['付款日期']<=pd.to_datetime('2021-4-30')]
shoukuan=shoukuan.groupby(by=['事由','付款日期'])['交易金额'].agg([('付款金额','sum')])

shoukuan.reset_index(inplace=True)
# print(shoukuan[shoukuan['事由']=='2017年下半年退保金发放'] )
shoukuan1=shoukuan.copy()

for idx in yinhanliushui.index:
    d=yinhanliushui.loc[idx,'交易日期']
    yh=yinhanliushui.loc[idx,'交易金额']
    print(d,' ',yh)
    sub_shoukuan=shoukuan[(shoukuan['付款日期']>=d+Day(-30)) & (shoukuan['付款日期']<=d+Day(30))]
    # print(sub_shoukuan)
    find_val=False
    for i in range(1,2,1):
        iter=itertools.combinations(sub_shoukuan.index,i)
        if find_val:
            print('找到')
            break
        for it in iter:
            r=sum(shoukuan.loc[list(it),'付款金额'])            
            if abs(yh-r)<0.01 :
                res.append([idx,it])
                shoukuan.drop(list(it),inplace=True)
                find_val=True
                break
    # print(shoukuan.iloc[0:50])
    inum=1
for iyh,isk in res:
    pd1=yinhanliushui.loc[(iyh,),['交易日期','交易金额','现转标志','对方户名']].copy()
    pd1.reset_index(drop=True,inplace=True)
    pd2=shoukuan1.loc[list(isk)].copy()
    pd2.reset_index(drop=True,inplace=True)
    pd1=pd.concat([pd1,pd2],axis=1)
    pd1['核对号']=inum
    inum+=1
    pds=pd.concat([pds,pd1],ignore_index=True)
c=pds.pop('核对号')
pds.insert(0,'核对号',c) 
c=pds.pop('付款金额')
pds.insert(3,'付款金额',c)    
c=pds.pop('付款日期')
pds.insert(4,'付款日期',c)       
pds['交易日期']=pds['交易日期'].dt.date
pds['付款日期']=pds['付款日期'].dt.date

idx=[x[0] for x in res]
print(idx)
idx=[x for x in yinhanliushui.index if (x in idx)==False]
print(idx)
with pd.ExcelWriter(r'output/数据核对.xlsx') as writer:
    pds.to_excel(writer, sheet_name='已核对')
    shoukuan.to_excel(writer, sheet_name='未核对-付款')
    yinhanliushui.loc[idx].to_excel(writer, sheet_name='未核对-银行')
print(pds)
    # print(shoukuan.loc[idx+Day(-30):idx+Day(30)])

