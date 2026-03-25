import os
import shutil
import customtkinter as ctk
import ctk_example as ctkeg
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_ALL
from CTkMenuBar import *
from pathlib import Path
import settings
import chooser
import menubar
import filer
import image_handler as img_hdl
import canvas_help
import configure

##########
# initialize
APPNAME = "Naninovel Sprite Assembler"
VERSION = "1.0"
DEVELOPER = "wakanameko"
SRC_DIR = os.path.dirname(__file__)
FONT = "system-ui"
path_setting_ini = Path(SRC_DIR, "setting.ini")

print("####################\n" + APPNAME, "version:", VERSION, "by", DEVELOPER, "\n####################")

##########
# functions
def update_sprite_list():
    # initialize
    for item in app.scrollable_checkbox_frame.get_all_items():
        app.scrollable_checkbox_frame.remove_item(item)
    # load
    sprite_list = filer.get_sprite_list(app)
    for i in range(len(sprite_list)):
        app.label_status.configure(text="[+] スプライト {} の情報を読み込んでいます。".format(sprite_list[i]))
        app.scrollable_checkbox_frame.add_item(sprite_list[i])
    app.label_status.configure(text="[o] スプライト情報を読み込みました。".format(sprite_list[i]))
        
def pipe_dnd(event):
    chooser.choose_with_dnd(event, app)

def setup_widgets():
    # section1 - select input
    app.frame_input = DnDFrame(master=frame_main)
    app.frame_input.pack(fill="x", pady=(5, 10))
    app.frame_input.drop_target_register(DND_ALL)
    app.frame_input.dnd_bind("<<Drop>>", pipe_dnd)
    app.button_dir_from = ctk.CTkButton(master=app.frame_input, text="フォルダを選択", font=(FONT, 14, "normal"), command=lambda:chooser.choose_dir_assets(app))
    app.button_dir_from.pack(side="left", padx=(0, 5))
    app.textbox_dir_from = ctk.CTkEntry(master=app.frame_input, font=(FONT, 14, "normal"), placeholder_text="")
    app.textbox_dir_from.pack(side="left", fill="x", expand=True)
    if app.history_dir_from:
        app.textbox_dir_from.insert(0, app.history_dir_from)
    app.button_open = ctk.CTkButton(master=app.frame_input, text="開く", font=(FONT, 14, "normal"), command=update_sprite_list)
    app.button_open.pack(side="left", padx=(5, 0))
    app.separator2 = ctk.CTkFrame(master=frame_main, height=2, fg_color="gray")
    app.separator2.pack(fill="x", pady=(5, 10))
    # section2 - frame for treeview and image preview
    app.paned = tk.PanedWindow(frame_main, orient="horizontal", sashrelief="raised")
    app.paned.config(bg=app._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]))
    app.paned.pack(fill="both", expand=True)
    # section2 - treeview
    app.frame_tree = ctk.CTkFrame(master=app.paned)
    app.paned.add(app.frame_tree, minsize=200)
    app.scrollable_checkbox_frame = ctkeg.ScrollableCheckBoxFrame(master=app.frame_tree, width=1280,
                                                                command=lambda:img_hdl.update_preview(app),
                                                                item_list=[]
                                                                )
    app.scrollable_checkbox_frame.pack(side="left", fill="both", padx=(5, 5), pady=(5, 5))
    # section3 - image preview
    app.frame_preview = ctk.CTkFrame(master=app.paned)
    app.frame_preview.grid_rowconfigure(0, weight=1)    # ウィンドウサイズに合わせて伸縮
    app.frame_preview.grid_columnconfigure(0, weight=1)
    app.paned.add(app.frame_preview, minsize=200)
    app.canvas_preview = ctk.CTkCanvas(master=app.frame_preview, bg=app._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]), highlightthickness=0)
    app.canvas_preview.grid(row=0, column=0, sticky=ctk.W + ctk.E + ctk.S + ctk.N)
    app.sb_v = ctk.CTkScrollbar(app.frame_preview, orientation=ctk.VERTICAL, command=app.canvas_preview.yview)
    app.sb_h = ctk.CTkScrollbar(app.frame_preview, orientation=ctk.HORIZONTAL, command=app.canvas_preview.xview)
    app.sb_v.grid(row=0, column=1, sticky="ns")
    app.sb_h.grid(row=1, column=0, sticky="ew")
    app.canvas_preview.configure(yscrollcommand=app.sb_v.set, xscrollcommand=app.sb_h.set)  # Scrollbarの動作を適用
    app.canvas_preview.bind("<MouseWheel>", lambda e:canvas_help.canvas_on_mousewheel(app, e))        # wheel (nt, darwin)
    app.canvas_preview.bind("<Button-4>", lambda e:canvas_help.canvas_on_mousewheel(app, e))          # wheel (linux)
    app.canvas_preview.bind("<Button-5>", lambda e:canvas_help.canvas_on_mousewheel(app, e))          # wheel (linux)
    # section4 - status
    app.label_status = ctk.CTkLabel(master=frame_main, height=18, text="[+] ここにステータスメッセージが表示されます。", font=(app.FONT, 10, "normal"), anchor=ctk.NW)
    app.label_status.pack(fill="both", anchor=ctk.N, padx=(5, 5))

