import pandas as pd
from typing import Dict

from mystockutil.type_convert import convert_numeric_columns

class SheetLoader:
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        # 로딩한 시트를 저장할 딕셔너리
        self.dfd:Dict[str, pd.DataFrame] = {}
        
    def get_url(self, sheet_name=None)-> str:
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    # 시트로딩하여 DF로 변환
    def _fetch_sheet(self, sheet_name)-> pd.DataFrame:
        try:
            df = pd.read_csv(self.get_url(sheet_name=sheet_name))

            # ⬇️ 모든 값이 NaN인 열/행 제거 > 칼럼명만 존재해도 보전
            df.dropna(axis=0, how='all', inplace=True)  # 모든 값이 NaN인 행 제거
            df = df.drop(columns=[
                col for col in df.columns
                if col.startswith("Unnamed") and df[col].isna().all()
            ])

            # 숫자로 변환 가능한 열 자동 처리
            converted_df = convert_numeric_columns(df)
            self.dfd[sheet_name] = converted_df
            return converted_df

        except Exception as e:
            print(f"Error loading sheet: {e}")
            return pd.DataFrame(columns=[])


class GRSheetLoader(SheetLoader):
    def __init__(self, sheet_id, generator_parameters_sn, trader_variables_sn=None):
        super().__init__(sheet_id)
        self.gnpm_sn = generator_parameters_sn
        self.tv_sn = trader_variables_sn
        self.param_columns = None
        self.trader_columns = None
        
    def set_columns(self, parameter_columns, trader_columns=None):
        "시트로더에게 패러매터 칼럼과 트레이더 칼럼을 설정한다."
        self.param_columns = parameter_columns
        self.trader_columns = trader_columns

    def fetch_parameters(self, selection_key=None)-> dict|pd.DataFrame:
        selection = self.fetch(selection_key=selection_key, sheet_name=self.gnpm_sn, columns = self.param_columns)
        if selection_key is not None:
            return selection.to_dict(orient='records')[0]
        else:
            return selection
    def fetch_trader_variables(self, selection_key=None)-> dict|pd.DataFrame:
        selection = self.fetch(selection_key=selection_key, sheet_name=self.tv_sn, columns = self.trader_columns)
        if selection_key is not None:
            return selection.to_dict(orient='records')[0]
        else:
            return selection
    def fetch(self, selection_key:int=None, sheet_name=None, columns=None)-> pd.DataFrame:
        df = self._fetch_sheet(sheet_name=sheet_name)
        if selection_key is not None:
            selection = df[df['채택'] == int(selection_key)]
            if len(selection) != 1:
                raise ValueError(f"Selection for key '{selection_key}' returned {len(selection)} rows, expected 1.")
        else:
            selection = df
        if columns is not None:
            selection = selection[columns]
        return selection

# 황금비 설정 시트    
gr_sheet_id = "1Mn_dpfOZ8EVBOjo_y-2rsGVICwjozbfg_l4XH4GnnTs"
gr_gnpr_sheet_name = "GoldenRatio"  # 또는 실제 시트 이름으로 변경
gr_tv_sheet_name = "TraderVariables"  # 또는 실제 시트 이름으로 변경
gr_gnpr_columns = [
    "radius", "회전율하단", "회전율상단", "변동률하단", "변동률상단", 
    "이격도기준", "이격도하단", "이격도상단", "기준거래대금", 
    "기준최고가범위", "고가유지ma범위", "고가유지alpha", 
    "고가유지beta", "청산이평범위", "청산카운트", "최고대손절비",
]
gr_loader = GRSheetLoader(gr_sheet_id, gr_gnpr_sheet_name, gr_tv_sheet_name)

        
if __name__ == "__main__":
    # Load the sheet and print the DataFrame
    gr_loader._fetch_sheet(gr_tv_sheet_name)
    gr_loader.set_columns(gr_gnpr_columns)
    from mystock.utility.df.format import print_df
    print_df(gr_loader.dfd[gr_tv_sheet_name])
    dict = gr_loader.fetch_parameters(0)
    print(dict)