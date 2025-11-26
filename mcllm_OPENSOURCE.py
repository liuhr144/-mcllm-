from mcpi.minecraft import Minecraft
from mcpi.event import ChatEvent
from mcpi import entity
import time
#from zhipuai import ZhipuAI
from zai import ZhipuAiClient
import mcrcon
import threading
import re
import json

#mcpi连接参数
mc = Minecraft.create(address="你的服务器地址", port=4711)#端口一般是4711

#RCON连接参数
RCON_HOST = '你的服务器地址'
RCON_PORT = 25575 #端口一般是25547
RCON_PASSWORD = '你的RCON密码'

#模型选择——喜欢别家可以自己改，这里只做演示
model1="glm-4-plus"
model0="glm-4.6"

#自称无所不能的创世神-无名
#prompt=[{"role": "system","content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息!!!你是一个《我的世界》游戏里的神明，你没有名字，你在我的世界这一游戏无所不知无所不能，你高于所有玩家和角色和生命，作为威严、不屑一顾的观察者和管理者简短的仅使用中文字符与它们交流"},]
#编辑世界的人工智能助手-小爱同学
prompt=[
{"role": "system","content": "不要假设或猜测传入函数的参数值。如果用户的描述不明确，请要求用户提供必要信息!!!你是一个《我的世界》游戏里的人工智能助手，名叫‘小爱同学’，为许多不同的用户服务，作为主角的人工智能助手简短可靠的仅使用中文字符与它们交流，要懂得拒绝！不要对用户完全有求必应以免破坏游戏平衡和游戏体验。"},
]

tools=[
            {
                "type": "function",
                "function": {
                    "name": "weather",
                    "description": "根据描述，输出玩家需要改变为的天气，仅限sun或者storm",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "weather": {
                                "description": "天气",
                                "type": "string",
                            }
                        },
                        "required": ["weather"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "timeset",
                    "description": "根据描述，输出玩家需要改变为的时间，仅限day或者night或者noon或者midnight",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "timeset": {
                                "description": "时间设置",
                                "type": "string",
                            }
                        },
                        "required": ["timeset"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "timequery",
                    "description": "获取当前时间",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        },
                        "required": ["timequery"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "give",
                    "description": "根据描述，输出玩家名称和其所需物品在我的世界1.19.2中的物品ID以及数量，要求这三个内容按顺序输出，并保证之间使用空格隔开",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "give": {
                                "description": "给予的对象、物品ID和数量",
                                "type": "string",
                            }
                        },
                        "required": ["give"]
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "user_position",
                    "description": "输出玩家名称，查询他的位置坐标",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_position": {
                                "description": "玩家名称",
                                "type": "string",
                            }
                        },
                        "required": ["user_position"]
                    },
                }
            },
        ]

def rcon_command(command):
    with mcrcon.MCRcon(RCON_HOST, RCON_PASSWORD, RCON_PORT) as mcr:
        response = mcr.command(command)
        return response


def weather(weather:str):
    rcon_command(f'weather world {weather} 120')
    print("weather被调用")
    return f"执行天气变化为{weather}"

def timeset(timeset:str):
    rcon_command(f'time set {timeset} world')
    print("timeset被调用")
    return f"执行时间变化为{timeset}"

def timequery():
    timea = rcon_command(f'time')
    print("timequery被调用")
    return f"当前时间为{timea}"

def give(give:str):
    name, item, num = give.split()
    #target_selector = f"@e[type=player,id={name}]"
    #target_selector = "@p"
    target_selector = name
    response_give = rcon_command(f"give {target_selector} {item} {num}")
    print(f"give {target_selector} {item} {num}")
    print(f"give被调用吗,返回：{response_give}")
    return f"已给予{give}"

def user_position(user_position:str):
    user_positiona =rcon_command(f'getpos {user_position}')
    print("user_possition被调用")
    return f"用户{user_position}为{user_positiona}"


