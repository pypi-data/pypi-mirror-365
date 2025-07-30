from typing import Optional

from .execption import HuiBiaoException


class LLMException(HuiBiaoException):
    pass

class Qwen32bAwqException(LLMException):
    pass


class Qwen32bAwqResponseFormatError(Qwen32bAwqException):
    def __init__(self, msg: str):
        super().__init__(f"模型返回结果错误，报错 {msg}")


class Qwen32bAwqResponseCodeError(Qwen32bAwqException):
    def __init__(self, code: Optional[int]):
        self.code = code
        super().__init__(f"模型处理失败，code={self.code}!")
