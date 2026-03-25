import os
from pathlib import Path

DIR_SRC = ""
DIR_TEXTURE = ""
DIR_SPRITE = ""

def open_source(instance):
    global DIR_SRC, DIR_TEXTURE, DIR_SPRITE
    
    dir_from = instance.textbox_dir_from.get()
    if dir_from and os.path.isdir(dir_from):
        DIR_SRC = dir_from
        DIR_TEXTURE = Path(DIR_SRC, "Texture2D")
        DIR_SPRITE = Path(DIR_SRC, "Sprite")
        
        return
    else:
        instance.label_status.configure(text="[x] 有効なフォルダが指定されていません。")
        return None

def get_image_path():
    global DIR_TEXTURE
    ret = None

    if (DIR_TEXTURE != ""):
        for file in os.listdir(DIR_TEXTURE):
            if file.endswith(".png"):
                ret = Path(DIR_TEXTURE, file)
    return ret
    
def get_sprite_list(instance):
    ret = []

    open_source(instance)

    if (DIR_SPRITE != ""):
        for file in os.listdir(DIR_SPRITE):
            if file.endswith(".asset"):
                ret.append(file)
    return ret