# Lusic: 这是一个超级无敌简陋的纯Python实现的音乐播放器GUI应用
# Lusic: This is a simple music player app implemented in pure Python.
# Author: LuDreamst, github.com/LuDreamst, ludreamst@foxmail.com


import ttkbootstrap as ttk
import play
import data
from data import current_song_path
from PIL import Image, ImageTk
from pathlib import Path
import tkinter.filedialog as fd
import pygame
from translation import translations


data_path = Path(__file__).parent / 'data'
img_path = Path(__file__).parent / 'assets'
# ========= 全局变量 ==========
# 列表是可变变量，以此来实现“伪全局变量”效果。
# current_song_path = [None] # 已迁移至data.py
# current_song_index = None
last_selected_button = [None]

is_paused = [False]
playlist_frames = {}  # 开始为空，由 create_playlist_frame 填充
current_content = [None] # 当前显示的内容框架，列表形式
current_playlist = [None]  # 当前歌单名
song_buttons_map = {} 
playlist_btn_map = {}  # 歌单名 -> 按钮对象

current_language = "zh"  # 默认语言为中文



# ========== 函数区 ==========

# ========== 语言切换相关函数 ==========
def update_ui_language():
    '''更新所有UI元素的语言显示'''
    # 更新侧边栏标签
    start_label.config(text=translations[current_language]["start"])
    playlist_label.config(text=translations[current_language]["playlist"])
    # 更新功能区标签
    start_labelframe.config(text=translations[current_language]["function_area"])
    playlist_labelframe.config(text=translations[current_language]["playlist_area"])
    # 更新按钮文本
    add_playlist_btn.config(text=translations[current_language]["new_playlist"])
    readme_btn.config(text=translations[current_language]["readme"])
    # 更新readme页面内容
    readme_labelframe.config(text=translations[current_language]["readme"])
    welcome_message.config(text=translations[current_language]["welcome_message"])
    description.config(text=translations[current_language]["description"])
    disclaimer.config(text=translations[current_language]["disclaimer"])
    prospect.config(text=translations[current_language]["prospect"])
    # 底部控制栏
    # play_button.config(text=translations[current_language]["play"])
    # pause_button.config(text=translations[current_language]["pause"])
    # next_song_button.config(text=translations[current_language]["next"])
    # prev_song_button.config(text=translations[current_language]["previous"])
    # 可以根据需要更新readme页面的其他文本内容


def switch_to_en():
    '''切换到英文'''
    global current_language
    if current_language != "en":
        current_language = 'en'
        update_ui_language()

def switch_to_zh():
    '''切换到中文'''
    global current_language
    if current_language != "zh":
        current_language = 'zh'
        update_ui_language()
    
def on_language_toggle():
    '''语言切换按钮的回调函数'''
    if language_var.get():
        switch_to_en()
    else:
        switch_to_zh()

def switch_to_play_button():
    '''切换到播放按钮'''
    pause_button.pack_forget()
    play_button.pack(padx=10, pady=10)

def switch_to_pause_button():
    '''切换到暂停按钮'''
    play_button.pack_forget()
    pause_button.pack(padx=10, pady=10)
    
def pause_and_switch():
    '''暂停并切换至播放按钮'''
    play.pause_song()
    is_paused[0] = True
    switch_to_play_button()

def play_and_switch():
    '''播放并切换至暂停按钮'''
    if current_song_path[0]:
        if is_paused[0]:
            # 只有在暂停状态下才允许恢复播放
            play.unpause_song()
            is_paused[0] = False
            switch_to_pause_button()
            # 启动监控
            play.restart_playback_monitor(root, current_song_path, is_paused, on_song_finished)
        else:
            # 如果没有暂停，则不执行任何操作
            print("请双击歌曲按钮开始播放")
    else:
        print("请先双击选择要播放的歌曲")
        
def select_and_change_color(button):
    '''
    选择歌曲并改变按钮颜色，恢复上次选择的按钮颜色  
    param button: 点击的按钮
    '''
    if last_selected_button[0] is not None:
        last_selected_button[0].config(bootstyle='light')
    button.config(bootstyle='secondary-outline')
    last_selected_button[0] = button
    
# ========== 播放控制相关 ==========
def play_prev_and_switch():
    '''
    播放上一首歌曲并切换至暂停按钮  
    播放失败时切换回播放按钮
    '''
    # play_prev_song()调用play_song_by_index()，而play_song_by_index()会更新current_song_path
    path, ifplayed = play.play_prev_song()
    current_song_path[0] = path
    title = current_playlist[0]
    for btn in song_buttons_map.get(title, []):
        if getattr(btn, "song_path", None) == path:
            select_and_change_color(btn)
    if path and ifplayed:
        switch_to_pause_button()
        # 启动监控
        play.restart_playback_monitor(root, current_song_path, is_paused, on_song_finished)
    else:
        print("已经是第一首")
        switch_to_play_button()

