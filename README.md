# 项目概述

**项目名称**：我的世界服务器人工智能

**项目目标**：
- 通过大模型（LLM）及RCON等，实现《我的世界》游戏内聊天框常驻人工智能。
- 玩家可通过自然语言甚至视觉等方式与LLM对话，进行地图和世界设置操作或角色扮演游戏。

## 技术实现

### 核心组件
1. **大模型（LLM）**：作为服务器OP，回应、处理玩家输入的自然语言，并通过function calling调用服务器OP权限指令。
2. **RCON（Remote Console）**：用于远程调用服务器指令。
3. **MCPI**：用于执行树莓派版本的我的世界指令。
4. **多模态模型（可选）**：在服务器算力支持的情况下，调用地图等视觉信息。
5. **我的世界服务器（版本可选）**：实验脚本使用的服务器版本为1.19.2。

## 效果展示

### 示例场景
1. **角色扮演对话**：
  - 基础功能，基于提示词模板实现
  - 分COT模式和非COT模式

2. **天气、时间等世界参数改变**：
  - 玩家：`下雨吧。`
  - LLM：`雨至`
  - （服务器指令执行“weather world storm 120”）
    ![FZHAB1~}%M@7WIY0I9`W6UW](https://github.com/user-attachments/assets/8b86fe92-74bd-42e7-af0b-58bbe288b5b1)
  - 天气改变展示：
 - https://www.bilibili.com/video/BV15EC7BjEKV/?spm_id_from=333.1387.list.card_archive.click&vd_source=a487178923e823574952754a9cde46cc
    
3. **玩家请求资源**：
  - 玩家：`小爱同学，给我两个苹果`
  - LLM：`好的，我已经把两个苹果放进你的物品栏了`
  - （服务器通过MCPI查询玩家UID后执行）
  - 演示：
  - https://www.bilibili.com/video/BV1nFCiBGErN/?spm_id_from=333.1387.list.card_archive.click&vd_source=a487178923e823574952754a9cde46cc


## 未来展望
- **增强多模态交互**：进一步提升视觉模型的识别能力，支持更复杂的场景互动。
- **优化LLM协同机制**：实现多个LLM之间的有效协同，让游戏拥有多个智能体op。
- **便捷自定义**：自定义简单便捷，允许玩家在前端自定义LLM行为和互动规则（gradio）。


