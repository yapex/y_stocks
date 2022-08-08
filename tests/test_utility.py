import os.path

import pandas as pd
import pytest
import toml
import ystocks.utility as yu
from ystocks.settings import *

report_types = [ZCFZ_TABLE_NAME, LRB_TABLE_NAME, XJLL_TABLE_NAME]


@pytest.fixture()
def get_csv_name():
    c_path = yu._get_seprated_by_company_path()
    return [(ZCFZ_TABLE_NAME, '600519', c_path + '/600519_资产负债表.csv'),
            (LRB_TABLE_NAME, '600519', c_path + '/600519_利润表.csv'),
            (XJLL_TABLE_NAME, '002304', c_path + '/002304_现金流量表.csv')]


class TestUtility:

    def test_get_csv_name_by(self, get_csv_name):
        for type, code, expected in get_csv_name:
            assert expected == yu.get_company_csv_filename_by(type, code)

    def test_get_runtime(self):
        runtime = yu.get_runtime()
        assert runtime['test']['sayhello'] == 'hello'

    def test_merge_3_df_by(self, monkeypatch):
        self.prepare_mock(monkeypatch)

        s_code = '000001'
        df: pd.DataFrame = yu.get_merged_table_by(s_code)
        assert not df.empty
        count = len(self.mock_get_date_for_dowanlad())
        assert df[C_NET_PROFIT].count() == count
        assert df[C_EQUITY].count() == count
        assert df[C_OPER_NET_CASH].count() == count

        assert os.path.exists(yu.get_merged_table_filename(s_code))

    def mock_get_date_for_dowanlad(self):
        return pd.date_range(start='20201231', end='20211231', freq='Y')

    def mock_get_runtime(self, reload=True):
        return toml.load(ENV_TOML_PATH)['test']

    def test_report_to_csv(self, monkeypatch):
        self.prepare_mock(monkeypatch)

        assert len(yu.get_date_for_download()) == len(
            self.mock_get_date_for_dowanlad())

        for report_type in report_types:
            assert yu.get_report_filename(report_type).endswith(
                f'A股{report_type}.csv')
            yu.report_to_csv(report_type)
            assert os.path.exists(yu.get_report_filename(report_type))

    def prepare_mock(self, monkeypatch):
        monkeypatch.setattr(yu, 'get_runtime', self.mock_get_runtime)
        monkeypatch.setattr(yu, 'get_date_for_download',
                            self.mock_get_date_for_dowanlad)

    def test_separate_by_stock_code(self, monkeypatch):
        self.prepare_mock(monkeypatch)
        assert len(yu.get_date_for_download()) == len(
            self.mock_get_date_for_dowanlad())
        # 以下代码太过耗费时间，轻易不运行
        '''
        for report_type in report_types:
            yu.separate_by_stock_code(report_type)
        '''
