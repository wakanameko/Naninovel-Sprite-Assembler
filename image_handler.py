import PIL
import yaml
import os
import pathlib
import re
import filer
import unit
import chooser
import prefab

IMAGE = None
IS_SEPARATED = False
COMPOSED_IMAGE_ATTR = "_composed_tk_image"
SCALE_RATE = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
SCALE_RATE_IDX = 4

# pyyamlがUnityのタグを無視できないので追加
def unity_tag_ignore(loader, tag_suffix, node):
    return loader.construct_mapping(node)
yaml.add_multi_constructor("!u!", unity_tag_ignore, Loader=yaml.FullLoader)
yaml.add_multi_constructor("tag:unity3d.com,2011:", unity_tag_ignore, Loader=yaml.FullLoader)

def load_image(instance):
    global IMAGE
    try:
        image = PIL.Image.open(filer.get_image_path()).convert("RGBA")
        IMAGE = image
        return image
    except Exception as e:
        print(e)
        instance.label_status.configure(text="[x] 画像の読み込み中にエラーが発生しました。例外: {}".format(e))
        return None

def get_ppu_from_asset(asset_path) -> float:
    """
    .assetファイルから m_PixelsToUnits を読み取ってPPUを返す
    読み取れない場合は unit.calc_ppu() にフォールバック、ゥ
    """
    try:
        with open(asset_path, "r", encoding="utf-8") as f:
            asset = yaml.load(f, Loader=yaml.FullLoader)
            return float(asset['Sprite']['m_PixelsToUnits'])
    except Exception:
        return unit.calc_ppu()

def export_img(instance):
    """ プレビュー中の画像を出力する """
    global SCALE_RATE_IDX

    # 保存前に拡大率を100%に戻す
    scale_rate_idx_escape = SCALE_RATE_IDX
    SCALE_RATE_IDX = 3
    preview_scale_change(instance, True)

    path_save = chooser.choose_path_png(instance)
    if path_save:
        image, (dead, beef) = combine_parts_to_image(
            instance.scrollable_checkbox_frame.get_checked_items())
        image.save(path_save)
        instance.label_status.configure(text="[o] 画像を出力しました。保存先: {}".format(path_save))
    
    # 出力前の拡大率に戻す
    SCALE_RATE_IDX = scale_rate_idx_escape - 1
    preview_scale_change(instance, True)

def separate_img(instance):
    global IMAGE, IS_SEPARATED

    if IMAGE is None:
        if load_image(instance) is None:
            instance.label_status.configure(text="[x] 画像の読み込みに失敗しました。")
            return

    for i in filer.get_sprite_list(instance):
        with open(pathlib.Path(filer.DIR_SPRITE, i), "r", encoding="utf-8") as f:
            asset = yaml.load(f, Loader=yaml.FullLoader)

            crop_pos = {
                "x": asset['Sprite']['m_Rect']['x'],
                "y": IMAGE.height - (asset['Sprite']['m_Rect']['y']
                                     + asset['Sprite']['m_Rect']['height']),
                "w": asset['Sprite']['m_Rect']['x'] + asset['Sprite']['m_Rect']['width'],
                "h": IMAGE.height - asset['Sprite']['m_Rect']['y']
            }

            img_cropped = IMAGE.crop(
                (crop_pos['x'], crop_pos['y'], crop_pos['w'], crop_pos['h']))
            path_out = pathlib.Path(
                pathlib.Path(pathlib.Path(__file__).parent, "tmp"),
                i.replace(".asset", ".png"))
            img_cropped.save(path_out)
            print("Saved: {}".format(path_out))

    instance.label_status.configure(text="[o] スプライトの画像を一時フォルダに保存しました。")
    IS_SEPARATED = True

