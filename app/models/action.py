from typing import List, Optional
from pydantic import BaseModel

class ActionKey(BaseModel):
    key: str         # 按键
    duration: Optional[float] = None  # 按键持续时间

class Action(BaseModel):
    name: str         # 动作名称
    keys: Optional[List[ActionKey]] = []  # 触发按键
    count: Optional[int] = 0  # 动作次数