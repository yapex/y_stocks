#!/usr/bin/env python

from cmath import log
import glob
import os

import pandas as pd
from loguru import logger

path: str = 'data/san_yang_kai_tai/'
merged_file_name = 'merged_net_values.csv'

if os.path.exists(path+merged_file_name):
    os.remove(path+merged_file_name)

files: list[str] = glob.glob(path + "*.csv")
sorted_files: list[str] = sorted(files)
logger.info(f"find csv files: {sorted_files}")

merged_df: pd.DataFrame = pd.DataFrame()
for file in sorted_files:
    curr_df: pd.DataFrame = pd.read_csv(file)
    logger.debug(f"going to merge: {curr_df.head(1)}")
    logger.debug(curr_df.sample())
    merged_df: pd.DataFrame = pd.concat(
        [merged_df, curr_df], ignore_index=True)

if len(merged_df):
    merged_df.drop_duplicates(inplace=True)
    merged_df.to_csv(path+merged_file_name, index_label='index')
    logger.debug(f"{len(merged_df)} records merged.")
