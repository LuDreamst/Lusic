import pygame
from pathlib import Path
import data
import threading
import time


data_path = Path(__file__).parent / 'data'
img_path = Path(__file__).parent / 'assets'
is_monitoring = [False]  # 是否正在监控播放状态
monitor_thread = [None]  # 监控线程引用


def play_song(song_path=None):
    '''
    播放指定路径的歌曲  
    return: bool, 是否成功播放
    '''
    if song_path is None:
        print("未指定歌曲文件")
        return False
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        print(f"正在播放: {song_path}")
        return True
    except Exception as e:
        print(f"播放失败: {e}")
        return False


def pause_song():
    '''
    暂停当前播放的歌曲  
    如果没有正在播放的歌曲，则不执行任何操作
    '''
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            print("已暂停播放")
        else:
            print("没有正在播放的音乐")
    except Exception as e:
        print(f"暂停失败: {e}")
        
def unpause_song():
    '''
    继续播放当前暂停的歌曲  
    如果没有暂停的歌曲，则不执行任何操作
    '''
    try:
        pygame.mixer.music.unpause()
        print('继续播放')
    except Exception as e:
        print(f"继续播放失败: {e}")

        
def play_song_by_index(index):
    ''' 
    根据索引播放歌曲  
    param index: int, 歌曲索引  
    return: tuple, (song_path, ifsuccess)
    '''
    if 0 <= index < len(data.current_song_list):
        song = data.current_song_list[index]
        data.current_song_index = index
        # play_song返回一个布尔值，表示是否成功播放
        # 如果播放失败，返回False
        # 如果播放成功，返回True
        result = play_song(song["path"])
        if not result:
            print(f"play_song_by_index 无法播放歌曲: {song['path']}")
            return song["path"], False
        else:
            return song["path"], True
    print(f"索引 {index} 超出范围")
    return None, False

def play_next_song():
    ''' 根据当前索引播放下一首歌曲'''
    # global current_song_index
    if data.current_song_index is not None and data.current_song_index + 1 < len(data.current_song_list):
        return play_song_by_index(data.current_song_index + 1)
    return None

def play_prev_song():
    ''' 根据当前索引播放上一首歌曲'''
    # global current_song_index
    if data.current_song_index is not None and data.current_song_index - 1 >= 0:
        return play_song_by_index(data.current_song_index - 1)
    return None

# 监控播放状态的函数

def start_playback_monitor(root, current_song_path, is_paused, on_song_finished):
    '''
    启动播放状态监控  
    param root: tkinter的根窗口对象, 回调参数  
    param current_song_path: 当前播放的歌曲路径列表, 伪全局变量  
    param is_paused: 是否暂停的状态列表，伪全局变量  
    param on_song_finished: 当歌曲播放完毕时调用的回调函数
    '''
    global monitor_thread
    if not is_monitoring[0]:
        is_monitoring[0] = True
        monitor_thread[0] = threading.Thread(
            target=monitor_playback_status, 
            args=(root, current_song_path, is_paused, on_song_finished), 
            daemon=True
        )
        monitor_thread[0].start()
        print("播放状态监控已启动")

def stop_playback_monitor():
    '''停止播放状态监控, 更新 is_monitoring 状态'''
    is_monitoring[0] = False
    # pygame.mixer.quit()
    print("播放状态监控已停止")

def monitor_playback_status(root, current_song_path, is_paused, on_song_finished):
    '''
    监控播放状态的后台线程  
    param root: tkinter的根窗口对象, 回调参数  
    param current_song_path: 当前播放的歌曲路径列表, 伪全局变量  
    param is_paused: 是否暂停的状态列表，伪全局变量  
    param on_song_finished: 当歌曲播放完毕时调用的回调函数
    '''
    import pygame
    was_playing = False  # 用于记录上一次的播放状态
    
    while is_monitoring[0]:
        try:
            # 检查pygame是否已初始化
            if not pygame.mixer.get_init():
                time.sleep(0.1)
                continue
                
            if current_song_path[0] and not is_paused[0]:
                is_busy = pygame.mixer.music.get_busy()
                
                # 如果之前在播放，现在不在播放了，说明歌曲播放完毕
                if was_playing and not is_busy:
                    # 音乐播放完毕，在主线程中更新UI
                    root.after(0, on_song_finished)
                    was_playing = False  # 重置状态
                elif is_busy:
                    was_playing = True  # 正在播放
                    
            else:
                was_playing = False  # 重置状态
        except Exception as e:
            print(f"监控播放状态时出错: {e}")
            
        time.sleep(0.1)  # 每100毫秒检查一次

    
def restart_playback_monitor(root, current_song_path, is_paused, on_song_finished):
    '''
    重启播放状态监控
    param root: tkinter的根窗口对象, 回调参数
    param current_song_path: 当前播放的歌曲路径列表, 伪全局变量
    param is_paused: 是否暂停的状态列表，伪全局变量
    param on_song_finished: 当歌曲播放完毕时调用的回调函数
    '''
    stop_playback_monitor()
    time.sleep(0.1)  # 给线程一点时间停止
    start_playback_monitor(root, current_song_path, is_paused, on_song_finished)