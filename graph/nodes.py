"""LangGraph节点定义"""
import random
from typing import Literal
from graph.state import GameState
from config.settings import NPCS


def idle_node(state: GameState) -> GameState:
    """闲置状态节点"""
    return {
        **state,
        "phase": "idle",
        "message": "等待行动...",
    }


def cultivation_node(state: GameState) -> GameState:
    """修炼节点 - 实际修炼逻辑在外部处理"""
    return {
        **state,
        "phase": "cultivation",
    }


def event_trigger_node(state: GameState) -> GameState:
    """事件触发节点"""
    event_type = state.get("event_type")
    event_data = state.get("event_data", {})
    
    # 根据事件类型设置选项
    options = []
    if event_type == "spiritual_rain":
        options = [{"id": 0, "text": "接受天道馈赠", "action": "accept"}]
    elif event_type == "inner_demon":
        options = [
            {"id": 0, "text": "强行压制 (消耗50灵力)", "action": "suppress"},
            {"id": 1, "text": "寻求师傅帮助", "action": "seek_help"},
            {"id": 2, "text": "放任不管", "action": "ignore"},
        ]
    elif event_type == "secret_realm":
        options = [
            {"id": 0, "text": "进入秘境探索", "action": "enter"},
            {"id": 1, "text": "放弃此次机缘", "action": "skip"},
        ]
    
    return {
        **state,
        "phase": "event",
        "event_options": options,
    }


def event_resolution_node(state: GameState) -> GameState:
    """事件解决节点 - 实际逻辑在外部处理"""
    return {
        **state,
        "phase": "idle",
        "event_type": None,
        "event_data": {},
        "event_options": [],
        "selected_option": None,
    }


def dialogue_init_node(state: GameState) -> GameState:
    """对话初始化节点"""
    npc_id = state.get("current_npc")
    npc_config = NPCS.get(npc_id, {})
    
    # 获取初始对话
    dialogues = npc_config.get("dialogues", ["..."])
    initial_dialogue = random.choice(dialogues)
    
    # 设置对话选项
    if npc_id == "master":
        options = ["请求指点", "询问修炼心得", "告辞"]
    elif npc_id == "merchant":
        options = ["查看商品", "出售物品", "告辞"]
    elif npc_id == "friend":
        options = ["切磋交流", "闲聊", "告辞"]
    else:
        options = ["告辞"]
    
    return {
        **state,
        "phase": "dialogue",
        "npc_info": npc_config,
        "npc_response": initial_dialogue,
        "dialogue_options": options,
        "dialogue_history": [{
            "role": "npc",
            "content": initial_dialogue,
        }],
        "dialogue_ended": False,
    }


def dialogue_process_node(state: GameState) -> GameState:
    """对话处理节点"""
    user_input = state.get("user_input", "")
    npc_id = state.get("current_npc")
    history = state.get("dialogue_history", [])
    
    # 记录玩家选择
    history.append({
        "role": "player",
        "content": user_input,
    })
    
    # 调用LLM占位符生成回复
    response = _generate_npc_response(npc_id, user_input, history)
    
    # 记录NPC回复
    history.append({
        "role": "npc",
        "content": response,
    })
    
    # 检查是否结束对话
    ended = user_input == "告辞"
    
    # 更新选项
    if ended:
        options = []
    else:
        if npc_id == "master":
            options = ["请求指点", "询问修炼心得", "告辞"]
        elif npc_id == "merchant":
            options = ["查看商品", "出售物品", "告辞"]
        elif npc_id == "friend":
            options = ["切磋交流", "闲聊", "告辞"]
        else:
            options = ["告辞"]
    
    return {
        **state,
        "npc_response": response,
        "dialogue_history": history,
        "dialogue_options": options,
        "dialogue_ended": ended,
    }


def _generate_npc_response(npc_id: str, user_input: str, history: list) -> str:
    """
    LLM占位符 - 生成NPC回复
    当前返回模板回复，后续可替换为真实LLM调用
    """
    npc_config = NPCS.get(npc_id, {})
    npc_name = npc_config.get("name", "NPC")
    
    # 模板回复
    if npc_id == "master":
        responses = {
            "请求指点": "修行之道在于悟性，你需多加思考，勤于修炼。记住，道法自然。",
            "询问修炼心得": "修炼需循序渐进，切莫急功近利。心境平和方能事半功倍。",
            "告辞": "去吧，记得常来请安。",
        }
    elif npc_id == "merchant":
        responses = {
            "查看商品": "本店有回灵丹、聚气丹、培元丹，道友请随意选购。",
            "出售物品": "道友想出售什么？本店价格公道。",
            "告辞": "道友慢走，欢迎下次光临。",
        }
    elif npc_id == "friend":
        responses = {
            "切磋交流": "好！那我们就来过两招。不过点到为止，切莫伤了和气。",
            "闲聊": "最近山门内有不少新鲜事，道友可曾听闻？",
            "告辞": "后会有期，道友保重。",
        }
    else:
        responses = {}
    
    return responses.get(user_input, f"{npc_name}微微点头。")


def route_from_idle(state: GameState) -> Literal["cultivation", "event", "dialogue", "idle"]:
    """从闲置状态路由"""
    action = state.get("action", "")
    
    if action == "cultivate":
        return "cultivation"
    elif action == "trigger_event":
        return "event"
    elif action == "talk_to_npc":
        return "dialogue"
    else:
        return "idle"


def route_dialogue_continuation(state: GameState) -> Literal["continue", "end"]:
    """判断对话是否继续"""
    if state.get("dialogue_ended", False):
        return "end"
    return "continue"
