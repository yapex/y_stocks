from datetime import datetime
import akshare as ak
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import snoop
from loguru import logger


class NetValueCalculator:
    nv_df: pd.DataFrame

    def __init__(self):
        self.nv_df = pd.DataFrame(columns=['日期', '净值', '增加资产', '增加份额', '总资产'])

    def display(self):
        format_dict = {
            '日期': lambda x: "{}".format(x.strftime('%Y-%m-%d')),
            '净值': '{0:.4f}',
            '增加资产': '¥{0:,.2f}',
            '增加份额': '{0:.4f}',
            '总资产': '¥{0:,.2f}',
        }

        view = self.nv_df.style.format(format_dict).bar(
            color='lightgreen', vmin=1, subset=['净值'], align='zero'
        )
        return view

    def _get_total_shares(self) -> pd.DataFrame:
        return self.nv_df['增加份额'].sum()

    def take_snapshot(self) -> pd.DataFrame:
        return self.nv_df.copy()

    def plot(self):
        plt.rcParams["font.family"] = 'Arial Unicode MS'  # 设置字体，正常显示中文
        plt.rcParams['axes.unicode_minus'] = False  # 设置字体，正常显示中文
        plt.figure(figsize=(12, 9))

        plt.plot(
            self.nv_df['日期'],
            self.nv_df['净值'],
            label='三羊开泰',
        )

        return plt

    def record_invest(self, date_time: datetime, invest_value: float, add_cash: float = 0.0) -> None:
        row = None
        if len(self.nv_df) == 0:
            logger.debug('init ...')
            net_value = 1.0000
            add_shares = add_cash / net_value
            total = add_cash

            row = [
                [
                    pd.to_datetime(date_time),
                    net_value,
                    add_cash,
                    add_shares,
                    total,
                ]
            ]
        else:
            last_index = len(self.nv_df) - 1
            last_net_value = self.nv_df.loc[last_index, '净值']
            add_shares = add_cash / last_net_value

            new_total = invest_value + add_cash
            last_total_shares = self._get_total_shares()
            total_shares = last_total_shares + add_shares
            net_value = invest_value / total_shares

            row = [
                [
                    pd.to_datetime(date_time),
                    net_value,
                    add_cash,
                    add_shares,
                    invest_value,
                ]
            ]
        if row:
            row_df = pd.DataFrame(row, columns=self.nv_df.columns)
            self.nv_df = pd.concat([self.nv_df, row_df], ignore_index=True)
