"""存档系统"""
import json
import os
from datetime import datetime
from typing import Optional

from config.settings import SAVE_DIR


def ensure_save_dir():
    """确保存档目录存在"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def get_save_files() -> dict:
    """获取所有存档文件列表"""
    ensure_save_dir()
    saves = {}
    
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SAVE_DIR, filename)
            try:
                # 从文件名提取槽位号
                slot = int(filename.replace("save_", "").replace(".json", ""))
                
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saves[slot] = {
                        "filename": filename,
                        "filepath": filepath,
                        "save_time": data.get("save_time", "未知"),
                        "game_time": data["state"].get("game_time", {}),
                        "data": data  # 包含完整的存档数据
                    }
            except (ValueError, json.JSONDecodeError, IOError):
                continue
    
    return saves


def save_game(state, slot: int = 1) -> dict:
    """
    保存游戏
    返回: {"success": bool, "message": str, "filepath": str}
    """
    ensure_save_dir()
    
    # 构建存档数据
    save_data = {
        "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state": state,
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