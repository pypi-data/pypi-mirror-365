import numpy as np
import pandas as pd
from scipy.stats import jarque_bera


def calculate_stats(column):
    mean_val = column.mean()
    std_error = column.std() / np.sqrt(len(column))
    median_val = column.median()
    std_dev = column.std()
    var_val = column.var()
    kurtosis_val = column.kurt()
    skewness_val = column.skew()
    range_val = column.max() - column.min()
    min_val = column.min()
    max_val = column.max()
    sum_val = column.sum()
    # 按照顺序拼接结果
    stats_result = [
        mean_val,
        std_error,
        median_val,
        std_dev,
        var_val,
        kurtosis_val,
        skewness_val,
        range_val,
        min_val,
        max_val,
        sum_val
    ]
    return stats_result

def describe(df):
    all_results = {}
    for col in df.columns:
        column_data = df[col]
        stats_result = calculate_stats(column_data)
        all_results[col] = stats_result

    index_names = [
        '平均',
        '标准误差',
        '中位数',
        '标准差',
        '方差',
        '峰度',
        '偏度',
        '区域',
        '最小值',
        '最大值',
        '求和'
    ]
    return pd.DataFrame(all_results, index=index_names)
def jb_test(file_path, alpha=0.05):
    df = pd.read_excel(file_path)
    jb_results = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        data = df[col].dropna()  # 去除缺失值
        if len(data) >= 3:  # JB检验需要至少3个数据点
            jb_stat, p_value = jarque_bera(data)
            jb_results.append([col, round(jb_stat, 4), round(p_value, 4)])
        else:
            jb_results.append([col, None, None, "数据量不足"])  # 数据量不足时标记

    result_df = pd.DataFrame(
        jb_results,
        columns=['列名', 'JB统计量', 'p值']
    )
    result_df.transpose().to_excel('JB检验.xlsx', index=True,header=False)