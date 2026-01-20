"""存档系统"""
import json
import os
from datetime import datetime
from typing import Optional

SAVE_DIR = "saves"


def ensure_save_dir():
    """确保存档目录存在"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def get_save_files() -> list:
    """获取所有存档文件列表"""
    ensure_save_dir()
    saves = []
    
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SAVE_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saves.append({
                        "filename": filename,
                        "filepath": filepath,
                        "player_name": data.get("player", {}).get("name", "未知"),
                        "realm": data.get("player", {}).get("realm", "练气期"),
                        "save_time": data.get("save_time", "未知时间"),
                        "game_time": data.get("time", {})
                    })
            except (json.JSONDecodeError, IOError):
                continue
    
    # 按保存时间排序
    saves.sort(key=lambda x: x.get("save_time", ""), reverse=True)
    return saves


def save_game(player, time_system, event_manager, slot: int = 1) -> dict:
    """
    保存游戏
    返回: {"success": bool, "message": str, "filepath": str}
    """
    ensure_save_dir()
    
    # 获取当前境界
    realm = player.realm
    
    # 构建存档数据
    save_data = {
        "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player": {
            "name": player.name,
            "realm": realm,
            "cultivation": player.cultivation,
            "spiritual_power": player.spiritual_power,
            "spiritual_power_max": player.spiritual_power_max,
            "health": player.health,
            "health_max": player.health_max,
            "wealth": player.wealth,
            "cultivation_count": player.cultivation_count,
            "buffs": player.buffs,
            "inventory": player.inventory,
        },
        "time": time_system.to_dict(),
        "event_manager": {
            "last_secret_realm_year": event_manager.last_secret_realm_year,
        }
    }
    
    # 生成文件名
    filename = f"save_{slot}.json"
    filepath = os.path.join(SAVE_DIR, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"存档成功！\n存档位置: {filename}",
            "filepath": filepath
        }
    except IOError as e:
        return {
            "success": False,
            "message": f"存档失败: {str(e)}",
            "filepath": ""
        }


def load_game(filepath: str) -> dict:
    """
    读取存档
    返回: {"success": bool, "message": str, "data": dict}
    """
    if not os.path.exists(filepath):
        return {
            "success": False,
            "message": "存档文件不存在！",
            "data": None
        }
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "success": True,
            "message": "读档成功！",
            "data": data
        }
    except (json.JSONDecodeError, IOError) as e:
        return {
            "success": False,
            "message": f"读档失败: {str(e)}",
            "data": None
        }


def delete_save(filepath: str) -> dict:
    """删除存档"""
    if not os.path.exists(filepath):
        return {"success": False, "message": "存档不存在"}
    
    try:
        os.remove(filepath)
        return {"success": True, "message": "存档已删除"}
    except IOError as e:
        return {"success": False, "message": f"删除失败: {str(e)}"}
