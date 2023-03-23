from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from obswebsocket import obsws, requests
from PIL import Image, ImageDraw, ImageFont
from time import sleep
import tkinter as tk
import time

# port番号とパスワード(OBS上で各自設定します)
host = "localhost"
port = 4444
password = "password"
ws = obsws(host, port, password)

OBS_scene = 'scene_test' #OBSのどのシーンに通知を表示するか

path = 'before_like_count.txt'# 0 とだけ入力されたテキストファイル

#OBS上のソース（画像）の表示非表示を切り替える
def changeRender(source, render, scene):
    ws.call(requests.SetSceneItemRender(source, render, scene))

#グリーン背景の上に文字を描画する
def text_maker(text_like_count, text_thanks):
    img = Image.open('gb.jpg')
    imagesize = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("Corporate-Logo-Bold-ver2.ttf", 64)  #フォントを指定、64はサイズでピクセル単位
    size = font.getsize(text_thanks)
    # 文字を画像に描画
    draw.text((imagesize[0] - size[0] - 10, imagesize[1] - size[1] - 200), text_thanks,
              font=font, fill='#FFF', stroke_width=6, stroke_fill='#f300ce', anchor='lm')
    draw.text((imagesize[0] - size[0] - 10, imagesize[1] - size[1] - 200), text_thanks,
              font=font, fill='#f300ce', stroke_width=3, stroke_fill='black', anchor='lm')

    draw.text((imagesize[0] - size[0] - 10, imagesize[1] - size[1] - 200), text_like_count,
              font=font, fill='#FFF', stroke_width=6, stroke_fill='#f300ce', anchor='lm')
    draw.text((imagesize[0] - size[0] - 10, imagesize[1] - size[1] - 200), text_like_count,
              font=font, fill='#FFF', stroke_width=3, stroke_fill='black', anchor='lm')
    #画像ファイルをout.pngという名前で保存※OBS側の機能を使ってクロマキー処理をしてグリーンを抜く
    img.save('out.png', 'PNG', quality=100, optimize=True)


class App:
    def __init__(self, master):
        self.master = master
        self.running = False
        self.build_widgets()

    def build_widgets(self):
        # 入力ボックスの設置
        input_frame = tk.Frame(self.master)
        input_frame.pack(side="top", padx=10, pady=10)
        input_label = tk.Label(input_frame, text="チャンネルID", width=10, anchor="w")
        input_label.pack(side="left")
        self.input_text = tk.Entry(input_frame, width=30)
        self.input_text.pack(side="left")

        # 実行ボタンと停止ボタンの設置
        button_frame = tk.Frame(self.master)
        button_frame.pack(side="top", padx=10, pady=10)
        self.btn_start = tk.Button(button_frame, text="実行", command=self.start)
        self.btn_start.pack(side="left")
        self.btn_stop = tk.Button(button_frame, text="停止", command=self.stop)
        self.btn_stop.pack(side="left")
        self.btn_start.pack(side="left")

    def start(self):
        # OBSと接続
        ws.connect()
        self.running = True
        self.like_notify()

    # ボタンを押したときに実行する関数
    # OBSに接続後、高評価数を表示する
    def like_notify(self):
        if self.running:

            with open(path, 'r') as f:
                before_like_count = f.read()

            YT_channelID = self.input_text.get()
            YT_liveUrl = 'https://www.youtube.com/channel/' + YT_channelID + '/live'
            options = Options()
            options.add_argument('--headless')
            browser = webdriver.Chrome('chromedriver.exe',options=options)
            url = YT_liveUrl
            browser.get(url)
            sleep(3)

            # 高評価数をスクレイピング
            elem_like = browser.find_element_by_xpath(
                '//*[@id="segmented-like-button"]/ytd-toggle-button-renderer/yt-button-shape/button/div[2]/span')
            like_count = elem_like.text

            browser.quit()

            print('前回の高評価は:' + str(before_like_count) + '個です')
            print('今回の高評価は:' + str(like_count) + '個です')

            like_up_count = int(like_count) - int(before_like_count)
            print('増えた高評価は:' + str(like_up_count) + '個です')

            # 高評価数が増えていなければアクションは起こさない
            if like_up_count <= 0:
                pass
            # 高評価数が増えていればプログラム続行
            else:
                #次回チェック時のために高評価の基準数を変更
                with open(path, 'w') as f:
                    f.write(like_count)

                text_thanks = '合計 ' + str(like_count) + ' グッド!感謝します!'  # 「合計○○グッド!感謝します!」という文章を生成
                text_like_count = ' 　　' + str(like_count)  # 画像生成時の位置ずれを補正
                text_maker(text_like_count, text_thanks)

                # OBS上で通知画像を表示オンにし、ライブ放送画面に反映する
                changeRender('like_notify', False, OBS_scene)  # 通知画像をオフ　#前回起動時のオフし忘れに対応するために、まずオフから入る
                changeRender('like_notify', True, OBS_scene)  # 通知画像をオン
                time.sleep(5)  # 5秒オンのまま
                changeRender('like_notify', False, OBS_scene)  # 通知画像をオフ

            self.master.after(20000, self.like_notify)

    #停止ボタンを押したときの挙動（before_like_countの値をリセットする）
    def stop(self):
        with open(path, 'w') as f:
            f.write('0')
        self.running = False


root = tk.Tk()
root.title("高評価通知プログラム")
app = App(root)
root.mainloop()