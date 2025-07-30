from typing import List, Optional

from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from huibiao_framework.execption.vllm import (
    Qwen32bAwqResponseFormatError,
    Qwen32bAwqResponseCodeError,
)


class HuizeQwen32bAwqDto(BaseModel):
    class Message(BaseModel):
        content: str = "今天天气如何"
        role: str = "user"

    Action: str = "NormalChat"
    Messages: List[Message] = [
        Message(),
    ]


class HuizeQwen32bAwqVo(BaseModel):
    class Result(BaseModel):
        Output: Optional[str]
        TokenProbs: Optional[List[float]]

        @field_validator("Output")
        def check_output_not_empty(cls, v: str) -> str:
            if v is None or not v.strip():
                raise Qwen32bAwqResponseFormatError("Field 'result.Output' is Empty")
            return v

    code: Optional[int]
    result: Optional[Result]
    message: str

    @field_validator("code")
    def check_code_valid(cls, v: int) -> int:
        if v is None or v != 0:
            # 校验 code 合法性（通常 0 表示成功，非 0 表示错误）
            raise Qwen32bAwqResponseCodeError(v)
        return v

    @field_validator("result")
    def check_result_consistent_with_code(
        cls, v: Optional["Result"], info: FieldValidationInfo
    ) -> Optional["Result"]:
        code = info.data.get("code")
        if code == 0 and v is None:
            # 整体后处理校验：code=0 时 result 必存在
            raise Qwen32bAwqResponseFormatError("Field 'result' is empty!")
        return v