def play_next_and_switch():
    '''
    播放下一首歌曲并切换至暂停按钮  
    播放失败时切换回播放按钮
    '''
    # play_next_song()调用play_song_by_index()
    # 而play_song_by_index()会更新current_song_path
    # play_song_by_index()播放失败时返回None
    # play_song_by_index()成功时返回当前播放的歌曲路径
    path, ifplayed = play.play_next_song()
    current_song_path[0] = path
    title = current_playlist[0]
    for btn in song_buttons_map.get(title, []):
        if getattr(btn, "song_path", None) == path:
            select_and_change_color(btn)
    if path and ifplayed:
        switch_to_pause_button()
        # 启动监控
        play.restart_playback_monitor(root, current_song_path, is_paused, on_song_finished)
    else:
        switch_to_play_button()

def show_readme():
    '''显示欢迎页'''
    if current_content[0]:
        current_content[0].pack_forget()
    readme_frame.pack(fill='both', expand=True)
    current_content[0] = readme_frame
    current_playlist[0] = None

def show_content(name):
    '''
    显示指定歌单内容  
    param name: 歌单名称
    '''
    if current_content[0]:
        current_content[0].pack_forget()
    frame = playlist_frames.get(name)
    if frame:
        frame.pack(fill='both', expand=True)
        current_content[0] = frame
        current_playlist[0] = name

def create_playlist_btn(name):
    '''
    创建歌单按钮  
    param name: 歌单名称  
    return btn: 返回创建的按钮对象
    '''
    btn = ttk.Button(playlist_btn_frame, text=name, bootstyle="secondary-outline", width=20)
    btn.pack(fill='x', padx=10, pady=4)
    btn.config(command=lambda: show_content(name))
    playlist_btn_map[name] = btn  # 保存引用
    return btn
        
def create_song_buttons(parent, songs, title=None):
    '''
    创建歌曲列表在content_frame中  
    歌曲以按钮样式展示  
    双击按钮可选择歌曲并播放  
    param parent: 父容器  
    param songs: 歌曲列表，格式为 [{'name': '歌曲名', 'path': '歌曲路径'}, ...]  
    param title: 歌单名称，定位歌曲列表  
    return: 返回创建的按钮列表，未被其他函数使用  
    def on_double_click: 内置函数，双击按钮时触发
    '''
    # 清空原有内容
    for widget in parent.winfo_children():
        widget.destroy()

    button_refs = []
    for song in songs:
        btn = ttk.Button(
            parent,
            text=song["name"],
            bootstyle='light',
            width=30,
            # 移除单击时的播放逻辑，只保留选择和高亮
            command=lambda p=song["path"], b=None, s=select_and_change_color, t=title: data.pick_song(p, b, s, t)
        )
        # 重新绑定command，确保使用正确的按钮引用
        btn.config(command=lambda p=song["path"], b=btn, s=select_and_change_color, t=title: data.pick_song(p, b, s, t))
        btn.song_path = song["path"]

        def on_double_click(event, p=song["path"], b=btn):
            '''
            双击按钮时触发的函数  
            param event: 事件对象, 必须有    
            param p: 歌曲路径  
            param b: 按钮对象  
            '''
            # 双击时选择歌曲并直接播放
            data.pick_song(p, b, select_and_change_color, title)
            try:
                play.pause_song()  # 停止当前播放
            except Exception:
                pass
            # 重置暂停状态
            is_paused[0] = False
            # 播放新歌曲
            result = play.play_song(p)
            if not result:
                switch_to_play_button()
            else:
                switch_to_pause_button()
                # 启动监控
                play.restart_playback_monitor(root, current_song_path, is_paused, on_song_finished)

        btn.bind("<Double-Button-1>", on_double_click)
        btn.pack(fill='x', padx=10)
        button_refs.append(btn)

    if title:
        song_buttons_map[title] = button_refs
    return button_refs

