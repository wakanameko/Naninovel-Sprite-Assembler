import webbrowser
from CTkMenuBar import *
import chooser
import image_handler as img_hdl
import configure

FONT = "system-ui"

def initialize_menubar(instance):
    menu = CTkMenuBar(instance)

    # buttons
    menu_button_file = menu.add_cascade("ファイル", font=(FONT, 12, "normal"))
    menu_button_view = menu.add_cascade("表示", font=(FONT, 12, "normal"))
    menu_button_config = menu.add_cascade("設定", font=(FONT, 12, "normal"))
    menu_button_about = menu.add_cascade("ヘルプ", font=(FONT, 12, "normal"))
    
    # drops
    # file
    drop_file = CustomDropdownMenu(widget=menu_button_file)
    drop_sub_open = drop_file.add_submenu("入力元")
    drop_sub_open.add_option(option="フォルダ", command=lambda:chooser.choose_dir_assets(instance))
    drop_file.add_option(option="出力 (Ctrl+E)", command=lambda:img_hdl.export_img(instance))
    drop_file.add_separator()
    drop_file.add_option(option="終了 (Ctrl+(W, Q))", command=lambda:quit())

    # view
    drop_view = CustomDropdownMenu(widget=menu_button_view)
    drop_view.add_option(option="拡大 (Ctrl+Plus)", command=lambda:img_hdl.preview_scale_change(instance, True))
    drop_view.add_option(option="縮小 (Ctrl+Minus)", command=lambda:img_hdl.preview_scale_change(instance, False))

    # config
    drop_edit = CustomDropdownMenu(widget=menu_button_config)
    drop_edit.add_option(option="設定 (Ctrl+P)", command=lambda:configure.create_popup(instance))

    # about
    drop_about = CustomDropdownMenu(widget=menu_button_about)
    drop_about.add_option(option="バージョン: {}".format(instance.VERSION))
    drop_about.add_option(option="開発者: {}".format(instance.DEVELOPER))
    drop_about.add_option(option="最新のリリースを確認", command=lambda:webbrowser.open(""))