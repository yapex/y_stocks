import pandas as pd
from tabulate import tabulate
import snoop

from y_stocks.settings import V_NPM_SCORE
from y_stocks.stocks import NpmAnalyzer

snoop.install()

stock_codes = ['600519', '600809', '000858', '002304', '000568', '603369',
               '000799', '000596', '600779', '603589']
voted = []
for code in stock_codes:
    npm = NpmAnalyzer(code)
    _s = npm.voting()
    voted.append(_s)

r_df = pd.concat(voted, axis=1)
r_df.sort_values([V_NPM_SCORE], axis=1, ascending=False)

pp(r_df.values)

# print(tabulate(r_df, headers='keys', floatfmt='.2f', tablefmt='grid'))
