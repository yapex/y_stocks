import abc
import logging

import matplotlib.pyplot as plt
import pandas as pd

import ystocks.utility as yu
from ystocks.settings import *
from ystocks.settings import V_FOC_SCORE, V_10Y_MEDIAN
from ystocks.utility import get_logger

log = get_logger()


class AverageLikeAnalyzer:
    """
    均值分析类型
    """
    _merged_df: pd.DataFrame
    _analyzed_df: pd.DataFrame
    _voted: pd.Series
    _stock_code: str
    _analyzing_columns: []
    _is_analyzed = False

    def __init__(self, stock_code):
        analyzing_columns = self._get_analyzing_columns()
        assert len(analyzing_columns), 'analyzing_columns should not empty'
        self._stock_code = stock_code
        self._analyzing_columns = analyzing_columns
        self._column_for_vote, self._v_score = self._get_voting_columns()
        self._merged_df = yu.get_merged_table_by(stock_code)
        assert not self._merged_df.empty, f'Can not get data from: {stock_code}'

    def _preprocess(self) -> pd.DataFrame:
        df = self._merged_df[self._analyzing_columns].copy()
        # df.loc[:, C_TOTAL_ASSETS] = self._merged_df[C_TOTAL_ASSETS]
        # df.loc[:, C_TOTAL_DEBTS] = self._merged_df[C_TOTAL_DEBTS]
        df.loc[:, C_STOCK_S_NAME] = self._merged_df[C_STOCK_S_NAME]
        df.loc[:, STOCK_CODE] = self._stock_code
        df.loc[:, REPORT_DATE_NAME] = self._merged_df[REPORT_DATE_NAME]
        df = df.fillna(0)
        return df

    def _create_empty_series(self) -> pd.Series:
        stock_name = self._analyzed_df.loc[0, C_STOCK_S_NAME]
        _data = {C_STOCK_S_NAME: stock_name}
        return pd.Series(data=_data, name=self._stock_code)

    @abc.abstractmethod
    def _do_analyzing(self,
                      df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_voting_columns(self) -> []:
        raise NotImplementedError('返回列类型和投票显示列')

    @abc.abstractmethod
    def _get_analyzing_columns(self) -> []:
        raise NotImplementedError

    def _postprocessing(self, a_df: pd.DataFrame):
        self._analyzed_df = a_df
        assert not self._analyzed_df.empty, '没有正确完成数据分析'

        self._is_analyzed = True
        return self._analyzed_df.copy()

    def analyzing(self) -> pd.DataFrame:
        p_df = self._preprocess()
        a_df = self._do_analyzing(p_df)
        return self._postprocessing(a_df)

    def _vote_median(self, voted, median, v_score) -> pd.Series:
        wonderful, excellent = V_Median_Standard[self._column_for_vote]
        if median >= wonderful:
            voted[v_score] += 2
        elif median >= excellent:
            voted[v_score] += 1
        voted[V_10Y_MEDIAN] = format(median, '0.2%')
        return voted

    def _vote_any_row_lt_expected(self, df, v_type, v_score, expected):
        voted = self._voted
        # 检查是否有某年的小于期望，没有则加0.5分
        any_row_lt_15 = (df[v_type] < expected)
        if any_row_lt_15.mean() == 0:
            log.debug(
                f'{voted[C_STOCK_S_NAME]}({v_type}): 没有小于15%的数据，非常棒！')
            voted[v_score] += 0.5
            voted[V_ANY_ROW_NOT_LT_EXPECTED] = True
        else:
            voted[V_ANY_ROW_NOT_LT_EXPECTED] = False
            log.debug(f'{voted[C_STOCK_S_NAME]}({v_type}): 找到小于15%的数据')

        return voted

    # 用 1-std 作为分数
    def _vote_std(self, _std, v_score):
        voted = self._voted
        voted[v_score] += (1 - _std)
        voted[v_score] = round(voted[v_score], 2)
        voted[V_10Y_STD] = round(_std, 2)
        return voted

    def voting(self):
        _type = self._column_for_vote
        v_score = self._v_score
        voted = self._prepare_vote()

        df = self._analyzed_df

        median = df[_type].median(axis=0)
        self._voted = self._vote_median(voted, median, v_score)  # 必须写第一行

        # self._voted = self._vote_any_row_lt_expected(df, _type, v_score)

        std = df[_type].std()
        self._voted = self._vote_std(std, v_score)
        self._custom_voting()
        return self._voted.copy()

    def _prepare_vote(self):
        if not self._is_analyzed:
            self.analyzing()
        df = self._analyzed_df

        self._voted = self._create_empty_series()
        self._voted[self._v_score] = 0.0
        return self._voted

    @abc.abstractmethod
    def _custom_voting(self):
        raise NotImplementedError


class RoeAnalyzer(AverageLikeAnalyzer):
    """
    sum(净利润)/sum(净资产)
    衡量每投入一元钱能创造多少价值
    """

    def _custom_voting(self):
        self._voted[C_ROE] = format(self._roe_by_sum, '.2%')

    def _get_analyzing_columns(self):
        return [C_NET_PROFIT, C_EQUITY]

    def _get_voting_columns(self):
        return [C_ROE, V_ROE_SCORE]

    def _do_analyzing(self, df: pd.DataFrame) -> pd.DataFrame:
        a_df = df
        a_df[C_ROE] = df[C_NET_PROFIT] / df[C_EQUITY]  # 计算ROE
        log.debug(
            f'{self._stock_code} ROE of {df[REPORT_DATE_NAME]}: {a_df[C_ROE]}')
        # a_df[C_DEBTS_DIV_ASSETS] = df[C_TOTAL_DEBTS] / df[C_TOTAL_ASSETS]
        self._roe_by_sum = df[C_NET_PROFIT].sum() / df[C_EQUITY].sum()
        log.debug(a_df)
        return a_df

    def plt_show(self):
        if self._is_analyzed:
            plt.rcParams["font.family"] = 'Arial Unicode MS'  # 设置字体，正常显示中文
            df = self._analyzed_df.copy()
            df[C_ROE] = self._analyzed_df[C_ROE] * 100
            report_date = pd.to_datetime(self._analyzed_df[REPORT_DATE_NAME],
                                         format='%Y%m%d')
            df[REPORT_DATE_NAME] = report_date.dt.year
            df.sort_index(ascending=True, inplace=True)
            # 设置数据
            df.plot(x=REPORT_DATE_NAME, y=C_ROE, kind="bar",
                    figsize=(23, 8),
                    title=f'{C_STOCK_S_NAME} - {C_ROE}%')

            plt.grid(True, linestyle=':', color='r', alpha=0.3)
            plt.ylabel(C_ROE + '%')
            plt.xlabel(REPORT_DATE_NAME)
            plt.show()


class FocAnalyzer(AverageLikeAnalyzer):
    """
    (sum(经营性现金流) - sum(资本性支出))/sum(净资产)
    衡量自由现金流的创造能力
    """

    def _custom_voting(self):
        self._voted[C_FOC] = format(self._foc_by_sum, '.2%')

    def _get_analyzing_columns(self):
        return [C_OPER_NET_CASH, C_CAPITAL_COST, C_EQUITY]

    def _get_voting_columns(self):
        return [C_FOC, V_FOC_SCORE]

    def _do_analyzing(self, df: pd.DataFrame) -> pd.DataFrame:
        a_df = df

        a_df[C_FREE_CASH] = df[C_OPER_NET_CASH] - df[C_CAPITAL_COST]
        a_df[C_FOC] = a_df[C_FREE_CASH] / df[C_EQUITY]
        log.debug(
            f'{self._stock_code} FOC of {df[REPORT_DATE_NAME]}: {a_df[C_FOC]}')

        # 计算总和后的FOC
        oper_net_cash_sum = df[C_OPER_NET_CASH].sum()
        captial_cost_sum = df[C_CAPITAL_COST].sum()
        equity_sum = df[C_EQUITY].sum()
        self._foc_by_sum = (oper_net_cash_sum - captial_cost_sum) / equity_sum
        log.debug(a_df)
        return a_df


class OpmAnalyzer(AverageLikeAnalyzer):
    """
    主营业务毛利率分析: C_OPER_PROFIT_MARGIN
    """

    def _custom_voting(self):
        self._voted[V_OPM] = format(self._opm_by_sum, '0.2%')
        a_df = self._analyzed_df
        selected = a_df[C_OPERATING_PROFIT]
        cagr10 = pow(selected.iloc[0] / selected.iloc[-1], 1 / 10) - 1
        self._voted[V_CAGR] = format(cagr10, '0.2%')
        if cagr10 >= 0.15:
            self._voted[self._v_score] += 2
        if cagr10 >= 0.1:
            self._voted[self._v_score] += 1

    def _get_analyzing_columns(self):
        return [C_TOTAL_OPER_PROFIT, C_OPERATING_PROFIT]

    def _get_voting_columns(self):
        return [C_OPER_PROFIT_MARGIN, V_OPM_SCORE]

    def _do_analyzing(self, df: pd.DataFrame) -> pd.DataFrame:
        df[C_OPER_PROFIT_MARGIN] = df[C_OPERATING_PROFIT] / df[
            C_TOTAL_OPER_PROFIT]

        self._opm_by_sum = df[C_OPERATING_PROFIT].sum() / df[
            C_TOTAL_OPER_PROFIT].sum()
        return df


class NpmAnalyzer(AverageLikeAnalyzer):
    '''
    净利率分析：C_NET_PROFIT_MARGIN
    '''

    def _do_analyzing(self, df: pd.DataFrame) -> pd.DataFrame:
        df[C_NET_PROFIT_MARGIN] = df[C_NET_PROFIT] / df[C_TOTAL_OPER_PROFIT]

        self._npm_by_sum = df[C_NET_PROFIT].sum() / df[C_TOTAL_OPER_PROFIT].sum()
        return df

    def _get_voting_columns(self) -> []:
        return [C_NET_PROFIT_MARGIN, V_NPM_SCORE]

    def _get_analyzing_columns(self) -> []:
        return [C_TOTAL_OPER_PROFIT, C_NET_PROFIT]

    def _custom_voting(self):
        self._voted[V_NPM] = format(self._npm_by_sum, '0.2%')

        a_df = self._analyzed_df
        selected = a_df[C_NET_PROFIT]
        cagr10 = pow(selected.iloc[0] / selected.iloc[-1], 1 / 10) - 1
        self._voted[V_CAGR] = format(cagr10, '0.2%')
        if cagr10 >= 0.15:
            self._voted[self._v_score] += 2
        if cagr10 >= 0.1:
            self._voted[self._v_score] += 1
