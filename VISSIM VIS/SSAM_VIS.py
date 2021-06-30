import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.image import imread
import matplotlib.pyplot as plt
from skimage import color
from skimage.transform import resize
import warnings
warnings.filterwarnings('ignore')
mat_img = imread("178793709117309719309.jpg")

def traffic_quantity():
    inputs = input("file sequence : ")
    sk = [i+1 for i in range(11)]
    VIS = pd.read_csv(f"/Users/user/Desktop/LeftTurn/left turn real_{inputs}.mer",sep=';' ,skiprows = sk)

    VIS.columns = [i.strip() for i in VIS.columns]
    VIS = VIS[VIS['t(Entry)']>0]
    VIS_group = VIS.groupby('Measurem.').sum()
    VIS_south = VIS_group['Pers'].iloc[0]+VIS_group['Pers'].iloc[1]
    VIS_left = VIS_group['Pers'].iloc[2]
    print(f'file : {inputs}')
    print(VIS_group)
    print('북쪽>남쪽교통량 : ',VIS_south)
    print('좌회전교통량 : ',VIS_left)

def collision_visualization():
    inputs = input("파일 경로 : ")
    df_trj = pd.read_csv(f"{inputs}")
    x1, y1 = [-5.5, -5.5], [-275.5,-290.5]
    x2, y2 = [9.5, 9.5], [-275.5,-290.5]
    x3, y3 = [-5.5, 9.5], [-275.5,-275.5]
    x4, y4 = [-5.5, 9.5], [-290.5,-290.5]
    df_10004 = df_trj[(((df_trj['FirstLink']==10004) & ((df_trj['SecondLink']==10001)|(df_trj['SecondLink']==1)|(df_trj['SecondLink']==10004))) 
                      | ((df_trj['SecondLink']==10004) & ((df_trj['FirstLink']==10001)|(df_trj['FirstLink']==1)|(df_trj['FirstLink']==10004))))]
    df_10004['counter'] = 1
    plt.figure(figsize=(10,10))
    plt.xlim(-20,20)
    plt.ylim(-300,-260)
    plt.xlim(0,310)
    plt.ylim(0,310)
    plt.title(f"collision : {df_10004['counter'].sum()}")
    plt.imshow(color.rgb2gray(resize(mat_img,(310,390,4))),alpha=0.6,cmap='gray')
    plt.plot((np.array(x1)+19.5)*10,(np.array(y1)+300.5)*10,c='r')
    plt.plot((np.array(x2)+19.5)*10,(np.array(y2)+300.5)*10,c='r')
    plt.plot((np.array(x3)+19.5)*10,(np.array(y3)+300.5)*10,c='r')
    plt.plot((np.array(x4)+19.5)*10,(np.array(y4)+300.5)*10,c='r')
    plt.axis('off')
    sns.scatterplot((df_10004['xMinPET']+20)*10,	(df_10004['yMinPET']+300)*10,alpha=0.2,s=300,color='b')
    # sns.scatterplot((df_10004['xSecondCEP']+20)*10,	(df_10004['ySecondCEP']+300)*10,alpha=0.2,s=300,color='b')
    plt.show()
if __name__=='__main__':
    while True:
        print('-'*100)
        asking = input('1 : 교통량조사(mer)\n2 : 상충지점 밀도 시각화(trj)\n3: 종료(아무키나 누르세요)\n입력 : ')
        if asking=='1':
            while True:
                try:
                    traffic_quantity()
                except:
                    print('다시입력해주세요')
                print('-'*100)
        elif asking=='2':
            while True:
                try:
                    collision_visualization()
                except:
                    print('다시입력해주세요')
                print('-'*100)
        else :
            print("종료")
            break
    