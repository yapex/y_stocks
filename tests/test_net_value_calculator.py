

from ystocks.netvalues import NetValueCalculator


class TestNetValueCalculator:
    def test_add_first(self):
        nv_c = NetValueCalculator()
        nv_c.record_invest(date_time='2018-01-01',
                           invest_value=0, add_cash=6494005.25)
        df = nv_c.take_snapshot()
        assert len(df) == 1
        assert df['净值'][0] == 1.0000

    def test_add_more(self):
        nv_c = NetValueCalculator()
        nv_c.record_invest(date_time='2018-01-01',
                           invest_value=0, add_cash=6494005.25)
        nv_c.record_invest(date_time='2018-01-02', invest_value=6595041.35)
        nv_c.record_invest(date_time='2018-01-03',
                           invest_value=6748813.81, add_cash=71612.17)

        df = nv_c.take_snapshot()

        assert len(df) == 3
        assert df['净值'][0] == 1.0
        assert round(df['净值'][1], 4) == 1.0156
        assert round(df['净值'][2], 4) == 1.0281
