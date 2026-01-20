"""LangGraph状态定义"""
from typing import TypedDict, List, Optional, Any
from core.player import Player
from core.time_system import TimeSystem
from events.special_events import EventManager
from npc.npcs import NPCManager


class GameState(TypedDict, total=False):
    """游戏状态结构"""
    # 核心系统对象
    player: Player
    time_system: TimeSystem
    event_manager: EventManager
    npc_manager: NPCManager

    # 游戏阶段: idle, cultivation, event, dialogue
    phase: str
    
    # 玩家信息快照
    player_info: dict
    
    # 时间信息
    time_info: dict
    
    # 当前动作
    action: str
    action_params: dict
    
    # 动作结果
    action_result: dict
    message: str
    
    # 事件相关
    event_type: Optional[str]
    event_data: dict
    event_options: List[dict]
    selected_option: Optional[int]
    
    # NPC对话相关
    current_npc: Optional[str]
    npc_info: dict
    dialogue_history: List[dict]
    user_input: str
    npc_response: str
    dialogue_options: List[str]
    
    # 标记
    should_trigger_event: bool
    breakthrough_occurred: bool
    dialogue_ended: bool
