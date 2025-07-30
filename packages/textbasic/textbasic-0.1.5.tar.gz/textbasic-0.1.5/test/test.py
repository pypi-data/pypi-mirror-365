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
    df, sim_df = extract_sim(
        data=data,
        column='설명',
        p=60,
        # preserve=True
    )
    print(df)
    print(sim_df)


if __name__ == '__main__':
    main()