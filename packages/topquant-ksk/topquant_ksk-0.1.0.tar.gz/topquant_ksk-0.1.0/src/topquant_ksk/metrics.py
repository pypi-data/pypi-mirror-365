import pandas as pd
import numpy as np
from tqdm import tqdm
def get_RiskReturnProfile(rebalencing_ret: pd.DataFrame, cash_return_daily_BenchmarkFrequency: pd.Series, BM: pd.Series | None = None):
    """
    수익률 데이터를 받아 주요 성과 지표를 계산합니다.
    IndexingError를 수정한 최종 벡터화 코드를 사용합니다.
    """
    
    def calculate_max_underwater_period(value_series: pd.Series) -> float:
        """단일 가치 시리즈에 대한 최대 손실 기간(연 단위)을 계산하는 내부 함수"""
        if value_series.empty or value_series.isnull().all():
            return 0.0
            
        value_max = value_series.cummax()
        underwater_series = value_max > value_series
        
        if not underwater_series.any():
            return 0.0
            
        # 연속된 하락 기간(True)의 길이를 계산
        underwater_groups = (underwater_series != underwater_series.shift()).cumsum()
        underwater_lengths = underwater_series.groupby(underwater_groups).sum()
        
        # ★★★ 오류 수정: 하락(True) 그룹만 필터링한 후 최대 기간을 찾음 ★★★
        # 1. underwater_series가 True인 그룹 ID를 찾음
        true_groups = underwater_groups[underwater_series]
        # 2. 해당 그룹 ID에 해당하는 길이들 중에서 최대값을 찾음
        max_period_days = underwater_lengths.loc[true_groups.unique()].max()

        return round(max_period_days / 252, 1)

    # --- 1. 전략(들)에 대한 공통 성과 지표 계산 ---
    CAGR = (np.exp(np.log(rebalencing_ret + 1).mean() * 252) - 1).round(3) * 100
    STD_annualized = (rebalencing_ret.std() * np.sqrt(252)).round(3) * 100
    
    excess_ret = rebalencing_ret.subtract(cash_return_daily_BenchmarkFrequency.reindex(rebalencing_ret.index, method='ffill'), axis=0)
    excess_ret_yearly = (np.exp(np.log(excess_ret + 1).mean() * 252) - 1)
    Sharpe_Ratio = (excess_ret_yearly / (rebalencing_ret.std() * np.sqrt(252))).round(3)
    
    pfl_value = (rebalencing_ret + 1).cumprod()
    MDD = (pfl_value / pfl_value.cummax() - 1).min().round(3) * 100
    MDD_date = (pfl_value / pfl_value.cummax() - 1).idxmin().astype(str).str[:7]
    UnderWaterPeriod = pfl_value.apply(calculate_max_underwater_period)

    # 기간별 수익률
    ret_1M = ((rebalencing_ret.iloc[-21:] + 1).prod() - 1).round(3) * 100
    ret_3M = ((rebalencing_ret.iloc[-21*3:] + 1).prod() - 1).round(3) * 100
    ret_6M = ((rebalencing_ret.iloc[-21*6:] + 1).prod() - 1).round(3) * 100
    ret_1Y = ((rebalencing_ret.iloc[-252:] + 1).prod() - 1).round(2) * 100
    ret_3Y = ((rebalencing_ret.iloc[-252*3:] + 1).prod() - 1).round(2) * 100
    
    metrics_list = [
        CAGR, STD_annualized, Sharpe_Ratio, MDD, MDD_date, UnderWaterPeriod,
        ret_1M, ret_3M, ret_6M, ret_1Y, ret_3Y
    ]
    index_list = [
        'CAGR(%)', 'STD_annualized(%)', 'Sharpe_Ratio', 'MDD(%)', 'MDD시점', 'UnderWaterPeriod(년)',
        '1M Ret(%)', '3M Ret(%)', '6M Ret(%)', '1Y Ret(%)', '3Y Ret(%)'
    ]
    
    matric = pd.DataFrame(metrics_list, index=index_list).T
    
    if BM is not None:
        aligned_ret, aligned_bm = rebalencing_ret.align(BM, join='inner', axis=0)
        
        # BM 자체의 공통 성과 지표 계산
        BM_CAGR = round(np.exp(np.log(aligned_bm + 1).mean() * 252) - 1, 3) * 100
        BM_STD = round(aligned_bm.std() * np.sqrt(252), 3) * 100
        bm_excess_ret = aligned_bm.subtract(cash_return_daily_BenchmarkFrequency.reindex(aligned_bm.index, method='ffill'))
        bm_excess_ret_yearly = np.exp(np.log(bm_excess_ret + 1).mean() * 252) - 1
        BM_Sharpe = round(bm_excess_ret_yearly / (aligned_bm.std() * np.sqrt(252)), 3)
        bm_value = (aligned_bm + 1).cumprod()
        BM_MDD = round((bm_value / bm_value.cummax() - 1).min(), 3) * 100
        BM_MDD_date = (bm_value / bm_value.cummax() - 1).idxmin().strftime('%Y-%m')
        BM_UnderWaterPeriod = calculate_max_underwater_period(bm_value)
        BM_ret_1M = round((aligned_bm.iloc[-21:] + 1).prod() - 1, 3) * 100
        BM_ret_3M = round((aligned_bm.iloc[-21*3:] + 1).prod() - 1, 3) * 100
        BM_ret_6M = round((aligned_bm.iloc[-21*6:] + 1).prod() - 1, 3) * 100
        BM_ret_1Y = round((aligned_bm.iloc[-252:] + 1).prod() - 1, 2) * 100
        BM_ret_3Y = round((aligned_bm.iloc[-252*3:] + 1).prod() - 1, 2) * 100
        
        # 전략의 BM 대비 상대 성과 지표 계산
        excess_return_vs_bm = aligned_ret.subtract(aligned_bm, axis=0)
        annualized_excess_return = (np.exp(np.log(excess_return_vs_bm + 1).mean() * 252) - 1)
        tracking_error = excess_return_vs_bm.std() * np.sqrt(252)
        information_ratio = (annualized_excess_return / tracking_error).round(3)
        relative_value = (excess_return_vs_bm + 1).cumprod()
        relative_drawdown = (relative_value / relative_value.cummax() - 1)
        max_relative_drawdown = relative_drawdown.min().round(3) * 100
        max_relative_drawdown_date = relative_drawdown.idxmin().astype(str).str[:7]
        max_relative_underwater_duration = relative_value.apply(calculate_max_underwater_period)

        # 최종 결과 테이블에 상대 성과 지표 컬럼 추가
        matric['BM excess_return(%)']=round(annualized_excess_return*100,1)
        matric['tracking_error(%)']=round(tracking_error*100,1)
        matric['Information_Ratio'] = information_ratio
        matric['BM대비최대손실(%)'] = max_relative_drawdown
        matric['BM대비최대손실시점'] = max_relative_drawdown_date
        matric['BM Max Underwater(년)'] = max_relative_underwater_duration

        # BM 성과 행 생성 및 추가
        bm_metrics_row = pd.Series(name='Benchmark', dtype=object)
        bm_metrics_row['CAGR(%)'] = BM_CAGR
        bm_metrics_row['STD_annualized(%)'] = BM_STD
        bm_metrics_row['Sharpe_Ratio'] = BM_Sharpe
        bm_metrics_row['MDD(%)'] = BM_MDD
        bm_metrics_row['MDD시점'] = BM_MDD_date
        bm_metrics_row['UnderWaterPeriod(년)'] = BM_UnderWaterPeriod
        bm_metrics_row['1M Ret(%)'] = BM_ret_1M
        bm_metrics_row['3M Ret(%)'] = BM_ret_3M
        bm_metrics_row['6M Ret(%)'] = BM_ret_6M
        bm_metrics_row['1Y Ret(%)'] = BM_ret_1Y
        bm_metrics_row['3Y Ret(%)'] = BM_ret_3Y
        bm_metrics_row['BM excess_return(%)'] = '-'
        bm_metrics_row['tracking_error(%)'] = '-'
        bm_metrics_row['Information_Ratio'] = '-'
        bm_metrics_row['BM대비최대손실(%)'] = '-'
        bm_metrics_row['BM대비최대손실시점'] = '-'
        bm_metrics_row['BM Max Underwater(년)'] = '-'

        matric = pd.concat([matric, bm_metrics_row.to_frame().T])

    return matric