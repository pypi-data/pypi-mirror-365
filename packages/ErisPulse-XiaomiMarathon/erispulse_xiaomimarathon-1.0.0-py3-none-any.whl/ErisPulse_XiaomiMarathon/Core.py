import asyncio
import random
from typing import Dict, List, Any

class GameContent:
    
    # 手机型号选项
    PHONE_MODELS = {
        "1": "小米15",
        "2": "红米Turbo 4 Pro", 
        "3": "小米14 Ultra",
        "4": "Redmi K70 Pro"
    }
    
    # 预约时间选项
    APPOINTMENT_TIMES = {
        "1": {"time": "上午9:00", "description": "工程师刚上班，精神饱满，但可能对你这个早起客户有些不爽"},
        "2": {"time": "上午11:00", "description": "人流较少，工程师有足够时间处理你的手机"},
        "3": {"time": "下午2:00", "description": "人流适中，工程师状态良好"},
        "4": {"time": "下午3:30", "description": "热门时段，工程师可能有些不耐烦"},
        "5": {"time": "下午5:00", "description": "工程师急于下班，可能会催促你"},
        "6": {"time": "晚上7:00", "description": "人流最少，但工程师可能很累，容易犯错"}
    }
    
    # 售后点行为选项
    STORE_ACTIONS = {
        "1": "你直接走向工程师，他正在忙碌地处理其他用户的手机。",
        "2": "你先观察了一下环境，发现有几个工程师在小房间内工作，门口还有店员把关。",
        "3": "你和其他用户交流，听说有人成功'跑路'过，还有人带了'特殊道具'。"
    }
    
    # Fastboot模式选项
    FASTBOOT_RESPONSES = {
        "1": "你耐心等待，但工程师没有告诉你具体进度，只是偶尔看看手机屏幕。",
        "2": "你询问进度，工程师头也不抬地说'快了快了，别着急'。",
        "3": "你注意到手机屏幕上显示着一些代码，似乎正在解锁BL。",
        "4": "你询问手机是否有其他问题，工程师检查后说你的手机电池有点问题。"
    }
    
    # 结局文本
    ENDINGS = {
        "success_escape": """
恭喜通关！
你成功完成了"小米马拉松"挑战，成为了一名真正的"跑路者"！
现在你的手机BL已解锁，可以随意刷机搞机了！

分享你的战绩：
"今天在小米售后成功跑路，BL解锁到手！#小米马拉松 #BL解锁"
        """,
        "caught": """
虽然没能成功，但至少你尝试过了！
下次记得选择更好的时机再挑战"小米马拉松"！

记住：跑马拉松有风险，行动需谨慎！
        """,
        "normal": """
安全第一，虽然没有获得解锁权限，
但至少手机安全回家了。

也许真正的发烧友应该通过正当途径申请解锁？
        """,
        "official_process": """
通过正当渠道表达诉求，虽然过程较长，
但这是最合理和有效的方式。

小米等厂商的解锁政策确实存在争议，
但通过合理途径反馈问题，推动政策改进，
才是对整个社区更有益的做法。
        """,
        "hospital": """
有时候情绪激动并不能解决问题，
反而可能让情况变得更糟。

理性沟通和合理维权才是正确的处理方式。
        """,
        "bricked": """
不幸的是，你的手机变砖了...
这次冒险的代价有点大。

也许下次应该更谨慎一些？
        """,
        "refund": """
虽然没有达成解锁目标，但你成功要回了费用。
有时候安全退出也是明智的选择。
        """,
        "scammed": """
你遭遇了诈骗陷阱，这提醒我们在面对
"特殊渠道"时要保持警惕。

不是所有看似有利的机会都是真的。
        """,
        "bargain_success": """
你不仅成功砍价，还解决了手机问题。
看来良好的沟通技巧也很重要！
        """,
        "tech_success": """
通过技术手段成功解锁，展现了你的专业能力。
        """,
        "wise_leave": """
你明智地离开了可疑环境，避免了潜在风险。
有时候谨慎比冒险更重要。
        """,
        "risk_averse": """
你因为风险过高而放弃，这是明智的选择。
        """,
        "hidden_success": """
你通过特殊渠道成功解锁，这在游戏中是个不错的结局。
        """
    }
    
    # 成就描述
    ACHIEVEMENTS = {
        "固执己见": "不听劝告坚持己见",
        "砍价高手": "成功砍价并解决问题",
        "轻信他人": "轻易相信陌生人",
        "正义使者": "揭露不当行为",
        "技术达人": "掌握专业技术",
        "内部渠道": "通过特殊渠道达成目标",
        "演技派": "巧妙利用道具制造混乱",
        "理性维权者": "通过合理方式表达诉求",
        "过度维权": "维权行为超出合理范围",
        "失败的勇士": "尝试跑路但失败",
        "BL战士": "获得解锁的BootLoader",
        "智取先锋": "巧妙利用环境成功跑路",
        "闪电侠": "成功在售后点拔线跑路",
        "谨慎行事": "谨慎评估风险"
    }

