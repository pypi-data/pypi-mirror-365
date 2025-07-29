from auto_teacher_process.llm.llm_base import BaseLLMProcessor
from auto_teacher_process.utils.text_utils import contains_chinese


class EmailLLMProcessor(BaseLLMProcessor):
    prompt = """
你的任务是从教师简介中提取出该教师的一个邮箱地址。请仔细阅读以下教师简介：
<教师简介>
{description}
</教师简介>
需要注意的是，有些邮箱为防止被恶意骚扰，可能被混淆处理，例如：
 - `user [at] example [dot] com`
 - `user(at)example(dot)com`
 - `user _at_ example _dot_ com`
 - `user＠example．com`（全角字符）
 - `user (at) mail dot edu` 等等。
在提取邮箱时，请遵循以下限制条件：
1. 只返回一个邮箱，不返回其他任何内容。
2. 如果没有提取到邮箱，返回'False'。
3. 邮箱提取必须基于教师简介中从原文中还原真实存在的邮箱，仅允许恢复混淆形式，不允许猜测、推断或构造邮箱。
4. 不要提取包含星号 `*` 的邮箱地址（例如 `li***@example.com`、`***@mail.com` 等）。
5. 不要提取以 `@` 开头、缺少用户名的，如：`@sebastian.adamo` 。
6. 不提取仅有域名或社交账号格式的。
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(description=input_data["description"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        email提取处理过程
        """

        self.logger.debug("开始提取email")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)
        self.logger.debug(f"LLM响应: {response[:200]}...")

        if "False" in response or contains_chinese(response):
            response = ""
            is_valid = 0
        elif "@" in response:
            is_valid = 1
        else:
            response = ""
            is_valid = 0
        self.logger.debug(f"处理完成，结果: {response}，有效: {is_valid}")

        return response, is_valid