def on_add(playlist_name):
    '''
    添加歌曲到指定歌单  
    param playlist_name: 歌单名称
    '''
    # 根据当前语言设置文件对话框的文本
    title_text = translations[current_language]["select_songs"]
    audio_files_text = translations[current_language]["audio_files"]
    all_files_text = translations[current_language]["all_files"]
    
    # 选择文件
    file_paths = fd.askopenfilenames(
        title=title_text,
        filetypes=[
            (audio_files_text, "*.mp3 *.wav *.flac *.ogg"), 
            (all_files_text, "*.*")
        ]
    )
    if not file_paths:
        return

    # 构造歌曲信息列表
    songs = []
    for path in file_paths:
        song_name = Path(path).stem
        songs.append({"name": song_name, "path": path})

    # 写入 JSON 文件
    data.add_songs_to_json(playlist_name, songs)

    # 重新创建整个播放列表框架
    old_frame = playlist_frames.get(playlist_name)
    if old_frame:
        # 记录当前是否正在显示这个播放列表
        is_currently_showing = (current_content[0] == old_frame)
        
        # 删除旧框架
        old_frame.destroy()
        
        # 重新创建框架
        create_playlist_frame(playlist_name)
        
        # 如果之前正在显示这个播放列表，重新显示它
        if is_currently_showing:
            show_content(playlist_name)

def on_rename(playlist_name, frame):
    '''
    重命名歌单  
    param playlist_name: 当前歌单名称  
    param frame: 当前歌单的框架
    def confirm: 确认重命名  
    def cancel: 取消重命名
    '''
    # 创建重命名弹窗
    dialog = ttk.Toplevel()
    dialog.overrideredirect(True)
    dialog.geometry("300x150")
    dialog.grab_set()

    # 设置弹窗位置为居中
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    dialog_frame1 = ttk.Frame(dialog, bootstyle='primary')
    dialog_frame1.pack(fill='both', expand=True)
    
    dialog_frame2 = ttk.Frame(dialog_frame1)
    dialog_frame2.pack(fill='both', expand=True, padx=3, pady=3)
    
    rename_playlist_label = ttk.Label(dialog_frame2, font=('Noto Serif SC Medium', 16))
    rename_playlist_label.pack(pady=(12, 5))
    rename_playlist_label.config(text=translations[current_language]["rename_playlist"])
    entry = ttk.Entry(dialog_frame2)
    entry.insert(0, playlist_name)
    entry.pack(pady=5)
    
    def confirm():
        new_title = entry.get().strip()
        if not new_title or new_title == playlist_name:
            dialog.destroy()
            return
        data.rename_json(old_name=playlist_name, new_name=new_title)
        # 刷新界面（删除旧按钮，添加新按钮和frame）
        frame.destroy()
        old_btn = playlist_btn_map.pop(playlist_name, None)
        if old_btn:
            old_btn.destroy()
        create_playlist_btn(new_title)
        create_playlist_frame(new_title)
        show_content(new_title)
        dialog.destroy()

    def cancel():
        dialog.destroy()
    
    btn_frame = ttk.Frame(dialog_frame2)
    btn_frame.pack(pady=8)
    confirm_btn = ttk.Button(btn_frame, text="确定", command=confirm, bootstyle='primary')
    confirm_btn.pack(side='left', padx=5)
    confirm_btn.config(text=translations[current_language]["confirm"])
    cancel_btn = ttk.Button(btn_frame, text="取消", command=cancel, bootstyle='secondary')
    cancel_btn.pack(side='left', padx=5)
    cancel_btn.config(text=translations[current_language]["cancel"])

    entry.focus_set()
    entry.select_range(0, 'end')

def on_delete(playlist_name):
    '''
    删除指定歌单  
    param playlist_name: 歌单名称
    '''
    data.delte_json(playlist_name)
    frame = playlist_frames.pop(playlist_name, None)
    if frame:
        frame.destroy()
    btn = playlist_btn_map.pop(playlist_name, None)
    if btn:
        btn.destroy()
    song_buttons_map.pop(playlist_name, None)
    show_readme()

def add_playlist_topbar(frame, playlist_name):
    '''
    添加歌单顶部工具栏  
    param frame: 歌单框架  
    param playlist_name: 歌单名称
    '''
    top_bar = ttk.Frame(frame)
    top_bar.pack(side='top', fill='x')

    # 加载图标
    add_icon = ImageTk.PhotoImage(Image.open(img_path / 'add_icon.png').resize((20, 20), Image.LANCZOS))
    rename_icon = ImageTk.PhotoImage(Image.open(img_path / 'rename.png').resize((20, 20), Image.LANCZOS))
    del_icon = ImageTk.PhotoImage(Image.open(img_path / 'del_icon.png').resize((20, 20), Image.LANCZOS))

    # 添加按钮
    add_button = ttk.Button(top_bar, 
                            image=add_icon, 
                            command=lambda: on_add(playlist_name), 
                            bootstyle='success')
    add_button.image = add_icon
    add_button.pack(side='right', padx=2)

    rename_button = ttk.Button(top_bar, 
                               image=rename_icon, 
                               command=lambda: on_rename(playlist_name, frame), 
                               bootstyle='info')
    rename_button.image = rename_icon
    rename_button.pack(side='right', padx=2)

    del_button = ttk.Button(top_bar, image=del_icon, command=lambda: on_delete(playlist_name), bootstyle='danger')
    del_button.image = del_icon
    del_button.pack(side='right', padx=2)

