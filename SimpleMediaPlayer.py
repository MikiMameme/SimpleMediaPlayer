import tkinter as tk
from tkinter import filedialog
import vlc
import os
from threading import Thread
import time

class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("シンプルメディアプレーヤー by神酒まめ")

        # VLCプレイヤーインスタンス（ハードウェアデコード無効化）
        self.instance = vlc.Instance('--avcodec-hw=none')
        self.player = self.instance.media_player_new()
        self.current_file = None
        self.updating = False

        # 再生用変数
        self.playlist = []
        self.current_index = 0

        # GUI作成
        self.create_widgets()
        self.update_thread = Thread(target=self.update_position)
        self.update_thread.daemon = True
        self.update_thread.start()

    def create_widgets(self):
        # 曲名表示
        self.label = tk.Label(self.root, text="再生するファイルを選択")
        self.label.pack(pady=5)

        # 再生ボタン
        frame_btn = tk.Frame(self.root)
        frame_btn.pack(pady=5)
        tk.Button(frame_btn, text="再生", command=self.play).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="一時停止", command=self.pause).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="停止", command=self.stop).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="ファイル選択", command=self.open_file).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="フォルダ選択", command=self.open_folder).pack(side=tk.LEFT, padx=2)

        # 音量スライダー
        self.volume = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, label="音量", command=self.set_volume)
        self.volume.set(80)
        self.volume.pack(pady=5)

        # シークバー
        self.scale = tk.Scale(self.root, from_=0, to=1000, orient=tk.HORIZONTAL, length=400, command=self.seek)
        self.scale.pack(pady=5)

        # プレイリスト表示
        self.listbox = tk.Listbox(self.root, width=50)
        self.listbox.pack(pady=5)
        self.listbox.bind("<Double-Button-1>", self.play_selected)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("メディアファイル", "*.mp3 *.wav *.mp4 *.avi *.mkv")])
        if path:
            self.playlist = [path]
            self.current_index = 0
            self.update_playlist_gui()
            self.load_and_play(self.current_index)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            exts = (".mp3", ".wav")
            self.playlist = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
            self.playlist.sort()
            self.current_index = 0
            self.update_playlist_gui()
            if self.playlist:
                self.load_and_play(self.current_index)

    def update_playlist_gui(self):
        self.listbox.delete(0, tk.END)
        for f in self.playlist:
            self.listbox.insert(tk.END, os.path.basename(f))

    def play_selected(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.current_index = sel[0]
            self.load_and_play(self.current_index)

    def load_and_play(self, index):
        path = self.playlist[index]
        self.current_file = path
        self.label.config(text=os.path.basename(path))
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.updating = True
        # 終了イベントで次の曲へ
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.next_track)

    def next_track(self, event=None):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self.load_and_play(self.current_index)
        else:
            self.updating = False
            self.scale.set(0)

    def play(self):
        if self.current_file:
            self.player.play()
            self.updating = True

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
        self.updating = False
        self.scale.set(0)

    def set_volume(self, val):
        self.player.audio_set_volume(int(val))

    def seek(self, val):
        if self.player.get_length() > 0:
            pos = int(val) / 1000.0
            self.player.set_position(pos)

    def update_position(self):
        while True:
            if self.updating and self.player.get_length() > 0:
                pos = self.player.get_position() * 1000
                self.scale.set(int(pos))
            time.sleep(0.2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaPlayer(root)
    root.mainloop()
