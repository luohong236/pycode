
import PySimpleGUI as sg
import sys 
import os 
import pandas as pd 

def get_Canshu():
    os.chdir(os.path.dirname(sys.modules[__name__].__file__) )

    canshu=pd.read_excel('data.xlsm',sheet_name='参数')
    canshu.dropna(inplace=True,how='all')

    canshu=canshu[['老板简称','老板微信','业务员','备注']]
    g1=canshu.groupby('老板微信')
    # canshu['个数']=g1.transform('size')
    canshu['个数']=(g1['老板微信'].transform('size'))
    return canshu
   

os.chdir(os.path.dirname(sys.modules[__name__].__file__) )

print(os.getcwdb())

if not sys.platform.startswith('win'):
    sg.popup_error('Sorry, you gotta be on Windows')
    sys.exit()
import winsound

layout = [
            [sg.Frame('操作', [[sg.Button('返回', button_color=('white', 'black'), key='reback'),
             sg.Button('读取写入', button_color=('white', 'black'), key='rw'),
             sg.Button('清空', button_color=('white', 'firebrick3'), key='clear'),           
             ]],vertical_alignment='center'
             )],
       
           [sg.Text('信息提示')],
           [sg.Output(size=(50,10),k='mt')]

          ]

window = sg.Window("Button Click", layout, icon='mo.ico', auto_size_buttons=False, use_default_focus=False, finalize=True)

# window['submit'].update(disabled=True)

recording = have_data = False
while True:
    event, values = window.read(timeout=100)    
    if event == sg.WINDOW_CLOSED:
        break
    elif event=="rw":
        df_canshu=get_Canshu()
        print(df_canshu)
    # winsound.PlaySound("ButtonClick.wav", 1) if event != sg.TIMEOUT_KEY else None
window.close()
