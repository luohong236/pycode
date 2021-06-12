import pandas as pd 
import os 
import numpy as np 

dfs=pd.DataFrame()
ss=[]
exps=[]

for root_dir,sub_dir,files in os.walk(r'数据'):
    for file in files:
        if file.endswith(('.xlsx','xls')):
            file_name=os.path.join(root_dir,file)
            print(file_name )
            for sheet in pd.read_excel(file_name,sheet_name=None).keys():
               
                df=pd.read_excel(file_name,sheet_name=sheet)
                if len(df)==0:
                    continue
                df.dropna(how='all',inplace=True)
                df.dropna(how='all',inplace=True,axis=1)
                df.reset_index(drop=True,inplace=True)
                df.columns=[ str(x)+ 'c' for  x in np.arange(df.shape[1])] 
                print(file_name,' ' ,sheet)
                try:
                    i=df[df['0c'].str.find('商品编号')>=0].index.tolist()
                except:
                    exps.append(file_name + ' '+sheet)
                    continue
                    
                if len(i)>0:
                    
                    df1=df.iloc[0:i[0]].copy()
                    df1.dropna(how='all',inplace=True,axis=1)
                    s=[]
                    for index,row in df1.iterrows():
                        s=s+row.tolist()
                    ss.append(s)

                    df2=df.iloc[i[0]:].copy()
                    df2.dropna(how='all',inplace=True,axis=1)
                    df2.columns=df2.iloc[0].str.strip().tolist()
                    df2.index=np.arange(df2.shape[0])
                    df2.drop([0],inplace=True) 
                    df2['工作簿']=file_name
                    df2['工作表']=sheet
                    df2=df2[-df2['商品编号'].str.contains('收货注意事项|开箱验货|如未经检验就签收|物验收无误|注明情况或拒收|如在收货时有任|期我公司视为正|异常情况说明|公司名称|纳税人识别号|地址及电话|银行账号|运单编号|开户银行',regex=True,na=False)]
                    try:
                        df2['业务人员']=df2[df2['商品编号'].str.contains('业务人员',na=False)].iloc[0,0]
                        df2=df2[-df2['商品编号'].str.contains('业务人员',na=False)]
                    except:
                        pass
                    col=[x for x in df2.columns if isinstance(x,str)]

                    dfs=pd.concat([dfs,df2[col]],ignore_index=True ) 
df=pd.DataFrame(ss)

df.to_excel('联系人.xlsx')
dfs.to_excel('数据.xlsx')
print(exps)
