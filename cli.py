"""仙宗 - 修仙模拟器 命令行版本"""
import random
import os
from core.game_state import GameState
from events.special_events import EventManager
from core.save_system import save_game, load_game, get_save_files
from config.settings import *



def LLM_invoke(message,tools=None):
    payload = json.dumps({
        "model": CHEAP_MODEL_ID,
        "stream": False,
        "messages": message,
        "tools": tools,
        "stream_options": {
            "include_usage": True
        }
    })if tools else json.dumps({
        "model": CHEAP_MODEL_ID,
        "stream": False,
        "messages": message,
        "stream_options": {
            "include_usage": True
        }
    })
    # start_time = datetime.datetime.now()

    CONNECTION.request("POST", "/api/v1/chat/completions", payload, HEADERS)
    res = CONNECTION.getresponse()
    obj = json.loads(res.read().decode('utf-8'))
    # elapsed_time = datetime.datetime.now()-start_time
    # log(obj)
    # print("-"*100,f"\nexecuted in {elapsed_time.total_seconds():.4f} seconds")
    # print("usage:",obj["usage"])
    try:
        content=obj["choices"][0]["message"]["content"]
    except:
        print("msg=",message)
        print("obj=",obj)
        content="胜算云API错误"
    return content

#test
# msg=[{"role": "user", "content": "你谁啊"}];print(LLM_invoke(msg))

# exit()

