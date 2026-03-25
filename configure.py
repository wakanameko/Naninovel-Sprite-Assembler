import customtkinter as ctk
from pathlib import Path
import settings

Appearance_Color = ["blue", "dark-blue", "green", "red", "magenta", "purple", "torquoise"]
Appearance_Theme = ["System", "Light", "Dark"]

def create_popup(instance, kind="config"):
    if kind == "config":
        global popup_config
        popup_config = ctk.CTkToplevel(instance)
        popup_config.geometry('335x265')
        popup_config.title("Settings")
        popup_config.option_add("*font", (instance.FONT, 11, "normal"))
        popup_config.lift()
        popup_config.focus_force()
        popup_config.transient(instance)   # 前面に出す
        popup_config.grab_set()        # メインを操作できなくする
        # Like a Memory compaction
        popup_config.protocol("WM_DELETE_WINDOW", lambda:close_popup(instance=popup_config))
        # Widgets
        popup_config_frame_main = ctk.CTkFrame(popup_config)
        popup_config_frame_main.pack(fill="both", expand=True, padx=10, pady=10)

        popup_config_frame_title = ctk.CTkFrame(master=popup_config_frame_main, height=10)
        popup_config_frame_title.pack(fill="x", expand=True, padx=10, pady=(10,5))
        popup_config_label_title = ctk.CTkLabel(master=popup_config_frame_title, text="Settings", font=(instance.FONT, 11, "normal"))
        popup_config_label_title.pack(side="left", padx=(10,5))

        popup_config_frame_appearance = ctk.CTkFrame(popup_config_frame_main)
        popup_config_frame_appearance.pack(fill="both", expand=True, padx=10, pady=(5,10))
        popup_config_frame_appearance_title = ctk.CTkFrame(popup_config_frame_appearance, corner_radius=0, height=10)
        popup_config_frame_appearance_title.pack(fill="x", expand=True, padx=10, pady=(10,0))
        popup_config_label_appearance = ctk.CTkLabel(master=popup_config_frame_appearance_title, text="Appearance", font=(instance.FONT, 11, "normal"))
        popup_config_label_appearance.pack(side="left", padx=(10,5))
        popup_config_frame_appearance_theme = ctk.CTkFrame(popup_config_frame_appearance, corner_radius=0)
        popup_config_frame_appearance_theme.pack(fill="both", expand=True, padx=10)
        popup_config_label_appearance_theme = ctk.CTkLabel(master=popup_config_frame_appearance_theme, text="Themes:", font=(instance.FONT, 11, "normal"))
        popup_config_label_appearance_theme.pack(side="left", padx=(10,5))
        popup_config_combo_appearance_theme = ctk.CTkComboBox(popup_config_frame_appearance_theme, values=Appearance_Theme)
        popup_config_combo_appearance_theme.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)
        popup_config_frame_appearance_color = ctk.CTkFrame(popup_config_frame_appearance, corner_radius=0)
        popup_config_frame_appearance_color.pack(fill="x", expand=True, padx=10, pady=(0,10))
        popup_config_label_appearance_color = ctk.CTkLabel(master=popup_config_frame_appearance_color, text="Colors:", font=(instance.FONT, 11, "normal"))
        popup_config_label_appearance_color.pack(side="left", padx=(10,5))
        popup_config_combo_appearance_color = ctk.CTkComboBox(popup_config_frame_appearance_color, values=Appearance_Color)
        popup_config_combo_appearance_color.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=10)

        popup_config_button_cancel = ctk.CTkButton(master=popup_config_frame_main, width=60, text="Cancel", font=(instance.FONT, 11, "bold"), command=lambda:close_popup(instance, instance=popup_config))
        popup_config_button_cancel.pack(side="right", padx=(5,10), pady=(5,10))
        popup_config_button_ok = ctk.CTkButton(master=popup_config_frame_main, width=60, text="OK", font=(instance.FONT, 11, "bold"), command=lambda:close_popup(instance, mode="ok", instance=popup_config, kind="config", args = [popup_config_combo_appearance_theme.get(), popup_config_combo_appearance_color.get()]))
        popup_config_button_ok.pack(side="right", padx=(10,5), pady=(5,10))

def close_popup(parent, mode="cancel", instance="", kind="", args=[]):
    instance.destroy()
    if mode == "ok":
        if kind == "config":
            parent.appearance = args[0]
            parent.theme = args[1]
            settings.writeSettingFile(parent, Path(Path(__file__).parent, "setting.ini"), mode="save")
            parent.label_status.configure(text="[o] Restart to apply all changes.")