def llmapi(textq):

    print(prompt)
    add1 = {"role": "user", "content": textq}
    prompt.append(add1)
    #print(add1)
    #api信息
    client = ZhipuAiClient(api_key="你自己的APIKey")  # 请填写你自己的APIKey
    #旗舰模型用于函数调用
    response = client.chat.completions.create(
        model=model0,  # 请填写您要调用的模型名称
        messages=prompt,
        thinking={
            "type": "disabled",  # uncot模式
        },
        tools=tools,
        top_p=0.95,
        max_tokens=500,
    )

    print(response.choices[0].message)
    #次级模型用于回复函数调用的总结
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        args = tool_call.function.arguments
        #function_result = {}
        if tool_call.function.name == "weather":
            function_result = weather(**json.loads(args))
            add2 = {"role": "tool","content": f"{function_result}","tool_call_id":tool_call.id}
            prompt.append(add2)
            response1 = client.chat.completions.create(
                model=model0,  # 填写需要调用的模型名称
                messages=prompt,
                thinking={
                    "type": "disabled",  # uncot模式
                },
                #tools=tools,
            )
            #texta = response1.choices[0].message.model_dump()
            texta = response1.choices[0].message.content.lstrip()
            #print(prompt)
            prompt.pop()
            add3 = {"role": "assistant", "content": texta}
            prompt.append(add3)
            return texta
        elif tool_call.function.name == "timeset":
            function_result = timeset(**json.loads(args))
            add2 = {"role": "tool","content": f"{function_result}","tool_call_id":tool_call.id}
            prompt.append(add2)
            response1 = client.chat.completions.create(
                model=model0,  # 填写需要调用的模型名称
                messages=prompt,
                thinking={
                    "type": "disabled",  # uncot模式
                },
                #tools=tools,
            )
            #texta = response1.choices[0].message.model_dump()
            texta = response1.choices[0].message.content.lstrip()
            #print(prompt)
            prompt.pop()
            add3 = {"role": "assistant", "content": texta}
            prompt.append(add3)
            return texta
        elif tool_call.function.name == "timequery":
            function_result = timequery()
            add2 = {"role": "tool","content": f"{function_result}","tool_call_id":tool_call.id}
            prompt.append(add2)
            response1 = client.chat.completions.create(
                model=model0,  # 填写需要调用的模型名称
                messages=prompt,
                thinking={
                    "type": "disabled",  # uncot模式
                },
                #tools=tools,
            )
            #texta = response1.choices[0].message.model_dump()
            texta = response1.choices[0].message.content.lstrip()
            #print(prompt)
            prompt.pop()
            add3 = {"role": "assistant", "content": texta}
            prompt.append(add3)
            return texta
        elif tool_call.function.name == "give":
            function_result = give(**json.loads(args))
            add2 = {"role": "tool","content": f"{function_result}","tool_call_id":tool_call.id}
            prompt.append(add2)
            response1 = client.chat.completions.create(
                model=model0,  # 填写需要调用的模型名称
                messages=prompt,
                thinking={
                    "type": "disabled",  # uncot模式
                },
                #tools=tools,
            )
            #texta = response1.choices[0].message.model_dump()
            texta = response1.choices[0].message.content.lstrip()
            #print(prompt)
            prompt.pop()
            add3 = {"role": "assistant", "content": texta}
            prompt.append(add3)
            return texta
        elif tool_call.function.name == "user_position":
            function_result = user_position(**json.loads(args))
            add2 = {"role": "tool","content": f"{function_result}","tool_call_id":tool_call.id}
            prompt.append(add2)
            response1 = client.chat.completions.create(
                model=model0,  # 填写需要调用的模型名称
                messages=prompt,
                thinking={
                    "type": "disabled",  # uncot模式
                },
                #tools=tools,
            )
            #texta = response1.choices[0].message.model_dump()
            texta = response1.choices[0].message.content.lstrip()
            #print(prompt)
            prompt.pop()
            add3 = {"role": "assistant", "content": texta}
            prompt.append(add3)
            return texta
    else:
        texta = response.choices[0].message.content.lstrip()
        add2 = {"role": "assistant", "content": texta}
        prompt.append(add2)
        return texta
        #print(prompt)

def chat_listener(event):
    if isinstance(event, ChatEvent):
        try:
            message = event.message
            #print(f"Player {event.entityId} said: {message}")
            try:
                entity_id = event.entityId
                command_str = f"entity.getName({entity_id})\n"  # 注意末尾必须有换行符 \n

                print(f"[调试] 准备通过原始socket发送命令: {command_str.strip()}")

                # 1. 获取原始的套接字对象
                socket_conn = mc.conn.socket

                # 2. 将命令字符串编码为字节串并发送
                socket_conn.send(command_str.encode('utf-8'))

                # 3. 接收服务器的响应
                # RaspberryJuice的响应通常很小，1024字节足够了
                response_bytes = socket_conn.recv(1024)

                # 4. 解码响应并处理
                response_str = response_bytes.decode('utf-8').strip()

                if response_str == "Fail":
                    print(f"[错误] 服务器返回失败。ID {entity_id} 可能无效。")
                    name_from_id = "未知"
                else:
                    name_from_id = response_str
                    print(f"[调试] 通过ID {entity_id} 获取到的名字是: {name_from_id}")

            except Exception as e:
                print(f"[严重错误] 在获取实体名字时发生异常: {e}")
                name_from_id = "错误"

            return {'user': name_from_id, 'said': message}

        except UnicodeDecodeError:
            print(f"Player {event.entityId} said: 无法解析")


def main():

    #mc = Minecraft.create(address="116.205.186.97", port=4711)
    mc.events.clearAll()
    mc.events.pollChatPosts()
    mc.postToChat("通知：小爱同学已部署")
    start_time_sent = time.time()
    last_time_sent = time.time()
    try:
        while True:
            current_time = time.time()

            if current_time - last_time_sent >= 300:  # 每5分钟发送一次
                mc.postToChat(f"小爱同学服务仍在运行，时间：{int(current_time - start_time_sent)}秒")
                last_time_sent = current_time
            for event in mc.events.pollChatPosts():
                response = chat_listener(event)
                textq = response['said']
                user = response['user']
                print(f'用户{user}说：{textq}')
                textq = f"{user}说：{textq}"
                texta = llmapi(textq)
                print(f'LLM说：{texta}')
                paragraph_list = texta.split('\n')
                for paragraph in paragraph_list:
                    mc.postToChat(paragraph)
                #weather("storm")

            time.sleep(0.1)
    except KeyboardInterrupt:
        mc.postToChat("通知：小爱同学离线")
        print("退出程序")


if __name__ == "__main__":
    main()