class GameCLI:
    """游戏命令行类"""
    
    def __init__(self):
        self.state = GameState()
        self.event_manager = EventManager()

    def run_turn(self):
        """

        玩家返回主菜单时return True
        """
        self.state.game_time+=1
        self._start_turn()

        # 玩家操作阶段
        while True:
            print("\n【操作菜单】")
            print("1. 弟子管理")
            print("2. 宗门建设")
            print("5. 存档/读档")
            print("9. 结束回合")
            print("0. 返回主菜单")

            choice = input("\n请选择操作: ").strip()

            if choice == "1":
                self._manage_disciples()
                self.display_status()
            elif choice == "2":
                self._manage_sect()
                self.display_status()
            elif choice == "5":
                self._handle_save_load()
                self.display_status()
            elif choice == "9":
                self._end_player_turn()
                break
            elif choice == "0":
                return True
            else:
                self.state.log("无效输入。")
        return False

    def display_status(self):
        """显示玩家当前状态"""
        os.system("cls")
        print(f"\n --- 第 {self.state.game_time} 年 ---")
        # print(self.state.sect_data)
        print("="*50)
        print(f"【财富】 灵石: {self.state.sect_data['wealth']}/{self.state.max_wealth}")
        print(f"【弟子】 总数: {self.state.sect_data['disciples_total']}/{self.state.max_disciples} | 空闲: {self.state.idle_disciples}")
        print(f"【分配】 挖矿: {self.state.sect_data['disciples_mining']} | 招募: {self.state.sect_data['disciples_recruiting']}")
        print("="*50)
        # 显示日志消息
        if self.state.logs:
            print("\n【最近日志】")
            for log_msg in self.state.logs[-10:]:  # 只显示最近5条日志
                print(f"  {log_msg}")

    def _start_turn(self):
        """开始新回合"""
        self.display_status()
        
        # 1. 回合开始 --> LLM生成随机事件
        event = self.event_manager.check_events(
            self.state,
            False # 回合开始触发
        )

        if event:
            self._handle_event(event)

    def _handle_event(self, event: dict):
        """处理事件"""
        print(f"\n【事件：{event['title']}】")
        print(event['description'])
        print("\n请选择：")
        for i, opt in enumerate(event['options']):
            print(f"{i}. {opt['text']}")
            
        while True:
            choice = input("\n输入选项编号: ").strip()
            if choice.isdigit() and 0 <= int(choice) < len(event['options']):
                option_id = int(choice)
                break
            print("无效输入，请重新输入。")
            
        result = self.event_manager.resolve_event(
            event,
            option_id,
            self.state
        )
        print(f"\n[结果] {result['message']}")
        self.state.log(f"事件结果: {result['message']}")
        
        if result.get("trigger_dialogue"):
            self._start_dialogue(result["trigger_dialogue"])

    def _manage_disciples(self):
        """弟子管理"""
        while True:
            print(f"\n【弟子管理】 总数: {self.state.sect_data['disciples_total']} | 空闲: {self.state.idle_disciples}")
            print(f"1. 派遣至 挖矿 (当前: {self.state.sect_data['disciples_mining']})")
            print(f"2. 派遣至 招募 (当前: {self.state.sect_data['disciples_recruiting']})")
            print(f"3. 召回 挖矿弟子")
            print(f"4. 召回 招募弟子")
            print(f"0. 返回")
            
            choice = input("\n选择操作: ").strip()
            if choice == "0": break
            
            if choice in ["1", "2"]:
                amount = input("输入派遣人数: ").strip()
                if not amount.isdigit(): continue
                amount = int(amount)
                task = "mining" if choice == "1" else "recruiting"
                if self.state.idle_disciples >= amount:
                    self.state.sect_data[f"disciples_{task}"] += amount
                    msg = "挖矿" if task == "mining" else "招募"
                    self.state.log(f"成功派遣 {amount} 名弟子去{msg}。")
                else:
                    self.state.log("没有足够的空闲弟子！")
            elif choice in ["3", "4"]:
                task = "mining" if choice == "3" else "recruiting"
                amount = input("输入召回人数: ").strip()
                if not amount.isdigit(): continue
                amount = int(amount)
                current = self.state.sect_data[f"disciples_{task}"]
                if current >= amount:
                    self.state.sect_data[f"disciples_{task}"] -= amount
                    msg = "挖矿" if task == "mining" else "招募"
                    self.display_status()
                    self.state.log(f"成功召回 {amount} 名去{msg}的弟子。")
                else:
                    self.state.log("没有这么多正在工作的弟子！")

    def _manage_sect(self):
        """宗门管理"""
        while True:
            # info = self.game_state.get_display_info()
            print(f"\n【宗门管理】 财富: {self.state.sect_data['wealth']} 灵石")
            print(f"1. 扩建灵库 (当前上限: {self.state.max_wealth}) - 消耗 10 灵石")
            print(f"2. 扩建洞府 (当前上限: {self.state.max_disciples}) - 消耗 10 灵石")
            print(f"0. 返回")
            
            choice = input("\n选择操作: ").strip()
            if choice == "0": break
            
            if choice in ["1", "2"]:
                cost = 10
                if self.state.sect_data['wealth'] >= cost:
                    self.state.sect_data['wealth'] -= cost
                    if choice == "1":
                        self.state.sect_data["vault_level"] += 1
                        self.display_status()
                        self.state.log("灵库扩建成功！上限+100")
                    else:
                        self.state.sect_data["cave_level"] += 1
                        self.state.log("洞府扩建成功！上限+5")
                else:
                    self.state.log(f"灵石不足，扩建需要 {cost} 灵石。")

    def _end_player_turn(self):
        """结束回合"""
        print("\n回合结束，结算中...")
        
        # 1. 模拟弟子工作产出
        # 挖矿产出
        mining_gain = self.state.sect_data["disciples_mining"] * 2
        if mining_gain > 0:
            self.state.gain_wealth(mining_gain)
            self.state.log(f"弟子挖矿产出: {mining_gain} 灵石")

        # 招募产出
        recruiting_disciples = self.state.sect_data["disciples_recruiting"]
        if recruiting_disciples > 0:
            new_disciples = 0
            for _ in range(recruiting_disciples):
                if self.state.sect_data["disciples_total"] < self.state.max_disciples:
                    if random.random() < RECRUITMENT_BASE_GAIN: # 3% 几率招募成功
                        new_disciples += 1
                        self.state.sect_data["disciples_total"] += 1
            if new_disciples > 0:
                self.state.log(f"招募弟子成功：新增 {new_disciples} 名弟子！")
            else:
                self.state.log("本轮未招募到新弟子。")

        print("结算完成。")
        print(self.state.to_dict())
        input("\n按回车进入下一回合...")

    def run(self):
        """游戏主界面与主循环"""
        while True:
            os.system("cls")
            print("="*50,"\n      欢迎来到《仙宗 - 修仙模拟器》\n","="*50)
            print("1. 开始新游戏\n2. 读取存档\n0. 退出游戏\n","="*50)
            
            menu_choice = input("\n请选择操作: ").strip()
            
            if menu_choice == "1":
                self.__init__()
            elif menu_choice == "2":
                self.load_save()
            elif menu_choice == "0":
                print("\n感谢游玩，江湖再见！")
                break
            else:
                continue

            # 游戏主循环
            while True:
                if self.run_turn():
                    break

    def _handle_save_load(self):
        """处理存档读档"""
        print("\n1. 存档")
        print("2. 读档")
        print("0. 返回")
        choice = input("\n选择: ").strip()
        
        if choice == "1":
            for i in range(1, 4):
                print(f"槽位 {i}")
            slot = input("选择存档槽位 (1-3): ").strip()
            if slot in ["1", "2", "3"]:
                res = save_game(self.state.to_dict(), int(slot))
                self.state.log(f"\n{res['message']}")
            else:
                self.state.log("无效的输入")
        elif choice == "2":
            self.load_save()
            self.display_status()

    def load_save(self):
        files = get_save_files()
        if not files:
            self.state.log("没有发现存档文件。")
            return
        for f in files:
            print(f"- 年份：{f['game_time']} 保存时间：{f['save_time']}")
        slot = input("输入存档编号 (1-3): ").strip()
        if slot in ["1", "2", "3"]:
            filepath = f"saves/save_{slot}.json"
            res = load_game(filepath)
            print(res)
            if res["success"]:
                self._apply_save_data(res["data"]["state"])
                self.state.log("\n读档成功！")
            else:
                self.state.log(f"\n{res['message']}")
        else:
                self.state.log("无效的输入")

    def _apply_save_data(self, data: dict):
        """恢复存档数据"""
        self.state = GameState.from_dict(data)
        # event_data = data.get("event_manager", {})
        # self.event_manager.last_secret_realm_year = event_data.get("last_secret_realm_year", 0)


if __name__ == "__main__":
    game = GameCLI()
    game.run()