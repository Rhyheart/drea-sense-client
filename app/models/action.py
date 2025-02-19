from typing import List, Optional
from pydantic import BaseModel

class ActionKey(BaseModel):
    key: Optional[str] = ''         # 按键
    duration: Optional[float] = 0  # 按键持续时间
    count: Optional[int] = 1  # 按键次数

class Action(BaseModel):
    name: Optional[str] = ''       # 动作名称
    keys: Optional[List[ActionKey]] = []  # 触发按键
    count: Optional[int] = 0  # 动作次数
    is_continue: Optional[bool] = False  # 是否继续执行