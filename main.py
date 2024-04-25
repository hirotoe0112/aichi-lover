from PIL import Image
import turtle
import pandas
import tkinter.messagebox

marker = turtle.Turtle()
marker.penup()
marker.hideturtle()


# 緯度経度からスクリーン座標に変換する関数
def calc_screen_coord(
    target_lat,
    target_lon,
    lat_min,
    lat_max,
    lon_min,
    lon_max,
    screen_width,
    screen_height,
):
    lat_ratio = screen_height / (lat_max - lat_min)
    lon_ratio = screen_width / (lon_max - lon_min)

    screen_x = screen_width / 2 - (lon_max - target_lon) * lon_ratio
    screen_y = screen_height / 2 - (lat_max - target_lat) * lat_ratio

    return screen_x, screen_y


# 市区町村の位置に文字を表示する関数
def mark_location(row: pandas.Series):
    screen_x, screen_y = calc_screen_coord(
        row["緯度"],
        row["経度"],
        lat_min,
        lat_max,
        lon_min,
        lon_max,
        map_width,
        map_height,
    )

    marker.goto(screen_x, screen_y)
    marker.write(row["市区町村名"], align="center", font=("Arial", 7, "normal"))


# 愛知県の地図ファイル名と表示サイズ
map_file = "map.png"
with Image.open(map_file) as map_img:
    width, height = map_img.size
map_width = width + 5
map_height = height + 5

# Turtleの設定
screen = turtle.Screen()
screen.title("The Road to Aichi Master")
screen.setup(map_width, map_height)
screen.bgpic(map_file)

# ファイル読み込み
boundaries = pandas.read_csv("./data/output/boundary_coordinates.csv")
center_coordinates = pandas.read_csv("./data/output/center_coordinates.csv")

# 境界緯度経度を取得
lat_min = boundaries[boundaries["方角"] == "S"]["緯度"].item()
lat_max = boundaries[boundaries["方角"] == "N"]["緯度"].item()
lon_min = boundaries[boundaries["方角"] == "W"]["経度"].item()
lon_max = boundaries[boundaries["方角"] == "E"]["経度"].item()

is_game_on = True
# ユーザが正解した市区町村名を格納するリスト
correct_answers = []
while is_game_on:
    answer = screen.textinput(
        title="Do you love Aichi?", prompt="市区町村名を当ててください。"
    )

    # キャンセルを押した場合
    if answer is None:
        is_game_on = False
    # 既に答えた市区町村名を入力した場合
    elif answer in correct_answers:
        screen.textinput(
            title=f"You love {answer} too much!",
            prompt="すでに答えた市区町村名です。別の市区町村名を入力してください。",
        )
    # 答えが正しい場合
    elif answer in center_coordinates["市区町村名"].values:
        row = center_coordinates[center_coordinates["市区町村名"] == answer].iloc[0]
        mark_location(row)
        correct_answers.append(answer)

    # 全市区町村を当てた場合
    if len(correct_answers) == len(center_coordinates):
        tkinter.messagebox.showinfo(
            title="Congratulations!",
            message="全市区町村を当てました！愛知県を愛してくれてありがとう！",
        )
        is_game_on = False

# screenを閉じる
screen.bye()

# center_coordinates.apply(mark_location, axis=1)

# turtle.mainloop()
