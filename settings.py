def openSettingFile(instance, path_setting_ini):
    try:
        with open(path_setting_ini, "r", encoding="UTF-8") as file_setting:
            settings = file_setting.read().splitlines()
            print(settings)
            if (len(settings) != 7):
                print("setting.ini が破損しています。")
                writeSettingFile(instance, path_setting_ini)
                openSettingFile(instance, path_setting_ini)
    except FileNotFoundError:
        print("setting.ini が見つかりません。")
        writeSettingFile(instance, path_setting_ini)
        openSettingFile(instance, path_setting_ini)
    except UnicodeDecodeError:
        print("setting.iniの読み込み中にエラーが発生しました。例外: UnicodeDecodeError")
        writeSettingFile(instance, path_setting_ini)
        openSettingFile(instance, path_setting_ini)
    return settings

def writeSettingFile(instance, path_setting_ini, mode="default"):
    if mode == "default":
        with open(path_setting_ini, "w", encoding="UTF-8") as file_setting:
            file_setting.write("580\n420\nsystem\nblue\nJapanese\n\n\n")
        print("setting.ini を初期化しました。")
    if mode == "save":
        with open(path_setting_ini, "w", encoding="UTF-8") as file_setting:
            settings_array_wrote = []
            settings_array_wrote.append(instance.winfo_width())
            settings_array_wrote.append(instance.winfo_height())
            settings_array_wrote.append(instance.appearance)
            settings_array_wrote.append(instance.theme)
            settings_array_wrote.append(instance.language)
            settings_array_wrote.append(instance.textbox_dir_from.get())
            settings_array_wrote.append(instance.history_dir_save)
            for i in range(len(settings_array_wrote)):
                file_setting.write("{}\n".format(settings_array_wrote[i]))
                print("[{:0X}] saved {}".format(i, settings_array_wrote[i]))
    return