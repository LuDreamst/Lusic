import json
from pathlib import Path


current_song_list = []
current_song_index = [None]
current_song_path = [None]
data_path = Path(__file__).parent / 'data'


def add_songs_to_json(playlist_name, songs):
    '''
    将歌曲列表添加到指定的播放列表JSON文件中  
    param playlist_name: str, 播放列表名称  
    param songs: list, 包含歌曲信息的字典列表，每个字典应包含 "title" 和 "path" 键
    '''
    file = data_path / f"{playlist_name}.json"
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"songs": []}

    # 去重：只添加新歌
    existing_paths = {song["path"] for song in data["songs"]}
    for song in songs:
        if song["path"] not in existing_paths:
            data["songs"].append(song)
            existing_paths.add(song["path"])  # 防止本次批量中有重复

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    

def rename_json(old_name, new_name):
    '''
    重命名指定的播放列表JSON文件  
    param old_name: str, 旧的播放列表名称  
    param new_name: str, 新的播放列表名称
    '''
    old_file = data_path / f"{old_name}.json"
    new_file = data_path / f"{new_name}.json"
    if old_file.exists():
        old_file.rename(new_file)
        print(f"重命名成功: {old_name} -> {new_name}")
    else:
        print(f"文件不存在: {old_file}")

def delte_json(title):
    '''
    删除指定的播放列表JSON文件  
    param title: str, 播放列表名称
    '''
    playlist_file = data_path / f"{title}.json"
    if playlist_file.exists():
        playlist_file.unlink()
    else:
        print(f"未找到要删除的播放列表文件: {playlist_file}")

# 保存信息到本地
def save_playlist_json(title):
    '''
    保存数据至指定的播放列表JSON文件  
    param title: str, 播放列表名称
    '''    
    playlist_file = data_path / f"{title}.json"
    if not playlist_file.exists():
        data_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        with open(playlist_file, "w", encoding="utf-8") as f:
            json.dump({"songs": []}, f, ensure_ascii=False, indent=2)
    else:
        print(f"已存在播放列表文件: {playlist_file}")

def load_playlist_songs(title):
    '''
    从指定的播放列表JSON文件中加载歌曲列表
    param title: str, 播放列表名称
    return list: 包含歌曲名单的列表
    '''
    playlist_file = data_path / f"{title}.json"
    if playlist_file.exists():
        with open(playlist_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("songs", [])
    return []


def get_current_song_index_by_path(song_path):
    '''
    根据歌曲路径获取当前歌曲的索引  
    param song_path: str, 歌曲文件路径
    return idx: int, 当前歌曲的索引
    '''
    global current_song_list, current_song_index
    for idx, song in enumerate(current_song_list):
        if song["path"] == song_path:
            current_song_index = idx
            print(f"当前歌曲索引: {current_song_index}")
            return idx

    
def pick_song(song_path, button, select_and_change_color, title):
    '''
    选中歌曲并更新当前歌曲路径
    param song_path: str, 歌曲文件路径
    param button: tkinter按钮对象, 用于更新UI状态
    param select_and_change_color: 函数，用于更新按钮颜色
    param title: str, 播放列表名称
    return current_song_path: list, 包含当前歌曲路径的列表
    '''
    global current_song_path
    current_song_path[0] = song_path
    # 更新歌曲列表和索引
    get_current_song_list_by_title(title)
    get_current_song_index_by_path(song_path)
    select_and_change_color(button)
    print(f"已选择歌曲: {song_path}")
    return current_song_path
    
def get_current_song_list_by_title(title):
    '''
    根据播放列表标题获取当前歌曲列表  
    param title: str, 播放列表名称
    return current_song_list: list, 包含当前播放列表的歌曲信息
    '''
    global current_song_list
    current_song_list = load_playlist_songs(title)
    return current_song_list
    
                                