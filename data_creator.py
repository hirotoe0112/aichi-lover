import os
import glob
import pandas
from typing import List


def load_and_unify_data(directory: str):
    # ディレクトリ内のCSVファイルを読み込む
    files = glob.glob(os.path.join(directory, "*.csv"))
    # 必要な列のみ取得
    dataframes = [
        pandas.read_csv(file, usecols=["市区町村名", "緯度", "経度"]) for file in files
    ]
    # 各データを統合する
    # ignore_indexをTrueにしないと各ファイルで重複したインデックスが発生してしまいidxmaxなどを使う際に不具合が起きる
    unified_data = pandas.concat(dataframes, ignore_index=True)
    return unified_data


# データを扱いやすい形式にフォーマットする
def format(data: pandas.DataFrame):
    #
    # 名古屋市の各区のデータは名古屋市に統一する
    # ただし北名古屋市はそのままにする
    data.loc[data["市区町村名"].str.contains("^名古屋市"), "市区町村名"] = "名古屋市"
    # 郡は除外する
    # ただし蒲郡市はそのままにする
    data["市区町村名"] = data["市区町村名"].str.replace(
        "(.+?)(?<!蒲)郡", "", regex=True
    )
    return data


# 東西南北端の緯度経度を取得
def get_boundary_coordinates(data: pandas.DataFrame):
    # 緯度が最も北の行を取得
    north = data.loc[data["緯度"].idxmax()].copy()
    north["方角"] = "N"
    # 緯度が最も南の行を取得
    south = data.loc[data["緯度"].idxmin()].copy()
    south["方角"] = "S"
    # 経度が最も東の行を取得
    east = data.loc[data["経度"].idxmax()].copy()
    east["方角"] = "E"
    # 経度が最も西の行を取得
    west = data.loc[data["経度"].idxmin()].copy()
    west["方角"] = "W"
    return pandas.concat([north, south, east, west], axis=1).T


# 各市町村の中心の緯度経度を取得
def get_center_coordinates(data: pandas.DataFrame):
    center_coordinates = (
        data.groupby("市区町村名")[["緯度", "経度"]].mean().reset_index()
    )
    return center_coordinates


# ファイルを読み込みデータを整える
unified_data = load_and_unify_data("./data/input")
formatted_data = format(unified_data)

# 東西南北端を取得
boundaries = get_boundary_coordinates(formatted_data)
print(boundaries)
boundaries.to_csv("./data/output/boundary_coordinates.csv", index=False)

# 各市区町村の中心を取得
center_coordinates = get_center_coordinates(formatted_data)
center_coordinates.to_csv("./data/output/center_coordinates.csv", index=False)
