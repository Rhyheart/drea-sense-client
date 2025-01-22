from typing import List
from pydantic import BaseModel

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: dict = {}

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        # 如果只传入一个参数且不是字典，则作为data
        if len(args) == 1 and not kwargs:
            kwargs = {'data': args[0]}
        instance.__init__(**kwargs)
        return instance.model_dump()

class PageData(BaseModel):
    list: List[dict]
    total: int
    page: int 
    page_size: int
    page_count: int