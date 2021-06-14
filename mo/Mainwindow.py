from PyQt5.QtWidgets import QApplication, QLabel, QTextEdit,QWidget,QMainWindow,QPushButton,QHBoxLayout,QGridLayout,QDialog,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot
import sys 
import os 
from fun_mo import *
import pandas as pd
import xlwings as xl
import re 
import datetime


os.chdir(os.path.dirname(sys.modules[__name__].__file__))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # self.bthBack=QPushButton("返回")
        self.btReadWrite =QPushButton("读取写入",self)
        self.btReadWrite.clicked.connect(self.read_write)    
        
        self.btClear=QPushButton("清空")
        self.btClear.clicked.connect(self.clear_data)
        self.lb=QLabel('信息提示：')
        self.msg=QTextEdit()        
        layout=QGridLayout()
        mainFrame=QWidget()
        # layout.addWidget(self.bthBack,0,0)
        layout.addWidget(self.btReadWrite,0,0)
        layout.addWidget(self.btClear,0,1)
        layout.addWidget(self.lb,1,0)
        layout.addWidget(self.msg,2,0,1,2)
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)     
    def show_msg(self,msg):
        QMessageBox.information(self,'错误',msg,QMessageBox.Ok)
    def clear_data(self):

        wb=xl.Book('data.xlsm')
        worksheet=wb.sheets['明细']  
        ra=worksheet.range(f'i1:i{worksheet.used_range.last_cell.row}').options(pd.DataFrame,index=0)
        ra.api.EntireColumn.ClearContents()
        ra.api.EntireColumn.Interior.Color=16777215
        ra.api.EntireColumn.Interior.Pattern=-4142

    def read_write(self):
        wb=xl.Book('data.xlsx')
        wb.save()
        canshu =get_canshu()
        df_dul=canshu[canshu['个数']>1]
        self.msg.setText('')
        if len(df_dul)>0:
            self.msg.setText(str(df_dul))
            self.show_msg('有重复的微信号！')
        else:         
            self.canshu=canshu   
            self.get_data(wb)
 
    def get_data(self,wb):
        # wb=xl.Book('data.xlsx')
        # wb.save()
        worksheet=wb.sheets['明细']
        #删除I列的空值     
        ra=worksheet.range(f'i1:i{worksheet.used_range.last_cell.row}').options(pd.DataFrame,index=0)
        self.ra=ra
        worksheet.range(f'A2:F{worksheet.used_range.last_cell.row}').options(pd.DataFrame,index=0).clear_contents()
        ra.api.EntireColumn.Interior.Color=16777215
        ra.api.EntireColumn.Interior.Pattern=-4142
        df=pd.DataFrame(ra.value)
        df.columns=['data']
        df.dropna(inplace=True)
        df.dropna(inplace=True,axis=1)
        worksheet.range('I:I').clear_contents()
        worksheet.range('i2').options(index=0).value=df.values	
        # worksheet.range('A:F').expand('table').offset(1,0).clear_contents()
        boss_wechat_list=self.canshu['老板微信'].str.lower().values
        s=[]
        s_boss=[]
        s_wechat=[]
        
        for index in range(0,df.shape[0],4):
            date=datetime.date.today()
            person=df.iloc[index,0]
            jiedanNum=re.search(r'\d+',df.iloc[index+3,0],re.M|re.I)
            boss_wechat=re.search(r'[a-zA-Z\d_-]+',df.iloc[index+2,0],re.M|re.I)
            if boss_wechat==None:
                boss_wechat='' 
            else:
                boss_wechat=boss_wechat.group()
                # person1=self.canshu.loc[self.canshu['老板微信'].str.contains(boss_wechat,case=False,regex=False,na=False),'业务员']
                person1=self.canshu.loc[boss_wechat_list ==boss_wechat.lower(),'业务员']
                boss_name=self.canshu.loc[boss_wechat_list ==boss_wechat.lower(),'老板简称']
                month=self.canshu.loc[boss_wechat_list ==boss_wechat.lower(),'月份']
                if len(person1)>0 :            
                    person1=person1.tolist()[0]
                    boss_name=boss_name.tolist()[0]
                    month=month.tolist()[0]
                else:
                    person1='' #必须对person1赋值，否则输出到excel会卡死，因为此时person1为一个空的dataframe,xlwings无法转换成功，而且也无法进行真假判断
                    boss_name=''
                    month=''
                    ra(index+1+3).color=(255,0,0)
                    s_wechat.append(boss_wechat)
            if jiedanNum==None:
                jiedanNum=0
            else:
                jiedanNum=int(jiedanNum.group())
            s.append([date,person,jiedanNum,0,jiedanNum*3,0])
            s.append([date,person1,0,jiedanNum,0,jiedanNum*2])
            s_boss.append([date,boss_name,boss_wechat,jiedanNum,person1,month])
        columns=['DATE','业务人员','接单量','老板点单','接单金额','点单量金额']
        dfContent=pd.DataFrame(s,columns=columns)
        columns=['DATE','老板简称','老板微信号','点单量','业务员','月份']
        df_boss=pd.DataFrame(s_boss,columns=columns)
        worksheet.range('A2').expand('table').options(index=0,header=0).value=dfContent
        wb.sheets['老板'].range('A:F').clear_contents()        
        ra=wb.sheets['老板'].range('A1').options(index=0)  
        ra.value=df_boss
        ra=wb.sheets['老板'].used_range
        ra.columns[1].last_cell.offset(1,0).value='汇总'
        ra.columns[3].last_cell.offset(1,0).value=df_boss['点单量'].sum()
        wb.sheets['汇总'].range('A:F').clear_contents()
        # df_agg=dfContent.groupby(['DATE','业务人员']).sum()
        df_agg=dfContent.pivot_table(index=['DATE','业务人员'],aggfunc='sum',margins=True,margins_name='汇总')
        df_agg.reset_index(inplace=True)
        wb.sheets['汇总'].range("A1").options(index=0).value=df_agg

        if len(s_wechat)>0:
            self.msg.setText(str(s_wechat))
            self.show_msg('有微信没有找到！')

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon('mo.jpg'))
    win =MainWindow()
    win.resize(400,400)
    win.setWindowTitle('单量汇总')
    win.show()
    sys.exit(app.exec_())
    

