import json

from auto_teacher_process.config import Config
from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class PositionLLMProcessor(BaseLLMProcessor):
    prompt = """
### 任务描述
根据以下教师简介提取出主人公教师至今仍在担任的现任行政职务。如果有，请仅输出具体单位职务；否则，仅输出'false'。

### 注意事项
1. 职务范围不限于候选职务列表{positions}中的职务。如果简介中的职务不在候选列表中，但符合实际情况，则返回原文中的职务，请不要将简介中的职务替换为候选列表中的职务。
2. 教授，特聘教授，研究员，特聘研究员，讲师等属于学术职称,请勿提取。
3. 输出时，必须包括完整的单位名称，包括二级学院等信息，不能仅仅输出学校名称或二级单位名称。例如，'中山大学院长'或'计算机学院院长'是不完整的，必须输出完整职务，如中山大学计算机学院院长。
4. 必须严格保留原文中的单位层级。如：中山大学人工智能学院主任不能简化成中山大学主任。

### 教师简介
{profile}

### 候选职务列表
{positions}

### 输出要求
1. 请仅输出职务或'false',不输出任何解释过程。
2. 输出的格式应为：单位名称（包括学校名+二级学院）+ 职务名称，例如:中山大学计算机学院院长。如果简介中没有提到学校或二级学院信息，直接返回职务名称，无需额外信息。
3. 如果教师同时担任多个职务，请用';'隔开，按以下格式输出：
    - 中山大学副校长;中山大学计算机学院院长
"""

    def __init__(
        self,
        logger=None,
        model_name: str = "qwen2.5-instruct-6-54-55",
        system: str = "llm_processor",
        stage: str = "unkonw_task_name",
    ):
        """
        职务提取处理器初始化
        """
        super().__init__(model_name=model_name, system=system, stage=stage, logger=logger)
        self.POSITIONS = Config.LLM_CONFIG.POSITIONS.POSITIONS

    def build_prompt(self, input_data: dict) -> str:
        """
        构建提示词模板
        输入:
            input_data (dict): 包含description键的输入数据
        输出:
            str: 完整的提示词
        """
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(positions=self.POSITIONS, profile=input_data["description"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        self.logger.debug("开始提取职务")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)
        self.logger.debug(f"LLM响应: {response[:200]}...")

        response = response.strip() if response else ""
        self.logger.debug(f"开始验证: {response}")

        if "false" in response.lower():
            result = []
            is_valid = 0
        else:
            try:
                # 处理标准格式的响应
                if response.startswith("[") and response.endswith("]"):
                    result = json.loads(response)
                else:
                    # 处理普通分号分隔的字符串
                    result = [item.strip() for item in response.split(";") if item.strip()]

                is_valid = 1 if result else 0
            except Exception as e:
                self.logger.error(f"响应解析失败: {e!s}", exc_info=True)
                raise e

        self.logger.debug(f"处理完成，结果: {result}，有效: {is_valid}")
        return result, is_valid
