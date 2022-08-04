import pandas as pd
import toml

import ystocks.utility as yu
from ystocks.settings import *
from ystocks.stocks import RoeAnalyzer, FocAnalyzer, OpmAnalyzer, NpmAnalyzer


def mock_get_runtime(reload=True):
    return toml.load(ENV_TOML_PATH)['test']


def mock_get_date_for_dowanlad():
    return pd.date_range(start='20201231', end='20211231', freq='Y')


def mock_get_merged_table_by(stock_code):
    data = {C_NET_PROFIT: [50, 45], C_EQUITY: [100, 92],
            REPORT_DATE_NAME: ['20211231', '20201231'],
            C_STOCK_S_NAME: ['贵州茅台', '贵州茅台'],
            STOCK_CODE: ['600519', '600519'],
            C_OPER_NET_CASH: [80, 70],
            C_CAPITAL_COST: [20, 19],
            C_TOTAL_OPER_PROFIT: [100, 90],
            C_OPERATING_PROFIT: [93, 81],
            C_NET_PROFIT: [50, 46]}
    df = pd.DataFrame(data)
    return df


def prepare_mock(monkeypatch):
    monkeypatch.setattr(yu, 'get_merged_table_by',
                        mock_get_merged_table_by)
    monkeypatch.setattr(yu, 'get_runtime', mock_get_runtime)
    monkeypatch.setattr(yu, 'get_date_for_download',
                        mock_get_date_for_dowanlad)


class TestRoeAnalyzer:

    def test_preprocess(self, monkeypatch):
        prepare_mock(monkeypatch)

        roe_a = RoeAnalyzer('600519')
        df = roe_a._preprocess()
        assert not df.empty
        assert df.loc[0, STOCK_CODE] == '600519'
        assert df.loc[0, C_STOCK_S_NAME] == '贵州茅台'

    def test_voting(self, monkeypatch):
        prepare_mock(monkeypatch)

        roe_a = RoeAnalyzer('600519')
        voted = roe_a.voting()
        assert roe_a._is_analyzed == True
        assert voted.name == '600519'
        assert voted[V_ROE_SCORE] == 3.0
        assert voted[C_STOCK_S_NAME] == '贵州茅台'
        assert voted[V_10Y_MEDIAN] == '50.00%'
        # assert voted[V_ANY_ROW_NOT_LT_EXPECTED] == True

    def test_analyzing(self, monkeypatch):
        prepare_mock(monkeypatch)

        roe_a = RoeAnalyzer('600519')
        df = roe_a.analyzing()
        assert not df.empty
        assert roe_a._is_analyzed
        assert round(df.loc[0, C_ROE], 2) == 0.5

    def test_do_analyzing(self, monkeypatch):
        prepare_mock(monkeypatch)

        roe_a = RoeAnalyzer('600519')
        p_df = roe_a._preprocess()
        a_df = roe_a._do_analyzing(p_df)
        assert not a_df.empty
        assert a_df.loc[0, C_ROE] == 50 / 100
        assert a_df.loc[1, C_ROE] == 0.5


class TestFocAnalyzer:
    def test__do_analyzing(self, monkeypatch):
        prepare_mock(monkeypatch)

        foc_a = FocAnalyzer('600519')
        p_df = foc_a._preprocess()
        assert not p_df.empty
        assert not p_df[C_OPER_NET_CASH].empty
        assert not p_df[C_CAPITAL_COST].empty

        a_df = foc_a._do_analyzing(p_df)
        assert a_df.loc[0, C_FOC] == (80 - 20) / 100
        assert foc_a._foc_by_sum == ((80 + 70) - (20 + 19)) / (100 + 92)

    def test_voting(self, monkeypatch):
        prepare_mock(monkeypatch)

        foc_a = FocAnalyzer('600519')
        voted_s = foc_a.voting()
        assert not voted_s.empty
        assert voted_s[C_STOCK_S_NAME] == '贵州茅台'
        assert voted_s[V_FOC_SCORE] == 2.97
        # assert voted_s[V_ANY_ROW_NOT_LT_EXPECTED] == True


class TestOpmAnalyzer:
    def test__get_voting_columns(self, monkeypatch):
        prepare_mock(monkeypatch)

        opm = OpmAnalyzer('600519')
        _type, score = opm._get_voting_columns()
        assert _type == C_OPER_PROFIT_MARGIN
        assert score == V_OPM_SCORE

    def test__get_analyzing_columns(self, monkeypatch):
        prepare_mock(monkeypatch)
        opm = OpmAnalyzer('600519')
        total_profit, oper_profit = opm._get_analyzing_columns()
        assert total_profit == C_TOTAL_OPER_PROFIT
        assert oper_profit == C_OPERATING_PROFIT

    def test__do_analyzing(self, monkeypatch):
        prepare_mock(monkeypatch)
        opm = OpmAnalyzer('600519')
        a_df = opm.analyzing()
        assert not a_df.empty
        assert a_df.loc[0, C_OPER_PROFIT_MARGIN] == 93 / 100

    def test_voting(self, monkeypatch):
        prepare_mock(monkeypatch)
        opm = OpmAnalyzer('600519')

        voted = opm.voting()
        assert not voted.empty
        assert voted[V_OPM_SCORE] == 2.98

    def test_000568(self, monkeypatch):
        monkeypatch.setattr(yu, 'get_runtime', mock_get_runtime)

        opm = OpmAnalyzer('000568')

        a_def = opm.analyzing()

        assert not a_def.empty
        assert a_def.loc[0, STOCK_CODE] == '000568'


class TestNpmAnalyzer:
    def test__do_analyzing(self, monkeypatch):
        prepare_mock(monkeypatch)
        npm = NpmAnalyzer('600519')
        a_df = npm.analyzing()
        assert not a_df.empty
        assert a_df.loc[0, C_NET_PROFIT_MARGIN] == 0.5

    def test_voting(self, monkeypatch):
        prepare_mock(monkeypatch)

        npm = NpmAnalyzer('600519')
        voted = npm.voting()
        assert not voted.empty
        assert voted[V_NPM_SCORE] == 2.99