class XiaomiMarathonGame:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = sdk.logger
        self.adapter = sdk.adapter
        self.util = sdk.util
        
        # 游戏状态存储
        self.active_sessions = {}
        self.custom_content = {}  # 自定义内容存储
        
        self.logger.info("小米马拉松初始化完成")
        
    def _get_session(self, user_id: str) -> dict:
        """获取用户游戏会话"""
        if user_id not in self.active_sessions:
            self.active_sessions[user_id] = {
                "player_name": f"用户{user_id[-4:]}",
                "current_scene": "start",
                "phone_model": "",
                "appointment_time": "",
                "unlock_attempts": 0,
                "engineer_trust": 100,
                "player_items": [],
                "achievements": [],
                "game_flags": set(),
                "last_interaction": 0,
                "phone_condition": "good",  # good, broken, unstable
                "engineer_personality": random.choice(["friendly", "strict", "lazy"]),  # 工程师性格
                "store_security": random.choice(["low", "medium", "high"]),  # 店面安保等级
                "player_reputation": 0,  # 玩家声誉值
                "player_skill": random.randint(1, 10),  # 玩家技能值
                "time_passed": 0,  # 游戏内时间（分钟）
                "easter_egg_found": False  # 是否发现彩蛋
            }
        return self.active_sessions[user_id]
        
    def _clear_session(self, user_id: str):
        """清理用户游戏会话"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            
    async def _send_message(self, platform: str, target_type: str, target_id: str, message: str):
        """统一发送消息方法，清理前后空格"""
        adapter = getattr(self.adapter, platform)
        cleaned_message = "\n".join(line.strip() for line in message.strip().split("\n"))
        
        async def _send():
            try:
                await adapter.Send.To(target_type, target_id).Text(cleaned_message)
            except Exception as e:
                self.logger.error(f"发送消息失败: {e}")
        
        asyncio.create_task(_send())
    async def start_game(self, user_id: str, platform: str, is_group: bool = False):
        """开始游戏"""
        session = self._get_session(user_id)
        session["current_scene"] = "start"
        
        welcome_msg = """
欢迎来到《小米马拉松》！

你是一位热爱刷机的发烧友，今天要挑战在小米售后"跑马拉松"！
准备好体验这场惊险刺激的冒险了吗？

