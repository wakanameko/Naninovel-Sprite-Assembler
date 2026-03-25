from pathlib import Path
import pathlib
from customtkinter import filedialog
import settings
import image_handler as img_hdl

def name_png(parts_list:list):
    output = []
    for i in range(len(parts_list)):
        output.append(parts_list[i][:-6])
    return ", ".join(output)

def choose_dir_assets(instance):
    settings_array = settings.openSettingFile(instance, Path(Path(__file__).parent, "setting.ini"))

    if settings_array[5]:
        initial_dir = settings_array[5]
    else:
        initial_dir = Path(__file__).parent
    open_dir_img = filedialog.askdirectory(title="Assetsフォルダを選択してください。", initialdir=initial_dir)
    if open_dir_img:
        instance.textbox_dir_from.delete(0, "end")
        instance.textbox_dir_from.insert(0, open_dir_img)
        settings.writeSettingFile(instance, Path(Path(__file__).parent, "setting.ini"), mode="save")

def choose_path_png(instance):
    settings_array = settings.openSettingFile(instance, Path(Path(__file__).parent, "setting.ini"))

    if settings_array[6]:
        initial_dir = settings_array[6]
    else:
        initial_dir = Path(__file__).parent
    initial_file = name_png(sorted((instance.scrollable_checkbox_frame.get_checked_items()), key=lambda p: img_hdl.get_sorting_order(p)))  # ファイル名 = 表示中のパーツリストから拡張子を除いたもの
    array_filetypes = [("PNG形式", ".png"), ("その他", ".*")]
    save_path_png = filedialog.asksaveasfilename(title="ファイルの保存先", initialdir=initial_dir, initialfile=initial_file, filetypes=array_filetypes, defaultextension=".png")
    if save_path_png:
        instance.history_dir_save = Path(save_path_png).parent
        settings.writeSettingFile(instance, Path(Path(__file__).parent, "setting.ini"), mode="save")
    return save_path_png

def choose_with_dnd(event, instance):
    settings_array = settings.openSettingFile(instance, Path(Path(__file__).parent, "setting.ini"))
    # サンプルコードの受け売り
    dropped_file = event.data.replace("{","").replace("}", "")
    if dropped_file:
        if event.widget == instance.frame_input:
            instance.textbox_dir_from.delete(0, "end")
            instance.textbox_dir_from.insert(0, dropped_file)
            settings.writeSettingFile(instance, Path(Path(__file__).parent, "setting.ini"), mode="save")