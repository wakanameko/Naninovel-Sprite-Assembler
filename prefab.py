import pathlib
import re
import yaml
import filer
from os import listdir

cache = {}   # prefabパス → (transforms, tr_to_name, name_to_tr)

# pyyamlがUnityのタグを無視できないので追加
def unity_tag_ignore(loader, tag_suffix, node):
    return loader.construct_mapping(node)
yaml.add_multi_constructor("!u!", unity_tag_ignore, Loader=yaml.FullLoader)
yaml.add_multi_constructor("tag:unity3d.com,2011:", unity_tag_ignore, Loader=yaml.FullLoader)

def parse(path: str):
    """
    .prefabをパースしてTransform階層情報を返す

    Returns:
        transforms : {fileID: {pos, father, go_id, children}}
        tr_to_name : {fileID: GameObject名}
        name_to_tr : {GameObject名: fileID}
    """
    if path in cache:
        return cache[path]

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r'(?=--- !u!)', content)

    transforms = {}
    gameobjects = {}
    name_to_sorting_order = {} # GameObject → SortingOrder

    for block in blocks:
        # GameObject → 名前
        go_match = re.match(r'--- !u!1 &(\d+)', block)
        if go_match:
            fid = go_match.group(1)
            name_match = re.search(r'm_Name: (.+)', block)
            if name_match:
                gameobjects[fid] = name_match.group(1).strip()

        # Transform to tree的な
        tr_match = re.match(r'--- !u!4 &(\d+)', block)
        if tr_match:
            fid = tr_match.group(1)
            pos_match = re.search(
                r'm_LocalPosition: \{x: ([^,]+), y: ([^,]+), z: ([^}]+)\}', block)
            father_match = re.search(r'm_Father: \{fileID: (\d+)\}', block)
            go_match2 = re.search(r'm_GameObject: \{fileID: (\d+)\}', block)
            children_section = re.search(
                r'm_Children:(.*?)m_Father:', block, re.DOTALL)
            children = re.findall(r'\{fileID: (\d+)\}',
                                  children_section.group(1)) if children_section else []

            transforms[fid] = {
                'pos':      (float(pos_match.group(1)),
                             float(pos_match.group(2))) if pos_match else (0.0, 0.0),
                'father':   father_match.group(1) if father_match else None,
                'go_id':    go_match2.group(1) if go_match2 else None,
                'children': children,
            }
 
        # --- !u!212 : SpriteRenderer → m_SortingOrder
        sr_match = re.match(r'--- !u!212 &(\d+)', block)
        if sr_match:
            go_match3 = re.search(r'm_GameObject: \{fileID: (\d+)\}', block)
            order_match = re.search(r'm_SortingOrder: (-?\d+)', block)
            if go_match3 and order_match:
                go_id = go_match3.group(1)
                name = gameobjects.get(go_id, "")
                if name:
                    name_to_sorting_order[name] = int(order_match.group(1))
 
    result = (transforms, name_to_sorting_order)
    cache[path] = result
    return result

def find_path() -> str:
    """Prefabファイルのパスを探す
    
    Returns:
        Str Path of a Prefab file 
    """
    dir_prefab = pathlib.Path(filer.DIR_SRC, "#WitchTrials", "Prefabs",
                               "Naninovel", "Characters", "LayeredCharacters")
    for file in listdir(dir_prefab):
        if file.endswith(".prefab"):
            return str(pathlib.Path(dir_prefab, file))
    raise FileNotFoundError("Prefabファイルが見つかりません: " + str(dir_prefab))

def get_pos_world(tr_fid: str, transforms: dict) -> tuple:
    """
    Transform fileID -> ワールド座標
    
    座標 = オフセット座標 + 親の座標
    """
    data = transforms[tr_fid]
    lx, ly = data['pos']
    father = data['father']
    if father and father != '0' and father in transforms:
        px, py = get_pos_world(father, transforms)
        return (lx + px, ly + py)
    return (lx, ly)

def get_pos_world_from_guid(guid: str) -> dict:
    """ GUID -> ワールド座標 """
    prefab_path = find_path()
    transforms, _ = parse(prefab_path)

    with open(prefab_path, "r", encoding="utf-8") as f:
        contents = f.read()

    idx = contents.find(guid)
    if idx == -1:
        raise ValueError("GUID {} がPrefab内に見つかりません".format(guid))

    # GUID直前の "--- !u!4 &XXXXX" が Transform に対応
    segment = contents[:idx]
    block_starts = [(m.start(), m.group(1))
                    for m in re.finditer(r'--- !u!4 &(\d+)', segment)]
    if not block_starts:
        raise ValueError("GUID {} に対応するTransformブロックが見つかりません".format(guid))

    _, tr_fid = block_starts[-1]

    wx, wy = get_pos_world(tr_fid, transforms)
    return {"x": wx, "y": wy, "z": 0.0}

def name_to_guid(name):
    with open(pathlib.Path(filer.DIR_SPRITE, name + ".meta"),
              "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f)
        return meta['guid']