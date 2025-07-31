from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.config import FfcsConfig
from huibiao_framework.execption.ffcs import FfcsSendProgressError
from .abstract_client import HuibiaoAbstractClient

from .data_model.ffcs import ProgressSend


class FfcsClient(HuibiaoAbstractClient):
    """
    福富客户端 - 异步实现
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        super().__init__(
            client_name="FfcsProgress", session=session, url=FfcsConfig.PROGRESS_URL
        )

    async def send_progress(
        self, progress_dto: ProgressSend.Dto, reqid
    ) -> Optional[ProgressSend.Vo]:
        request_body: dict = progress_dto.model_dump()

        headers = {"Content-Type": "application/json", "x-request-id": reqid}
        try:
            async with self.session.post(
                self.url, json=request_body, headers=headers
            ) as response:
                logger.debug(f"发送进度请求，reqid={reqid}，dto={request_body}")
                response_data = await response.json()
                logger.debug(f"ffcs progress resp={response_data}")
                vo = ProgressSend.Vo(**response_data)
                logger.debug(f"发送进度成功，reqid={reqid}，vo={vo}")
                return vo
        except Exception as e:
            logger.error(f"发送进度失败，dto={request_body}, {str(e)}")
            raise FfcsSendProgressError(reason=str(e), e=e, reqid=reqid)
