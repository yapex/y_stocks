import logging
import os

import akshare as ak
import pandas as pd
import toml
from tqdm import tqdm
from loguru import logger

from ystocks.settings import *

_is_init = False

_stock_runtime: dict


def get_runtime(reload=False) -> dict:
    if _is_init == False or reload:
        _stock_runtime = toml.load(ENV_TOML_PATH)

    return _stock_runtime


def get_logger():
    return logger


log = get_logger()


def __init_env__():
    get_runtime(True)
    report_types = [ZCFZ_TABLE_NAME, LRB_TABLE_NAME, XJLL_TABLE_NAME]
    for report_type in report_types:
        report_to_csv(report_type)
        separate_by_stock_code(report_type)

    log.debug('...finished')


# 准备运行环境
def get_date_for_download():
    return pd.date_range(start='20121231', end='20211231', freq='Y')


def post_process(df, date_str):
    assert not df.empty
    df[REPORT_DATE_NAME] = date_str
    # 去除列名上的空格
    df.columns.map(lambda x: str(x).strip())
    return df


def get_report_by(name):
    if ZCFZ_TABLE_NAME == name:
        return ak.stock_zcfz_em
    if LRB_TABLE_NAME == name:
        return ak.stock_lrb_em
    if XJLL_TABLE_NAME == name:
        return ak.stock_xjll_em


def download_report(date_str, report_type):
    # 获取资产负债表
    log.debug(f'prepare downloading {report_type}: {date_str} ...')
    _get_report_by = get_report_by(report_type)
    df = _get_report_by(date_str)
    return post_process(df, date_str)


def get_report_filename(report_type):
    if not os.path.exists:
        os.mkdir(f'{get_runtime()[E_CACHED_DIR]}')
    return f'{get_runtime()[E_CACHED_DIR]}/A股{report_type}.csv'


def report_to_csv(report_type):
    dates = get_date_for_download().strftime("%Y%m%d")
    filename = get_report_filename(report_type)
    if not os.path.exists(filename):
        log.debug(f'{filename} not exist, prepare to cache it')
        dfs = []
        for _date in dates:
            dfs.append(download_report(_date, report_type))

        df = pd.concat(dfs, axis=0, ignore_index=True)
        r_df = df.sort_values([STOCK_CODE, REPORT_DATE_NAME],
                              ascending=False)
        r_df.to_csv(filename, index_label=CSV_DEFULT_INDEX)


def _get_seprated_by_company_path():
    return get_runtime()[E_CACHED_DIR] + get_runtime()[E_BY_COMPANY_PATH]


def separate_by_stock_code(report_type):
    df = pd.read_csv(f'{get_runtime()[E_CACHED_DIR]}/A股{report_type}.csv',
                     index_col=CSV_DEFULT_INDEX,
                     dtype={STOCK_CODE: 'str'})
    sorted_df = df.sort_values([STOCK_CODE, REPORT_DATE_NAME])
    sorted_df = sorted_df.fillna(0)
    codes = sorted_df[STOCK_CODE].unique()

    log.debug(f'prepare separating {len(codes)} stocks in {report_type}')
    os.makedirs(_get_seprated_by_company_path(), exist_ok=True)

    for code in tqdm(codes):
        filename = get_company_csv_filename_by(report_type, code)
        selected = sorted_df[sorted_df[STOCK_CODE] == code]
        selected.to_csv(filename, index_label=CSV_DEFULT_INDEX, mode='w')
        log.debug(f'{code}_{report_type} already cached in: {filename}')


def get_company_csv_filename_by(report_type, stock_code):
    by_company_path = _get_seprated_by_company_path()
    return f'{by_company_path}/{stock_code}_{report_type}.csv'

def get_merged_table_filename(stock_code):
    file_path = get_runtime()[E_CACHED_DIR] + '/merged'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path + f'/{stock_code}_merged.csv'

def get_merged_table_by(stock_code):
    mered_filename = get_merged_table_filename(stock_code)
    if os.path.exists(mered_filename):
        log.debug(f'find cached file: {mered_filename}')
        df = pd.read_csv(mered_filename, index_col=CSV_DEFULT_INDEX,
                         dtype={STOCK_CODE: 'str'})
        return df
    # 获取资产负债表
    zcfz_filename = get_company_csv_filename_by(ZCFZ_TABLE_NAME, stock_code)
    if not os.path.exists(zcfz_filename):
        raise FileNotFoundError(
            f'{zcfz_filename} not exists, we need to prepare env first')
    zcfz_df = pd.read_csv(zcfz_filename, index_col=CSV_DEFULT_INDEX,
                          dtype={STOCK_CODE: 'str'})
    # 获取利润表
    lrb_filename = get_company_csv_filename_by(LRB_TABLE_NAME, stock_code)
    if not os.path.exists(lrb_filename):
        raise FileNotFoundError(
            f'{lrb_filename} not exists, we need to prepare env first')
    lrb_df = pd.read_csv(lrb_filename, index_col=CSV_DEFULT_INDEX,
                         dtype={STOCK_CODE: 'str'})
    #合并
    zcfz_lrb_df = pd.merge(zcfz_df, lrb_df, how='right', on=REPORT_DATE_NAME)
    #获取现金流量表
    xjll_filename = get_company_csv_filename_by(XJLL_TABLE_NAME, stock_code)
    if not os.path.exists(xjll_filename):
        raise FileNotFoundError(
            f'{xjll_filename} not exists, we need to prepare env first')
    xjll_df = pd.read_csv(xjll_filename, index_col=CSV_DEFULT_INDEX,
                          dtype={STOCK_CODE: 'str'})
    # 合并
    big_df = pd.merge(zcfz_lrb_df, xjll_df, how='right', on=REPORT_DATE_NAME)
    big_df.sort_values([REPORT_DATE_NAME], ascending=False, inplace=True)
    # 缓存结果
    big_df.to_csv(mered_filename, index_label=CSV_DEFULT_INDEX, mode='w')
    return big_df