def create_playlist_frame(name):
    '''
    创建歌单框架  
    param name: 歌单名称
    '''
    frame = ttk.Frame(content_frame)
    add_playlist_topbar(frame, playlist_name=name)

    # --- 滚动区实现 ---
    songs_frame = ttk.Frame(frame)
    songs_frame.pack(fill='both', expand=True)

    canvas = ttk.Canvas(songs_frame, borderwidth=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(songs_frame, 
                              bootstyle='round',
                              orient="vertical", 
                              command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.pack(side="top", fill="both", expand=True)

    # 让canvas和scrollbar紧贴
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 在canvas中创建scrollable_frame窗口
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # 让canvas的scrollregion随内容变化
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_frame_configure)  # 新增：canvas变化也刷新scrollregion

    # 让scrollable_frame宽度随canvas变化
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
        scrollable_frame.config(width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    # 鼠标滚轮支持
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

    songs = data.load_playlist_songs(name)
    create_song_buttons(scrollable_frame, songs, title=name)
    playlist_frames[name] = frame
    
def add_playlist():
    '''
    新建歌单按钮的回调函数  
    def confirm: 确认新建歌单  
    def cancel: 取消新建歌单
    '''
    dialog = ttk.Toplevel()
    dialog.overrideredirect(True)
    dialog.title("新建歌单")
    dialog.geometry("300x150")
    dialog.grab_set()

    # 设置弹窗位置为居中
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    dialog_frame1 = ttk.Frame(dialog, bootstyle='primary')
    dialog_frame1.pack(fill='both', expand=True)
    
    dialog_frame2 = ttk.Frame(dialog_frame1)
    dialog_frame2.pack(fill='both', expand=True, padx=3, pady=3)
    
    new_playlist_label = ttk.Label(dialog_frame2, font=('Noto Serif SC Medium', 16))
    new_playlist_label.pack(pady=(12, 5))
    new_playlist_label.config(text=translations[current_language]["new_playlist_dialog"])
    entry = ttk.Entry(dialog_frame2)
    entry.pack()

    def confirm():
        name = entry.get().strip()
        if name and name not in playlist_frames:
            data.save_playlist_json(name)
            create_playlist_btn(name)
            create_playlist_frame(name)
            show_content(name)
        dialog.destroy()  # 隐藏表单
    
    def cancel():
        dialog.destroy()
    
    btn_frame = ttk.Frame(dialog_frame2)
    btn_frame.pack(pady=8)
    
    btn_frame = ttk.Frame(dialog_frame2)
    btn_frame.pack()
    confirm_btn = ttk.Button(btn_frame, text="确定", command=confirm, bootstyle='primary')
    confirm_btn.pack(side='left', padx=5)
    confirm_btn.config(text=translations[current_language]["confirm"])
    cancel_btn = ttk.Button(btn_frame, text="取消", command=cancel, bootstyle='secondary')
    cancel_btn.pack(side='left', padx=5)
    cancel_btn.config(text=translations[current_language]["cancel"])


def restore_all_playlists():
    '''还原所有歌单按钮和框架'''
    for file in data_path.glob("*.json"):
        title = file.stem
        create_playlist_btn(title)
        create_playlist_frame(title)

def on_song_finished():
    '''歌曲播放完毕时的回调函数'''
    print("歌曲播放完毕")
    switch_to_play_button()
    play.stop_playback_monitor()  # 停止监控
    # 可选：自动播放下一首
    # play_next_and_switch()
    
def on_closing():
    '''程序退出时的清理函数'''
    play.stop_playback_monitor()
    root.destroy()
    
# ========== 主窗口 ==========
style = ttk.Style(theme='minty')
root = style.master
root.title("Lusic")
width_gui, height_gui = 900, 500
width_screen = root.winfo_screenwidth()
height_screen = root.winfo_screenheight()
root.geometry(f'{width_gui}x{height_gui}+{(width_screen-width_gui)//2}+{(height_screen-height_gui)//2}')

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

# ========== 侧边栏 ==========
sidebar = ttk.Frame(main_frame, width=180, style='light.TFrame')
sidebar.pack(side='left', fill='y')
sidebar.pack_propagate(False)

start_label = ttk.Label(sidebar, font=('Noto Serif SC Medium', 13, 'bold'), bootstyle="inverse-primary")
start_label.pack(pady=(18, 10))
start_labelframe = ttk.Labelframe(sidebar, bootstyle="info")
start_labelframe.pack(fill='x',padx=5)
home_btn_frame = ttk.Frame(start_labelframe, style='light.TFrame')
home_btn_frame.pack(fill='x', pady=(0, 10))

add_playlist_btn = ttk.Button(home_btn_frame, bootstyle="outline", width=20, command=add_playlist)
readme_btn = ttk.Button(home_btn_frame, bootstyle="success-outline", width=20, command=show_readme)
readme_btn.pack(fill='x', padx=10, pady=(10, 4))
add_playlist_btn.pack(fill='x', padx=10, pady=(0, 4))

playlist_label = ttk.Label(sidebar, font=('Noto Serif SC Medium', 13, 'bold'), bootstyle="inverse-secondary")
playlist_label.pack(pady=(18, 10))
playlist_labelframe = ttk.Labelframe(sidebar, bootstyle="danger")
playlist_labelframe.pack(fill='x', padx=5)
playlist_btn_frame = ttk.Frame(playlist_labelframe, style='light.TFrame')
playlist_btn_frame.pack(fill='y', expand=True)

sidebar_bottom = ttk.Frame(sidebar, style='light.TFrame')
sidebar_bottom.pack(side='bottom', fill='x')
language_var = ttk.BooleanVar()  # 用于跟踪checkbutton状态

language_checkbutton = ttk.Checkbutton(
    sidebar_bottom, 
    text='EN', 
    variable=language_var,
    bootstyle='round-toggle', 
    command=on_language_toggle
)
language_checkbutton.pack(side='left', padx=5, pady=5)


# ========== 主内容区 ==========
content_frame = ttk.Frame(main_frame)
content_frame.pack(side='left', fill='both', expand=True)

# ========== readme内容页 ==========
readme_frame = ttk.Frame(content_frame)
readme_labelframe = ttk.Labelframe(readme_frame, bootstyle='success')
readme_labelframe.pack(fill='both', expand=True, padx=10)
welcome_message = ttk.Label(readme_labelframe, font=('Noto Serif SC Medium', 11))
welcome_message.pack(pady=(120,20))
description = ttk.Label(readme_labelframe, font=('Noto Serif SC Medium', 11))
description.pack()
disclaimer = ttk.Label(readme_labelframe, font=('Noto Serif SC Medium', 11))
disclaimer.pack(pady=20)
prospect = ttk.Label(readme_labelframe, font=('Noto Serif SC Medium', 11))
prospect.pack()
readme_frame.pack(fill='both', expand=True)

# ========== 播放控制条（示例） ==========
control_bar = ttk.Frame(root)
control_bar.pack(side='bottom', fill='x')

control_bar_left = ttk.Frame(control_bar)
control_bar_center = ttk.Frame(control_bar)
control_bar_right = ttk.Frame(control_bar)

control_bar_left.pack(side='left', fill='both', expand=True)
control_bar_center.pack(side='left', fill='both', expand=True)
control_bar_right.pack(side='left', fill='both', expand=True)

prev_song_btn_frame = ttk.Frame(control_bar_center)
play_btn_frame = ttk.Frame(control_bar_center)
next_song_btn_frame = ttk.Frame(control_bar_center)
prev_song_btn_frame.pack(side='left',fill='both',expand=True)
play_btn_frame.pack(side='left',fill='both',expand=True)
next_song_btn_frame.pack(side='left',fill='both',expand=True)

prev_song_button = ttk.Button(prev_song_btn_frame, text="⏮", width=4, command=play_prev_and_switch)
prev_song_button.pack(side='right', padx=10, pady=10)

play_button = ttk.Button(play_btn_frame, text="▶", width=4, command=play_and_switch)
play_button.pack(padx=10, pady=10)

pause_button = ttk.Button(play_btn_frame, text="⏸", width=4, bootstyle='secondary', command=pause_and_switch)

next_song_button = ttk.Button(next_song_btn_frame, text="⏭", width=4, command=play_next_and_switch)
next_song_button.pack(side='left', padx=10, pady=10)


if __name__ == "__main__":
    current_content[0] = readme_frame
    restore_all_playlists()
    pygame.mixer.init()  # 初始化pygame的音频模块
    update_ui_language()
    # root.protocol() 需要的是一个函数对象
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()