请选择你的手机型号：
1. 小米15
2. 红米Turbo 4 Pro
3. 小米14 Ultra
4. Redmi K70 Pro
5. 自定义型号
        """
        
        await self._send_message(platform, "group" if is_group else "user", user_id, welcome_msg)
        session["current_scene"] = "phone_selection"
        
    async def handle_input(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理用户输入"""
        session = self._get_session(user_id)
        
        try:
            scene_handlers = {
                "start": self.start_game,
                "phone_selection": self._handle_phone_selection,
                "custom_phone": self._handle_custom_phone,
                "appointment": self._handle_appointment,
                "at_store": self._handle_at_store,
                "fastboot_mode": self._handle_fastboot_mode,
                "unlock_attempt": self._handle_unlock_attempt,
                "escape_attempt": self._handle_escape_attempt,
                "extreme_measures": self._handle_extreme_measures,
                "extreme_actions": self._handle_extreme_actions,
                "life_threat": self._handle_life_threat,
                "ending": self._handle_ending,
                "phone_issue": self._handle_phone_issue,
                "negotiation": self._handle_negotiation,
                "secret_path": self._handle_secret_path,
                "hiding_spot": self._handle_hiding_spot,
                "security_confrontation": self._handle_security_confrontation,
                "bribe_attempt": self._handle_bribe_attempt,
                "technical_solution": self._handle_technical_solution
            }
            
            handler = scene_handlers.get(session["current_scene"])
            if handler:
                await handler(user_id, platform, user_input, is_group)
            else:
                target_type = "group" if is_group else "user"
                await self._send_message(platform, target_type, user_id, "游戏出现异常，请重新开始。输入 /开始小米马拉松 重新开始游戏")
                self._clear_session(user_id)
                
        except Exception as e:
            self.logger.error(f"游戏处理出错: {e}")
            target_type = "group" if is_group else "user"
            await self._send_message(platform, target_type, user_id, "游戏出现异常，请重新开始。输入 /开始小米马拉松 重新开始游戏")
            self._clear_session(user_id)
            
    async def _handle_phone_selection(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理手机选择"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input in GameContent.PHONE_MODELS:
            session["phone_model"] = GameContent.PHONE_MODELS[user_input]
        elif user_input == "5":
            await self._send_message(platform, target_type, user_id, "请输入你的手机型号：")
            session["current_scene"] = "custom_phone"
            return
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-5：")
            return
            
        # 进入预约环节
        msg = f"""
你选择了 {session['phone_model']}
现在需要预约小米售后服务来降级系统。

请选择预约时间：
上午时段：
1. 上午9:00 (工程师刚上班，精神饱满)
2. 上午11:00 (人流较少，但工程师可能有些疲劳)

下午时段：
3. 下午2:00 (推荐，人流适中)
4. 下午3:30 (默认热门时段)
5. 下午5:00 (工程师可能急于下班)

晚间时段：
6. 晚上7:00 (人流最少，但工程师可能很累)
        """
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "appointment"
        
    async def _handle_custom_phone(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理自定义手机型号"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if len(user_input.strip()) < 2:
            await self._send_message(platform, target_type, user_id, "请输入有效的手机型号：")
            return
            
        session["phone_model"] = user_input.strip()
        
        msg = f"""
你选择了 {session['phone_model']}
现在需要预约小米售后服务来降级系统。

请选择预约时间：
上午时段：
1. 上午9:00 (工程师刚上班，精神饱满)
2. 上午11:00 (人流较少，但工程师可能有些疲劳)

下午时段：
3. 下午2:00 (推荐，人流适中)
4. 下午3:30 (默认热门时段)
5. 下午5:00 (工程师可能急于下班)

晚间时段：
6. 晚上7:00 (人流最少，但工程师可能很累)
        """
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "appointment"
        
    async def _handle_appointment(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理预约"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input not in GameContent.APPOINTMENT_TIMES:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-6：")
            return
            
        time_info = GameContent.APPOINTMENT_TIMES[user_input]
        session["appointment_time"] = time_info["time"]
        
        msg = f"""
预约成功！你将在{time_info['time']}到达小米售后点。
{time_info['description']}

签到后，你需要签署相关文件并等待工程师为你服务。

到达售后点后：
1. 直接找工程师
2. 先观察环境再行动
3. 和其他用户交流经验
4. 检查是否有隐藏彩蛋 (需要仔细观察)
        """
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "at_store"
        
    async def _handle_at_store(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理在售后点"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        # 发现彩蛋的特殊选项
        if user_input == "4":
            session["easter_egg_found"] = True
            msg = """
你仔细观察周围，发现墙上贴着一张纸条：
"小米之家温馨提示：解锁BootLoader请前往官方社区申请，售后点不提供此服务"
纸条下面还有一行小字："偷偷告诉你，工程师的抽屉里有好东西..."

你获得了隐藏道具：「工程师的提示」
            """
            if "工程师的提示" not in session["player_items"]:
                session["player_items"].append("工程师的提示")
            await self._send_message(platform, target_type, user_id, msg)
            
            # 继续正常流程
            msg2 = """
你继续观察环境，发现有几个工程师在小房间内工作，门口还有店员把关。

请选择下一步行动：
1. 直接找工程师
2. 先观察环境再行动
3. 和其他用户交流经验
            """
            await self._send_message(platform, target_type, user_id, msg2)
            return
        
        if user_input not in GameContent.STORE_ACTIONS:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-4：")
            return
            
        observation = GameContent.STORE_ACTIONS[user_input]
        
        # 随机事件：是否有特殊道具
        if user_input == "3" and random.random() < 0.3:
            session["player_items"].append("精神类药物")
            special_item_msg = "\n一位老哥悄悄塞给你一个小瓶子：'关键时刻用这个，工程师不敢拦你'"
        else:
            special_item_msg = ""
            
        msg = f"""
{observation}{special_item_msg}
工程师叫到你的号码，你把手机交给他。
他开始检查你的手机，并准备进入Fastboot模式进行降级操作。

此时你可以：
1. 耐心等待工程师操作
2. 询问刷机进度
3. 趁机观察手机状态
4. 询问手机是否有其他问题
        """
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "fastboot_mode"
        
    async def _handle_fastboot_mode(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理Fastboot模式"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input not in GameContent.FASTBOOT_RESPONSES:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-4：")
            return
            
        engineer_response = GameContent.FASTBOOT_RESPONSES[user_input]
        
        # 如果选择询问手机问题，触发新分支
        if user_input == "4":
            session["phone_condition"] = "broken"
            msg = f"""
{engineer_response}
他继续说："电池老化可能导致刷机过程中断电，有一定风险。"

你的选择：
1. 坚持继续刷机
2. 要求更换电池后再刷机
3. 询问是否有其他解决方案
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "phone_issue"
            return
        
        # 随机事件：工程师离开
        engineer_leaves = random.random() < 0.4  # 40%概率工程师离开
        if engineer_leaves:
            msg = f"""
{engineer_response}
突然，工程师手机响了，他接了个电话后说："我先出去抽口烟"，然后离开了现场。
此时你发现手机正处于解锁状态！

你的选择：
1. 立即拔线跑路（经典马拉松）
2. 耐心等待工程师回来
3. 尝试自己操作手机
4. 趁机与工程师协商解锁事宜
            """
            session["engineer_trust"] -= 30
        else:
            # 工程师不离开的情况
            msg = f"""
{engineer_response}
工程师继续操作，但你注意到屏幕上的信息显示BL正在解锁。

你的选择：
1. 趁工程师不注意时拔线跑路
2. 继续等待完成刷机
3. 询问是否可以解锁BL
4. 提出技术性建议
            """
            
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "unlock_attempt"
        
    async def _handle_phone_issue(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理手机问题分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 坚持继续刷机
            msg = """
你坚持继续刷机，工程师有些犹豫但还是继续操作。
刷机过程中手机突然断电，刷机失败！
工程师无奈地说："我早就提醒过你了..."

结局：刷机失败，手机变砖
成就解锁：【固执己见】- 不听劝告坚持己见
            """
            if "固执己见" not in session["achievements"]:
                session["achievements"].append("固执己见")
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "bricked", is_group)
            
        elif user_input == "2":  # 要求更换电池
            msg = """
你要求先更换电池再刷机，工程师表示需要额外收费。
你们开始协商价格...

你的选择：
1. 接受工程师的报价
2. 讨价还价
3. 放弃刷机，要求退款
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "negotiation"
            
        elif user_input == "3":  # 询问其他解决方案
            msg = """
你询问是否有其他解决方案，工程师带你到一个隐蔽的角落...

他神秘地说："其实我有个朋友可以帮你解锁，但需要一点'特殊操作'..."

你的选择：
1. 询问详情
2. 拒绝并要求正常处理
3. 表示感兴趣
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "secret_path"
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_negotiation(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理价格协商分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 接受报价
            msg = """
你接受了工程师的报价，他开始更换电池。
更换完成后继续刷机，过程很顺利。
但BL依然锁定，你没有获得解锁权限。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "2":  # 讨价还价
            # 根据玩家技能值决定结果
            if session["player_skill"] > 5:
                msg = """
凭借你的口才，成功将价格压低了一半。
工程师虽然不太情愿，但还是同意了。
更换电池后刷机顺利完成，虽然没有解锁BL，但手机运行更稳定了。

成就解锁：【砍价高手】- 成功砍价并解决问题
                """
                if "砍价高手" not in session["achievements"]:
                    session["achievements"].append("砍价高手")
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "bargain_success", is_group)
            else:
                msg = """
你尝试讨价还价，但工程师态度强硬，坚持原价。
最终你放弃了更换电池的计划，要求直接刷机。
刷机过程中手机断电，刷机失败！

结局：刷机失败，手机变砖
                """
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "bricked", is_group)
                
        elif user_input == "3":  # 放弃刷机
            msg = """
你决定放弃刷机，要求退款。
工程师虽然有些不情愿，但还是退还了部分费用。
你带着手机离开了售后点。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "refund", is_group)
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_secret_path(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理秘密路径分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 询问详情
            msg = """
工程师左右看了看，压低声音说："我有个熟人在小米总部，
可以帮你解锁，但需要500元手续费，而且这事不能声张..."

你的选择：
1. 同意并付款
2. 拒绝并离开
3. 假装同意，然后举报
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "bribe_attempt"
            
        elif user_input == "2":  # 拒绝并要求正常处理
            msg = """
你拒绝了工程师的提议，要求正常处理。
工程师有些尴尬，但还是带你回到工作区继续刷机。
刷机过程很顺利，但BL依然锁定。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 表示感兴趣
            msg = """
你表示感兴趣，工程师带你到仓库后面的一个小房间。
他拿出一个奇怪的设备，说："用这个可以强制解锁，但有一定风险..."

你的选择：
1. 同意尝试
2. 意识到风险，拒绝操作
3. 要求查看设备资质
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "technical_solution"
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_bribe_attempt(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理贿赂尝试分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 同意并付款
            msg = """
你同意了工程师的提议并付款。
他带你到一个隐蔽的地方操作，但突然几个保安出现...
原来这是个陷阱！你被当作可疑人员带到了经理办公室。

结局：遭遇陷阱，被调查
成就解锁：【轻信他人】- 轻易相信陌生人
            """
            if "轻信他人" not in session["achievements"]:
                session["achievements"].append("轻信他人")
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "scammed", is_group)
            
        elif user_input == "2":  # 拒绝并离开
            msg = """
你意识到这可能是个骗局，拒绝了工程师的提议。
工程师脸色一变，但还是带你回到工作区继续刷机。
刷机过程很顺利，但BL依然锁定。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 假装同意，然后举报
            msg = """
你假意同意，趁工程师不注意时用手机录了音。
然后你直接找到店长举报了这件事。
店长对你表示感谢，并安排了另一位工程师为你服务。

成就解锁：【正义使者】- 揭露不当行为
            """
            if "正义使者" not in session["achievements"]:
                session["achievements"].append("正义使者")
            await self._send_message(platform, target_type, user_id, msg)
            # 继续正常流程
            msg2 = """
新的工程师非常专业，为你仔细检查了手机。
刷机过程很顺利，虽然没有解锁BL，但手机运行更稳定了。
            """
            await self._send_message(platform, target_type, user_id, msg2)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_technical_solution(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理技术解决方案分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 同意尝试
            # 根据玩家技能值决定结果
            if session["player_skill"] > 7:
                msg = """
你决定冒险一试。工程师操作设备时，你仔细观察并记下了关键步骤。
设备成功解锁了你的手机BL，而且没有损坏手机！

成就解锁：【技术达人】- 掌握专业技术
                """
                if "技术达人" not in session["achievements"]:
                    session["achievements"].append("技术达人")
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "tech_success", is_group)
            else:
                msg = """
你同意尝试，但设备操作过程中出现异常。
手机屏幕突然变黑，无法开机！
工程师慌忙检查，但为时已晚...

结局：手机变砖
                """
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "bricked", is_group)
                
        elif user_input == "2":  # 意识到风险，拒绝操作
            msg = """
你意识到风险太大，拒绝了这个操作。
工程师有些失望，但还是带你回到工作区继续刷机。
刷机过程很顺利，但BL依然锁定。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 要求查看设备资质
            msg = """
你要求查看设备的资质证明，工程师支支吾吾拿不出任何证明。
你决定离开这里，找其他途径解决问题。

结局：明智离开
成就解锁：【谨慎行事】- 谨慎评估风险
            """
            if "谨慎行事" not in session["achievements"]:
                session["achievements"].append("谨慎行事")
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "wise_leave", is_group)
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_unlock_attempt(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理解锁尝试"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 拔线跑路
            await self._attempt_escape(user_id, platform, is_group)
                
        elif user_input == "2":  # 等待完成
            msg = """
你选择耐心等待刷机完成。
刷机过程很顺利，手机成功降级并恢复正常。
但BL依然锁定，你没有获得解锁权限。

工程师将手机还给你，并提醒你小心使用。
这次体验虽然安全，但没有达到"跑马拉松"的目的。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 询问解锁
            # 随机触发极端情况
            if random.random() < 0.15:  # 15%概率触发极端对话
                msg = """
你询问工程师是否可以解锁BL。
工程师严肃地告诉你："BootLoader解锁需要满足特定条件，
并且需要在小米社区申请，不能在售后点随意解锁。"

你显得有些失望，情绪激动地说："我手机现在这样用不了，
你们必须给我解决！"

工程师有些为难："这确实不是我们能处理的..."

此时你的选择：
1. 继续正常等待刷机
2. 采取极端措施（警告：可能导致严重后果）
3. 放弃询问，等待刷机完成
4. 要求与店长对话
                """
                await self._send_message(platform, target_type, user_id, msg)
                session["current_scene"] = "extreme_measures"
            else:
                msg = """
你询问工程师是否可以解锁BL。
工程师严肃地告诉你："BootLoader解锁需要满足特定条件，
并且需要在小米社区申请，不能在售后点随意解锁。"

你意识到直接询问不是好办法...
现在你有两个选择：
1. 放弃询问，等待刷机完成
2. 趁工程师去洗手间时尝试跑路
3. 寻找其他机会
                """
                await self._send_message(platform, target_type, user_id, msg)
                session["current_scene"] = "escape_attempt"
        elif user_input == "4":  # 提出技术性建议
            msg = """
你提出了一些技术性建议，工程师很感兴趣。
你们开始讨论一些高级刷机技巧，工程师对你的专业知识刮目相看。

他悄悄告诉你："其实我这里有一些内部工具，可以帮你解锁，
但这件事不能让别人知道..."

你的选择：
1. 同意并尝试
2. 感谢但拒绝
3. 询问是否有风险
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "hiding_spot"
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-4：")
            
    async def _handle_hiding_spot(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理隐藏地点分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 同意并尝试
            # 根据玩家技能值决定结果
            success = random.random() < (session["player_skill"] / 15 + 0.5)
            if success:
                msg = """
工程师带你到仓库后面，使用内部工具成功解锁了你的手机BL。
整个过程非常顺利，没有留下任何记录。

成就解锁：【内部渠道】- 通过特殊渠道达成目标
                """
                if "内部渠道" not in session["achievements"]:
                    session["achievements"].append("内部渠道")
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "hidden_success", is_group)
            else:
                msg = """
工程师尝试使用内部工具，但操作过程中出现错误。
手机系统受损，无法正常启动！

结局：操作失误导致手机损坏
                """
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "bricked", is_group)
                
        elif user_input == "2":  # 感谢但拒绝
            msg = """
你感谢工程师的好意，但还是决定通过正常渠道申请解锁。
工程师尊重你的决定，继续完成正常的刷机流程。
刷机过程很顺利，但BL依然锁定。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 询问是否有风险
            msg = """