def name_to_guid(name):
    with open(pathlib.Path(filer.DIR_SPRITE, name + ".meta"),
              "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f)
        return meta['guid']

def preview_scale_change(instance, up: bool):
    global SCALE_RATE_IDX
    if up:
        if SCALE_RATE_IDX < len(SCALE_RATE) - 1:
            SCALE_RATE_IDX += 1
    else:
        if SCALE_RATE_IDX > 0:
            SCALE_RATE_IDX -= 1
    update_preview(instance)

def get_sorting_order(name_parts:str) -> int:
    prefab_path = prefab.find_path()
    _, name_to_sorting_order = prefab.parse(prefab_path)
    # .asset拡張子を除いた名前で検索
    return name_to_sorting_order.get(name_parts[:-6], 0)

def combine_parts_to_image(list_parts):
    if not list_parts:
        return PIL.Image.new("RGBA", (1, 1), (0, 0, 0, 0)), (0, 0)
    
    list_parts_sorted = sorted(list_parts, key=lambda p: get_sorting_order(p))
    print(list_parts_sorted)

    parts_data = []
    min_x_world = float('inf')
    min_y_world = float('inf')
    max_x_world = float('-inf')
    max_y_world = float('-inf')

    first_asset_path = pathlib.Path(filer.DIR_SPRITE, list_parts_sorted[0])
    ppu = get_ppu_from_asset(first_asset_path)

    for part in list_parts_sorted:
        path_img = pathlib.Path(
            pathlib.Path(pathlib.Path(__file__).parent, "tmp"),
            part.replace(".asset", ".png"))

        pos = prefab.get_pos_world_from_guid(name_to_guid(part))
        image = PIL.Image.open(path_img).convert("RGBA")

        center_x = pos['x']
        center_y = pos['y']
        world_w = image.width  / ppu
        world_h = image.height / ppu

        parts_data.append({
            'image':    image,
            'center_x': center_x,
            'center_y': center_y,
            'world_w':  world_w,
            'world_h':  world_h,
        })

        min_x_world = min(min_x_world, center_x - world_w / 2)
        min_y_world = min(min_y_world, center_y - world_h / 2)
        max_x_world = max(max_x_world, center_x + world_w / 2)
        max_y_world = max(max_y_world, center_y + world_h / 2)

    world_width  = max_x_world - min_x_world
    world_height = max_y_world - min_y_world
    combined_width_px  = int(world_width  * ppu)
    combined_height_px = int(world_height * ppu)

    if combined_width_px <= 0 or combined_height_px <= 0:
        return PIL.Image.new("RGBA", (1, 1), (0, 0, 0, 0)), (0, 0)

    combined_img = PIL.Image.new("RGBA", (combined_width_px, combined_height_px),
                                 (0, 0, 0, 0))

    for data in parts_data:
        part_top_left_x_world = data['center_x'] - data['world_w'] / 2
        part_top_left_y_world = data['center_y'] + data['world_h'] / 2

        offset_x_px = int((part_top_left_x_world - min_x_world) * ppu)
        offset_y_px = int((max_y_world - part_top_left_y_world) * ppu)

        # combined_img.paste(data['image'], (offset_x_px, offset_y_px), data['image'])  # Alpha黒くなる
        # fixed:
        tmp = PIL.Image.new("RGBA", combined_img.size, (0, 0, 0, 0))
        tmp.paste(data['image'], (offset_x_px, offset_y_px))
        combined_img = PIL.Image.alpha_composite(combined_img, tmp)

    # リサイズはループ外で1回だけ
    scaled_w = int(combined_width_px  * SCALE_RATE[SCALE_RATE_IDX])
    scaled_h = int(combined_height_px * SCALE_RATE[SCALE_RATE_IDX])
    combined_img = combined_img.resize((scaled_w, scaled_h), PIL.Image.LANCZOS)

    return combined_img, (min_x_world, max_y_world)

def update_preview(instance):
    global IMAGE, IS_SEPARATED

    if IMAGE is None:
        if load_image(instance) is None:
            instance.label_status.configure(text="[x] 画像の読み込みに失敗しました。")
            return

    if not IS_SEPARATED:
        separate_img(instance)

    list_parts = instance.scrollable_checkbox_frame.get_checked_items()
    instance.canvas_preview.delete("all")

    combined_img, (combined_top_left_x, combined_top_left_y) = combine_parts_to_image(list_parts)
    tk_image = PIL.ImageTk.PhotoImage(image=combined_img)
    pos_pixel = unit.to_pixel(combined_top_left_x, combined_top_left_y)
    instance.canvas_preview.create_image(
        pos_pixel['x'], pos_pixel['y'], image=tk_image, anchor="nw")
    # キャンバス内の全てのオブジェクトを囲む矩形を取得
    bbox = instance.canvas_preview.bbox("all")
    # その範囲をスクロール可能領域として設定
    instance.canvas_preview.configure(scrollregion=bbox)

    setattr(instance, COMPOSED_IMAGE_ATTR, tk_image)    # prevent garbage collection