# 淘灵热 — 游戏数据面板

> 此文件存储游戏初始数据和当前状态，每次新游戏从此加载初始值。

---

## 🎮 游戏时间

```yaml
current_time:
  year: 1
  month: 1
  day: 1
turn_count: 0
```

---

## 👤 玩家状态

```yaml
player:
  name: "林凡"
  realm: "炼气期三层"           # 境界：炼气期 → 筑基期 → 金丹期 → 元婴期
  level: 3                      # 境界层级（炼气期1-9层）
  age: 23
  lifespan: 180                 # 最大寿元
  spirit_stones: 100            # 灵石（货币）
  cultivation: 0                # 修为值（0-100）
  reputation: 0                 # 声望（-100 到 100）
  location: "灵石矿小镇"
  known_secrets: []             # 已知的秘密/消息
```

---

## 🎒 玩家库存

```yaml
inventory: {}
# 示例：
# inventory:
#   spirit_stone:
#     name: "灵石"
#     quantity: 50
#     type: "基础材料"
#   gathering_dan:
#     name: "聚气丹"
#     quantity: 10
#     type: "丹药"
```

---

## 👥 人脉关系

```yaml
relationships: {}
# 示例：
# relationships:
#   miner_wang:
#     name: "王矿工"
#     favorability: 50
#     level: "矿工"
#     description: "在矿洞干了二十年，消息灵通"
#   merchant_li:
#     name: "李掌柜"
#     favorability: 30
#     level: "商人"
#     description: "镇上最大的丹药铺老板"
```

---

## 📊 市场价格

```yaml
market:
  prices:
    spirit_stone:               # 基础货币
      name: "灵石"
      current: 100
      trend: "持平"
      history: [98, 100, 100, 100, 100]
      type: "基础材料"
      volatility: "低"
      factors: ["矿坑产量", "官方政策"]

    gathering_dan:              # 丹药
      name: "聚气丹"
      current: 50
      trend: "上涨"
      history: [45, 46, 48, 49, 50]
      type: "丹药"
      volatility: "高"
      factors: ["修仙者人数", "丹药产能"]

    iron_fine:                  # 材料
      name: "下品铁精"
      current: 20
      trend: "下跌"
      history: [25, 24, 23, 21, 20]
      type: "基础材料"
      volatility: "中"
      factors: ["矿工数量", "铁匠需求"]

    fire_sun_grass:            # 草药
      name: "火阳草"
      current: 15
      trend: "持平"
      history: [15, 15, 15, 15, 15]
      type: "稀有资源"
      volatility: "极低"
      factors: ["采集难度", "炼丹需求"]

    flying_sword_low:           # 法器
      name: "下品飞剑"
      current: 500
      trend: "稳定"
      history: [480, 490, 500, 500, 500]
      type: "法器"
      volatility: "极高"
      factors: ["战争需求", "门派采购"]

    foundation_dan:            # 丹药
      name: "筑基丹"
      current: 2000
      trend: "稳定"
      history: [1950, 1980, 2000, 2000, 2000]
      type: "丹药"
      volatility: "极高"
      factors: ["稀缺药材", "炼丹师水平"]

    rare_elixir:                # 稀有物品
      name: "九转洗髓丹"
      current: 10000
      trend: "未知"
      history: []
      type: "稀有物品"
      volatility: "未知"
      factors: ["天材地宝", "传说"]

  recent_news:                  # 近期新闻
    - id: "news_001"
      content: "灵石矿第三坑口出产增加，矿工们传言'富矿'"
      impact:
        spirit_stone: -2
      time:
        year: 1
        month: 1
        day: -3
      source: "矿工口述"

    - id: "news_002"
      content: "青州官方宣布：下月起对灵石交易征收5%的灵石税"
      impact:
        spirit_stone: 5
      time:
        year: 1
        month: 1
        day: -7
      source: "官方公告"

    - id: "news_003"
      content: "三大宗门因矿脉归属发生争斗，附近修仙者人心惶惶"
      impact:
        gathering_dan: 10
        flying_sword_low: 20
      time:
        year: 1
        month: 1
        day: -15
      source: "坊间传闻"
```

---

## 🎲 随机事件池

```yaml
event_pool:
  common:                      # 普通事件（发生概率高）
    - id: "event_001"
      name: "矿工寻宝"
      description: "一位年轻矿工兴奋地跑来找你，说他发现了一块罕见的伴生灵晶，愿意低价卖给你。"
      trigger_conditions:
        relationship: "miner_wang"
        favorability: 60
      options:
        - text: "购买灵晶（300灵石）"
          cost: 300
          reward:
            rare_crystal: 1
          message: "你买下了'伴生灵晶'，这可是炼制筑基丹的难得材料！"

        - text: "拒绝"
          message: "你摇摇头拒绝了。矿工失望地离开了。"

    - id: "event_002"
      name: "丹药铺缺货"
      description: "镇上唯一的丹药铺贴出告示：聚气丹断货，预计半月后补货。"
      trigger_conditions: {}
      options:
        - text: "询问是否有其他渠道"
          requirement:
            relationships: "merchant_li"
            favorability: 70
          reward:
            message: "李掌柜悄悄告诉你，有一批黑货在城西树林交易，价格是市价的2倍。"

        - text: "等待官方补货"
          message: "你决定等待官方补货。"

  rare:                        # 稀有事件（发生概率低）
    - id: "event_101"
      name: "矿难突发"
      description: "轰隆隆！矿洞传来巨响，尘土飞扬。官方宣布暂停开采，至少关闭一月！"
      trigger_conditions:
        random: 0.05
      impact:
        spirit_stone: 50
        iron_fine: 30
      options:
        - text: "趁低吸货"
          message: "市场恐慌，你趁机低价收购灵石和铁精！"

        - text: "静观其变"
          message: "你选择观望，等待局势明朗。"

    - id: "event_102"
      name: "秘境现世"
      description: "传说中'紫云仙子'曾闭关的秘境现世，据说里面有筑基功法和天材地宝！"
      trigger_conditions:
        random: 0.02
      options:
        - text: "组队探险"
          requirement:
            cultivation: 50
          message: "你组织了一支队伍进入秘境，希望有所收获。"

        - text: "守在入口"
          message: "你守在秘境入口，等待出来的修仙者收购战利品。"
```

---

## 🏆 飞升条件

```yaml
ascension_conditions:
  realm: "元婴期大圆满"
  required_items:
    - name: "九转洗髓丹"
      quantity: 1
    - name: "天外陨铁"
      quantity: 1
    - name: "雷劫草"
      quantity: 3
  spirit_stones: 10000          # 飞升需要缴纳的灵石费用
  cultivation: 100              # 修为圆满
  reputation: 80                # 声望足够
```

---

## 🎯 游戏设置

```yaml
game_settings:
  time_skip_interval: 7         # 加速时间默认跳过天数
  price_update_frequency: 1     # 价格更新频率（天）
  event_probability: 0.3       # 每日事件触发概率
  save_slots: 3                 # 存档槽位数
```

---

## 📝 版本信息

```yaml
meta:
  version: "1.0.0"
  last_updated: "2026-04-01"
  creator: "OfficeClaw1"
```
