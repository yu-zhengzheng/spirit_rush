"""LangGraph游戏状态图"""
from langgraph.graph import StateGraph, END
from graph.state import GameState
from graph.nodes import (
    idle_node,
    cultivation_node,
    event_trigger_node,
    event_resolution_node,
    dialogue_init_node,
    dialogue_process_node,
    route_from_idle,
    route_dialogue_continuation,
)


def create_game_graph() -> StateGraph:
    """创建游戏状态图"""
    
    # 创建状态图
    graph = StateGraph(GameState)
    
    # 添加节点
    graph.add_node("idle", idle_node)
    graph.add_node("cultivation", cultivation_node)
    graph.add_node("event_trigger", event_trigger_node)
    graph.add_node("event_resolution", event_resolution_node)
    graph.add_node("dialogue_init", dialogue_init_node)
    graph.add_node("dialogue_process", dialogue_process_node)
    
    # 设置入口
    graph.set_entry_point("idle")
    
    # 从闲置状态的条件路由
    graph.add_conditional_edges(
        "idle",
        route_from_idle,
        {
            "cultivation": "cultivation",
            "event": "event_trigger",
            "dialogue": "dialogue_init",
            "idle": END,
        }
    )
    
    # 修炼完成后返回闲置
    graph.add_edge("cultivation", END)
    
    # 事件流程
    graph.add_edge("event_trigger", "event_resolution")
    graph.add_edge("event_resolution", END)
    
    # 对话流程
    graph.add_edge("dialogue_init", END)  # 初始化后返回，等待用户选择
    graph.add_conditional_edges(
        "dialogue_process",
        route_dialogue_continuation,
        {
            "continue": END,  # 继续对话，返回等待用户输入
            "end": END,  # 结束对话
        }
    )

    return graph


class GameGraphManager:
    """游戏状态图管理器"""
    
    def __init__(self, player, time_system, event_manager, npc_manager):
        self.graph = create_game_graph()
        self.compiled_graph = self.graph.compile()
        mmd_graph = self.compiled_graph.get_graph().draw_mermaid().replace("classDef", "%% classDef")
        with open("graph.mmd", "w") as f:
            f.write(mmd_graph)
        self.current_state: GameState = {
            "player": player,
            "time_system": time_system,
            "event_manager": event_manager,
            "npc_manager": npc_manager,
            "phase": "idle",
            "player_info": {},
            "time_info": {},
            "action": "",
            "action_params": {},
            "action_result": {},
            "message": "",
            "event_type": None,
            "event_data": {},
            "event_options": [],
            "selected_option": None,
            "current_npc": None,
            "npc_info": {},
            "dialogue_history": [],
            "user_input": "",
            "npc_response": "",
            "dialogue_options": [],
            "should_trigger_event": False,
            "breakthrough_occurred": False,
            "dialogue_ended": False,
        }
    
    def update_state_info(self):
        """同步对象信息到快照（用于UI显示）"""
        self.current_state["player_info"] = self.current_state["player"].get_display_info()
        self.current_state["time_info"] = self.current_state["time_system"].to_dict()
    
    def process_action(self, action: str, params: dict = None) -> GameState:
        """处理玩家动作"""
        self.current_state["action"] = action
        self.current_state["action_params"] = params or {}
        
        # 运行状态图
        result = self.compiled_graph.invoke(self.current_state)
        self.current_state = result
        
        # 处理完成后更新快照
        self.update_state_info()
        
        return result
    
    def start_cultivation(self) -> GameState:
        """开始修炼"""
        return self.process_action("cultivate")
    
    def trigger_event(self, event_type: str, event_data: dict = None) -> GameState:
        """触发事件"""
        self.current_state["event_type"] = event_type
        self.current_state["event_data"] = event_data or {}
        return self.process_action("trigger_event")
    
    def resolve_event(self, selected_option: int) -> GameState:
        """解决事件"""
        self.current_state["selected_option"] = selected_option
        # 直接运行event_resolution节点
        result = event_resolution_node(self.current_state)
        self.current_state = result
        return result
    
    def start_dialogue(self, npc_id: str) -> GameState:
        """开始与NPC对话"""
        self.current_state["current_npc"] = npc_id
        return self.process_action("talk_to_npc")
    
    def continue_dialogue(self, user_input: str) -> GameState:
        """继续对话"""
        self.current_state["user_input"] = user_input
        # 直接运行dialogue_process节点
        result = dialogue_process_node(self.current_state)
        self.current_state = result
        return result
    
    def end_dialogue(self):
        """结束对话"""
        self.current_state["phase"] = "idle"
        self.current_state["current_npc"] = None
        self.current_state["dialogue_history"] = []
        self.current_state["dialogue_ended"] = False
    
    def get_state(self) -> GameState:
        """获取当前状态"""
        return self.current_state.copy()
