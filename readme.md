# Lusic
This is a simple music player app implemented in pure Python.  
这是一个超级无敌简陋的音乐播放器，完全由Python实现  
## Screenshots/截图 
**1**  
   <img width="1127" height="665" alt="image" src="https://github.com/user-attachments/assets/3c7b69e9-2c43-42eb-83ed-27473906589c" />
**2**  
   <img width="1127" height="665" alt="image" src="https://github.com/user-attachments/assets/e39aca83-5a0c-4dc2-b374-1420f7584c7e" />

## How to use/使用方法
**build manually/手动编译**
1. clone or download this project to local.  
   克隆或下载此工程至本地
2. open your terminal and cd to the path where gui.py is located. (The order can also be reversed.)  
   打开终端并cd到gui.py所在路径（顺序颠倒亦可）
3. run this command:  
   运行如下命令：
   `pyinstaller --windowed --name "Lusic" --add-data "assets;assets" --hidden-import pygame --hidden-import PIL --hidden-import ttkbootstrap gui.py`  
(P.S. Confirm that related dependencies have been installed, such as `pyinstaller`, `ttkbootstrap` and `pygame`. )  
确保相关依赖已安装
1. Then you will find the app in the dist folder, if everything goes well.  
   然后你就能在dist文件夹里找到app（如果一切顺利的话）

**Releases**  
Or check the Releases page. 
或者查看发行页

## The End/写在最后
Limited capabilities, please be understanding.  水平有限, 还请包涵 🤝  
Hope you enjoy this! 希望你喜欢! 😄  
