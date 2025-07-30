import sys
import os
import pandas as pd

sys.path.append('/home/kimyh/library/textbasic')
from textbasic.compare.similarityanalysis import *


def main():
    df = pd.read_csv('./faultcode_whole.csv', encoding='utf-8-sig')
    # df = df[:10]
    data = df.copy()
    # data = df['설명'].tolist()
    # print(data)

    data = [
        '크루즈 컨트롤 전방 거리 센서로부터 잘못된 데이터 수신',
        '크루즈 컨트롤 전방 거리 센서로부터 잘못된 데이터 수신',
        '크루즈 컨트롤 전방 거리 센서로부터 잘못된 데이터 수신',
        'O2 센서 기준 전압 회로 로우 뱅크 1 센서 1',
        'O2 센서 기준 전압 회로 로우 뱅크 2 센서 1',
        'O2 센서 기준 전압 회로 하이 뱅크 1 센서 1',
        'O2 센서 기준 전압 회로 하이 뱅크 2 센서 1',
        'O2 센서 기준 전압 회로/개방 뱅크 1 센서 1',
        'O2 센서 기준 전압 회로/개방 뱅크 2 센서 1'
    ]


    df, sim_df = extract_sim(
        data=data,
        # column='설명',
        p=99,
        # preserve=True
    )
    print(df)
    print(sim_df)


if __name__ == '__main__':
    main()