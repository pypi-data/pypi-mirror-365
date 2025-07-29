import os
import pandas as pd
import warnings

# ==============================================================================
# ## 헬퍼(Helper) 함수 (이전과 동일)
# ==============================================================================

def find_file_recursive(filename: str) -> str | None:
    """현재 디렉토리와 하위에서 파일을 재귀적으로 찾아 경로를 반환합니다."""
    root_dir = os.getcwd()
    for root, _, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def _load_file(file_path: str, sheet_name: str | None = None) -> pd.DataFrame | None:
    """파일 경로와 시트 이름(선택)으로 데이터프레임을 로드하는 공통 함수"""
    try:
        if file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, sheet_name=sheet_name, index_col=[0])
        elif file_path.endswith('.csv'):
            return pd.read_csv(file_path, encoding='cp949', index_col=[0], low_memory=False)
        else:
            print(f"지원하지 않는 파일 형식입니다: {file_path}")
            return None
    except Exception as e:
        print(f"파일 로드 중 오류: {e}")
        return None

def _process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """데이터프레임 후처리를 위한 공통 함수"""
    idx = df.index
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        non_date_elements = idx[pd.to_datetime(idx, errors='coerce').isna()]
    df.drop(non_date_elements, inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index.name = None
    df.replace(',', '', regex=True, inplace=True)
    df.dropna(how='all',axis=1,inplace=True)
    print("float 타입으로 변환을 시도합니다...")
    for col in df.columns:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass
    return df

# ✨ 수정된 마스터 헬퍼 함수
def _load_and_process_data(filename: str, column_spec: list, data_type_name: str, sheet_name: str | None = None) -> pd.DataFrame | None:
    """파일 검색, 로드, 후처리 전체 과정을 수행하는 마스터 헬퍼 함수"""
    file_path = find_file_recursive(filename)
    if not file_path:
        print(f"'{filename}' 파일을 찾을 수 없습니다. 🤷‍♂️")
        return None
    
    print(f"파일 발견! '{file_path}' 파일을 로드합니다... 📂")
    df = _load_file(file_path, sheet_name=sheet_name)
    if df is None:
        return None

    print(f"{data_type_name} 데이터 후처리를 시작합니다... 🛠️")
    
    # --- ✨ 컬럼 설정 로직 수정 ✨ ---
    if len(column_spec) == 1:
        # column_spec의 길이가 1이면 단일 인덱스로 설정
        df.columns = df.loc[column_spec[0]]
    else:
        # 길이가 1보다 크면 멀티인덱스로 설정
        df.columns = [df.loc[name] for name in column_spec]

    # 공통 후처리 로직 호출
    df = _process_dataframe(df)
    
    print("처리 완료! ✨")
    return df

# ==============================================================================
# ## ✨ 메인(Main) 데이터 로드 함수 (수정됨) ✨
# ==============================================================================

def load_FactSet_TimeSeriesData(filename: str, sheet_name: str | None = 'TimeSeries') -> pd.DataFrame | None:
    """TimeSeries 데이터를 로드합니다. (3-level columns)"""
    return _load_and_process_data(
        filename=filename,
        sheet_name=sheet_name,
        column_spec=['Item Name', 'Symbol Name', 'Symbol'],
        data_type_name='TimeSeries'
    )


def load_DataGuide_TimeSeriesData(filename: str, sheet_name: str | None = 'TimeSeries') -> pd.DataFrame | None:
    """TimeSeries 데이터를 로드합니다. (3-level columns)"""
    return _load_and_process_data(
        filename=filename,
        sheet_name=sheet_name,
        column_spec=['Item Name', 'Symbol Name', 'Symbol'],
        data_type_name='TimeSeries'
    )

def load_DataGuide_IndexData(filename: str, sheet_name: str | None = 'TimeSeries') -> pd.DataFrame | None:
    """Index 데이터를 로드합니다. (2-level columns)"""
    return _load_and_process_data(
        filename=filename,
        sheet_name=sheet_name,
        column_spec=['Item Name', 'Symbol Name'],
        data_type_name='Index'
    )

def load_DataGuide_EconomicData(filename: str, sheet_name: str | None = 'Economic') -> pd.DataFrame | None:
    """Economic 데이터를 로드합니다. (1-level column)"""
    return _load_and_process_data(
        filename=filename,
        sheet_name=sheet_name,
        column_spec=['Item Name'],
        data_type_name='Economic'
    )

def load_DataGuide_CrossSectionalData(filename: str) -> pd.DataFrame | None:
    """
    지정된 파일명으로 CrossSectional 데이터를 찾아 로드하고 전처리합니다.
    """
    file_path = find_file_recursive(filename)

    if not file_path:
        print(f"현재 폴더 및 하위 폴더에서 '{filename}' 파일을 찾을 수 없습니다. 🤷‍♂️")
        return None

    print(f"파일 발견! '{file_path}' 파일을 로드합니다... 📂")

    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, sheet_name='CrossSectional', index_col=[1, 0])
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='cp949', index_col=[1, 0], low_memory=False)
        else:
            print(f"지원하지 않는 파일 형식입니다: {filename}")
            return None
    except Exception as e:
        print(f"파일 로드 중 오류: {e}")
        return None

    print("CrossSectional 데이터 후처리를 시작합니다... 🛠️")
    header_tuple = ('Name', 'Symbol')
    df.columns = df.loc[header_tuple]
    header_location = df.index.get_loc(header_tuple)
    df = df.iloc[header_location + 1:]
    df.columns.names = ['Item Name']
    df.index.names = ['Name', 'Symbol']
    df.replace(',', '', regex=True, inplace=True)

    print("float 타입으로 변환을 시도합니다...")
    for col in df.columns:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass

    print("처리 완료! ✨")
    return df