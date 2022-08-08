import csv
from loguru import logger

if __name__ == "main":
    with open("test-cached/三羊开泰/net_value_2018.csv", "rb") as f:
        reader = csv.reader(f)
        data_as_list = list(reader)

    logger.add("output/ystocks.log", rotation="1 week")
    logger.debug(f"length: {len(data_as_list)}")