def quit_thisAPP(event=None):
    # settings.writeSettingFile(app, path_setting_ini, mode="save")
    app.destroy()
    shutil.rmtree(Path(SRC_DIR, "tmp"), ignore_errors=True)
    os.mkdir(Path(SRC_DIR, "tmp"))
    quit()

class CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
class DnDFrame(ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # define variables
        self.APPNAME = APPNAME
        self.VERSION = VERSION
        self.DEVELOPER = DEVELOPER
        self.FONT = FONT
        settings_array = settings.openSettingFile(ctk, path_setting_ini)
        self.size_window_x = settings_array[0]
        self.size_window_y = settings_array[1]
        self.appearance = settings_array[2]
        self.theme = settings_array[3]
        self.language = settings_array[4]
        self.history_dir_from = settings_array[5]
        self.history_dir_save = settings_array[6]
        # define widgets
        self.textbox_dir_from = ctk.CTkEntry(self)
        self.paned = tk.PanedWindow(self)
        self.scrollable_checkbox_frame = None
        # section3 - image preview
        self.canvas_preview = ctk.CTkCanvas(self)
        # section4 - status
        self.label_status = ctk.CTkLabel(self)

        self.title("{} | version: {}".format(APPNAME, VERSION))
        try:
            self.geometry("{}x{}".format(self.size_window_x, self.size_window_y))
        except TypeError:
            settings.writeSettingFile(ctk, path_setting_ini)
            self.geometry("{}x{}".format(self.size_window_x, self.size_window_y))

# initialize main window
app = App()
# 外観を指定
ctk.set_appearance_mode(app.appearance)  # options: "Light", "Dark", "System"
ctk.set_default_color_theme(app.theme)   # options: "blue", "green", "dark-blue"
# Tkinter のデフォルトフォントを強制変更
ctk.CTkFont._default_font = ctk.CTkFont(FONT)
# process when closed window
app.protocol("WM_DELETE_WINDOW", quit_thisAPP)
# hot keys
app.bind("<Control-w>", quit_thisAPP)
app.bind("<Control-q>", quit_thisAPP)
app.bind("<Control-o>", lambda e:update_sprite_list())
app.bind("<Control-O>", lambda e:chooser.choose_dir_assets(app))
app.bind("<Control-e>", lambda e:img_hdl.export_img(app))
app.bind("<Control-+>", lambda e:img_hdl.preview_scale_change(app, True))
app.bind("<Control-minus>", lambda e:img_hdl.preview_scale_change(app, False))

if "__main__" == __name__:
    # 先にpackしないと下に行く
    menubar.initialize_menubar(app)
    # make frame_main scrollable frame
    frame_main = ctk.CTkFrame(app)
    frame_main.pack(fill="both", expand=True, padx=10, pady=10)
    setup_widgets()
    
app.mainloop()