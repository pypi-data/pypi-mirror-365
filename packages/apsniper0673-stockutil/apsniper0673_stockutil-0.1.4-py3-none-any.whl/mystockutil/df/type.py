import pandas as pd
import numpy as np

def init_df_with_type(
    df: pd.DataFrame,
    int_cols: list[str] = None,
    float_cols: list[str] = None,
    insert_when_not_exist:bool = True,
    fill_int_value: int = 0,
    fill_float_value: float = 0.0
    ) -> pd.DataFrame:
    """
    DataFrame의 특정 열을 지정된 타입으로 초기화합니다.
    Parameters
    ----------
    df : pd.DataFrame
        초기화할 DataFrame
    int_cols : list[str], optional
        정수형으로 초기화할 열의 리스트, 기본값은 None
    float_cols : list[str], optional
        실수형으로 초기화할 열의 리스트, 기본값은 None
    insert_when_not_exist : bool, optional
        지정된 열이 DataFrame에 없을 경우 새로 추가할지 여부, 기본값은 True
    """
    df = df.copy()  # 원본 DataFrame을 변경하지 않도록 복사
    if int_cols is None:
        int_cols = []
    if float_cols is None:
        float_cols = []
    # 정수형 열 초기화
    for col in int_cols:
        if col not in df.columns:
            if insert_when_not_exist:
                df[col] = 0
            else:
                continue
        df[col] = df[col].fillna(fill_int_value).astype(int)
    # 실수형 열 초기화
    for col in float_cols:
        if col not in df.columns:
            if insert_when_not_exist:
                df[col] = 0.0
            else:
                continue
        df[col] = df[col].fillna(fill_float_value).astype(float)
    return df