你询问操作是否有风险，工程师犹豫了一下说：
"任何操作都有风险，但我的技术你可以放心。"
你注意到他说话时有些紧张，似乎在隐瞒什么。

你的选择：
1. 坚持要求了解详细风险
2. 放弃这个提议
3. 要求签署免责协议
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "security_confrontation"
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_security_confrontation(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理安全对峙分支"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 坚持要求了解详细风险
            msg = """
你坚持要求了解详细风险，工程师显得很不耐烦。
这时一个保安走过来询问情况，工程师立即改变了态度。

保安说："先生，这里不能进行非标准操作，请回到工作区。"
你被带回到公开工作区，工程师继续正常的刷机流程。

结局：被制止非标准操作
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "2":  # 放弃这个提议
            msg = """
你决定放弃这个提议，要求进行正常的刷机服务。
工程师有些失望，但还是带你回到工作区继续刷机。
刷机过程很顺利，但BL依然锁定。

工程师将手机还给你，并提醒你小心使用。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "3":  # 要求签署免责协议
            msg = """
你要求签署免责协议，工程师脸色一变。
他说："这种操作不能签署协议，出了问题你自己负责。"
你觉得风险太大，决定放弃。

结局：因风险过高放弃
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "risk_averse", is_group)
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _handle_extreme_measures(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理极端措施"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 继续正常等待
            msg = """
你冷静下来，决定还是正常等待刷机完成。
整个过程很顺利，手机恢复正常。
虽然没有获得解锁权限，但至少安全回家了。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "2":  # 采取极端措施
            # 极端措施选项
            msg = """
你的情绪变得激动，场面开始紧张起来...

你可以选择：
1. 威胁要投诉到小米总部
2. 声称手机问题严重可能危及生命（极端言论）
3. 拿出准备的"精神类药物"（如果你有的话）
4. 放弃极端行为，正常等待
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "extreme_actions"
            
        elif user_input == "3":  # 放弃询问
            msg = """
你意识到这样做不合适，决定还是正常等待刷机完成。
整个过程很顺利，手机恢复正常。
虽然没有获得解锁权限，但至少安全回家了。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "4":  # 要求与店长对话
            msg = """
你要求与店长对话，工程师去请示了店长。
店长过来后了解情况，表示理解你的需求，
但依然坚持官方解锁流程。

他说："我们可以帮你加快官方申请流程，
但不能在售后点进行非标准操作。"

你的选择：
1. 接受店长的建议
2. 坚持要求现场解锁
3. 要求提供官方申请指导
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "negotiation"
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-4：")
            
    async def _handle_extreme_actions(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理极端行为"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 威胁投诉
            msg = """
你大声说："你们这样对待客户，我要投诉到小米总部！"
工程师和其他工作人员都看向你，场面一度尴尬。
店长走过来询问情况，在了解后表示会向上反馈你的需求。

最终：
1. 工程师继续正常刷机
2. 店长安排专人跟进你的解锁申请
            """
            await self._send_message(platform, target_type, user_id, msg)
            # 这种情况下通常会正常处理
            await asyncio.sleep(2)
            msg2 = """
店长记录了你的信息，并承诺会协助你通过官方渠道申请解锁。
虽然这次没有直接解锁，但你获得了官方的关注。

结局：通过正当渠道获得关注
成就解锁：【理性维权者】- 通过合理方式表达诉求
            """
            if "理性维权者" not in session["achievements"]:
                session["achievements"].append("理性维权者")
            await self._send_message(platform, target_type, user_id, msg2)
            await self._show_ending(user_id, platform, "official_process", is_group)
            
        elif user_input == "2":  # 声称危及生命
            msg = """
你激动地说："我这手机问题严重，可能危及我的生命！
你们必须马上给我解决！"
周围的人都震惊了，店长立即联系了值班经理。
保安也围了过来，场面变得紧张...

此时你意识到可能过激了：
1. 继续坚持你的说法
2. 道歉并正常等待刷机
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "life_threat"
            
        elif user_input == "3":  # 使用精神类药物
            if "精神类药物" in session["player_items"]:
                msg = """
你拿出小瓶子："我有医生开的药，现在感觉不太舒服..."
周围的人开始后退，工程师和店长面露难色。
"你先坐下休息一下，我们联系医生..."店长紧张地说。

在混乱中，你抓起手机准备跑路...

成就解锁：【演技派】- 巧妙利用道具制造混乱
                """
                if "演技派" not in session["achievements"]:
                    session["achievements"].append("演技派")
                await self._send_message(platform, target_type, user_id, msg)
                await self._attempt_escape(user_id, platform, is_group, success_boost=0.3)
            else:
                msg = """
尴尬...你并没有那种道具。
周围的人用奇怪的眼神看着你。
工程师说："先生，你先冷静一下，我们正常处理你的手机。"

你只能继续等待刷机完成。
                """
                await self._send_message(platform, target_type, user_id, msg)
                await self._show_ending(user_id, platform, "normal", is_group)
                
        elif user_input == "4":  # 放弃极端行为
            msg = """
你意识到这样做不合适，决定还是正常等待刷机完成。
整个过程很顺利，手机恢复正常。
虽然没有获得解锁权限，但至少安全回家了。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-4：")
            
    async def _handle_life_threat(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理生命威胁后续"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 继续坚持
            msg = """
你继续坚持你的说法，引起了更大的关注。
最终医护人员和警察都赶到了现场。
经过检查，确认你并无大碍，只是情绪激动。

结局：被送往医院检查，手机正常归还
成就解锁：【过度维权】- 维权行为超出合理范围
            """
            if "过度维权" not in session["achievements"]:
                session["achievements"].append("过度维权")
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "hospital", is_group)
            
        elif user_input == "2":  # 道歉
            msg = """
你意识到自己的言行过激，向工作人员道歉。
"对不起，我刚才太激动了，我们还是正常处理吧。"
工程师点头表示理解，继续为你刷机。

虽然经历了一些波折，但最终手机恢复正常。
这件事也让你反思维权的合理方式。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-2：")
            
    async def _handle_escape_attempt(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理逃跑尝试"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        if user_input == "1":  # 放弃询问
            msg = """
你决定放弃解锁BL的念头，耐心等待刷机完成。
整个过程很顺利，手机恢复正常。
虽然没有获得解锁权限，但至少安全回家了。
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "normal", is_group)
            
        elif user_input == "2":  # 趁机跑路
            await self._attempt_escape(user_id, platform, is_group)
            
        elif user_input == "3":  # 寻找其他机会
            msg = """
你决定寻找其他机会，假装去洗手间。
在洗手间里，你发现了一个紧急出口...

但门口有监控，而且门是锁着的。
你意识到强行闯出去可能会触发警报。

你的选择：
1. 回到工作区，放弃逃跑
2. 尝试撬开门锁
3. 寻找其他出口
            """
            await self._send_message(platform, target_type, user_id, msg)
            session["current_scene"] = "hiding_spot"
            
        else:
            await self._send_message(platform, target_type, user_id, "无效选择，请重新输入1-3：")
            
    async def _attempt_escape(self, user_id: str, platform: str, is_group: bool = False, success_boost: float = 0.0):
        """尝试逃跑"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        # 计算逃跑成功率
        base_success_rate = 0.4  # 基础成功率40%
        success_rate = base_success_rate + success_boost
        
        # 根据之前行为调整成功率
        if session["engineer_trust"] < 50:
            success_rate += 0.2  # 工程师信任度低，更容易成功
            
        # 根据店面安保等级调整成功率
        if session["store_security"] == "high":
            success_rate -= 0.2
        elif session["store_security"] == "low":
            success_rate += 0.1
            
        escape_success = random.random() < success_rate
            
        if escape_success:
            # 成功逃跑
            escape_method = random.choice([
                "你果断拔掉数据线，抓起手机就往外跑！工程师刚好转身，你成功逃离了售后点！",
                "趁工程师不注意，你迅速收起手机塞进口袋，借口上厕所逃离了现场。",
                "你大喊一声'我有急事'，抓起手机就冲出门，工程师在身后喊你都没停下。"
            ])
            
            msg = f"""
{escape_method}
恭喜你完成了"小米马拉松"挑战！

成就解锁：【BL战士】- 获得解锁的BootLoader
            """
            if "BL战士" not in session["achievements"]:
                session["achievements"].append("BL战士")
                
            # 根据情况解锁额外成就
            if success_boost > 0.2:  # 使用了特殊手段
                msg += "成就解锁：【智取先锋】- 巧妙利用环境成功跑路\n"
                if "智取先锋" not in session["achievements"]:
                    session["achievements"].append("智取先锋")
            else:
                msg += "成就解锁：【闪电侠】- 成功在售后点拔线跑路\n"
                if "闪电侠" not in session["achievements"]:
                    session["achievements"].append("闪电侠")
                    
            msg += """
你现在的手机已经解锁BL，可以随意刷机了！
分享你的战绩：
"今天在小米售后成功跑路，BL解锁到手！#小米马拉松 #BL解锁"
            """
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "success_escape", is_group)
        else:
            # 被抓住
            capture_method = random.choice([
                "你刚拔线准备跑路，工程师正好回头！他一把抓住了你：'你要干嘛？'",
                "你刚起身，门口的店员就拦住了你：'先生请留步，手机还没处理完呢。'",
                "你刚跑到门口，保安就出现了：'先生请回来，有问题我们需要当面解决。'"
            ])
            
            msg = f"""
{capture_method}
场面一度非常尴尬...

结局：被工作人员抓住，手机被没收检查
成就解锁：【失败的勇士】- 尝试跑路但失败
            """
            if "失败的勇士" not in session["achievements"]:
                session["achievements"].append("失败的勇士")
                
            # 根据情况追加后果
            if session["engineer_trust"] < 30:
                msg += """
由于你的行为过于激烈，工程师要求你签署额外的协议，
并且你的信息被记录在案，可能影响今后的小米服务。
                """
                
            await self._send_message(platform, target_type, user_id, msg)
            await self._show_ending(user_id, platform, "caught", is_group)
            
    async def _handle_ending(self, user_id: str, platform: str, user_input: str, is_group: bool = False):
        """处理结局后操作"""
        target_type = "group" if is_group else "user"
        
        if user_input.lower() in ["重新开始", "restart", "r"] or user_input.startswith("/开始小米马拉松"):
            self._clear_session(user_id)
            await self.start_game(user_id, platform, is_group)
        elif user_input.lower() in ["查看成就", "achievements", "a"]:
            session = self._get_session(user_id)
            achievements = "、".join(session["achievements"]) if session["achievements"] else "暂无成就"
            msg = f"当前成就：{achievements}\n\n输入'重新开始'再来一次，或'退出'结束游戏"
            await self._send_message(platform, target_type, user_id, msg)
        elif user_input.lower() in ["退出", "quit", "q"]:
            self._clear_session(user_id)
            await self._send_message(platform, target_type, user_id, "游戏结束。感谢游玩《小米马拉松》！")
        else:
            await self._send_message(platform, target_type, user_id, "游戏副本：\n输入'重新开始'再玩一次\n输入'查看成就'查看获得的成就\n输入'退出'结束游戏")
            
    async def _show_ending(self, user_id: str, platform: str, ending_type: str, is_group: bool = False):
        """显示结局"""
        session = self._get_session(user_id)
        target_type = "group" if is_group else "user"
        
        msg = GameContent.ENDINGS.get(ending_type, "游戏结束")
        msg += "\n\n游戏副本：\n输入'重新开始'再玩一次\n输入'查看成就'查看获得的成就\n输入'退出'结束游戏"
        
        await self._send_message(platform, target_type, user_id, msg)
        session["current_scene"] = "ending"

# 游戏入口点
class Main:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = sdk.logger
        self.game = XiaomiMarathonGame(sdk)
        
        # 注册消息处理器
        @sdk.adapter.on("message")
        async def handle_message(event_data):
            await self._on_message(event_data)
            
        self.logger.info("小米马拉松模块已加载")
        
    async def _on_message(self, data):
        """处理消息事件"""
        platform = data.get("platform")
        detail_type = data.get("detail_type")
        is_group = detail_type == "group"
        
        # 根据消息类型确定目标ID
        if is_group:
            target_id = data.get("group_id")
        else:
            target_id = data.get("user_id")
            
        message = data.get("alt_message", "")
            
        self.logger.debug(f"收到消息: {message}, 用户: {target_id}, 平台: {platform}, 类型: {detail_type}")
        
        # 检查是否是游戏相关消息
        if message.startswith("/开始小米马拉松") or message.startswith("/xm_marathon"):
            self.logger.info(f"用户 {target_id} 开始游戏")
            await self.game.start_game(target_id, platform, is_group)
        elif message in ["/重新开始", "/restart", "/r"] and target_id in self.game.active_sessions:
            self.game._clear_session(target_id)
            await self.game.start_game(target_id, platform, is_group)
        elif target_id in self.game.active_sessions:
            # 用户在游戏中，处理游戏输入
            self.logger.debug(f"处理游戏中输入: {message}")
            await self.game.handle_input(target_id, platform, message, is_group)
        elif message.startswith("/"):
            # 其他命令
            await self._handle_commands(data)
            
    async def _handle_commands(self, data):
        """处理其他命令"""
        platform = data.get("platform")
        detail_type = data.get("detail_type")
        is_group = detail_type == "group"
        
        # 根据消息类型确定目标ID
        if is_group:
            target_id = data.get("group_id")
        else:
            target_id = data.get("user_id")
            
        message = data.get("alt_message", "")
        
        if message in ["/help", "/帮助"]:
            help_text = """
/开始马拉松 - 开始小米马拉松
/重新开始 - 重新开始上一局
/查看成就 - 查看已完成的成就
/退出 - 结束游戏
            """
            await self.game._send_message(platform, detail_type, target_id, help_text)

    @staticmethod
    def should_eager_load():
        return True