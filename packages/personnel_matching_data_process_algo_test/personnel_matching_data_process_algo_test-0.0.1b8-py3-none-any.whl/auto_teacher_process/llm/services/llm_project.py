from auto_teacher_process.llm.llm_base import BaseLLMProcessor


class ProjectLLMProcessor(BaseLLMProcessor):
    prompt = """
## 任务描述
请从提供的教师简介中，提取出该教师的科研项目(论文、专利不属于科研项目)，并根据项目描述严格按照以下规则进行分类，提取到的项目信息必须来自教师简介原文，多个项目必须以数组的形式存储，请注意“承担”的科研项目不是主持的项目
1.主持的项目：项目的相关描述中必须明确出现“主持”、“负责”、“负责人”字样。
2.参与的项目：项目的相关描述中没有出现“主持”、“负责”、“负责人”字样。

## 注意事项
1.论文和专利不属于科研项目，不需要提取。
2.项目信息必须包含该项目所有相关的描述。
3.多个项目信息必须以数组的形式存储。
4.请注意，项目描述中的“承担”不属于主持的项目。

## 教师简介
{description}

## 输出格式要求：
将提取到的项目信息按照以下 JSON 格式返回，只需返回一个json，不要返回其他任何内容：
{{
	"主持的项目": ["项目信息1", "项目信息2"],
	"参与的项目": ["项目信息1", "项目信息2"]
}}
"""

    def __init__(self, model_name="qwen2.5-instruct-6-54-55", logger=None, system="llm_processor", stage="unkonw_task_name"):
        super().__init__(model_name, logger, system, stage)

    def build_prompt(self, input_data: dict) -> str:
        if "description" not in input_data:
            raise ValueError("input_data must contain 'description' key")

        return self.prompt.format(description=input_data["description"])

    async def process(self, *args, **kwargs) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        self.logger.debug("开始提取项目")
        prompt = self.build_prompt(kwargs["input_data"])
        self.logger.debug(f"生成的提示词: {prompt[:200]}...")

        response = await self.get_llm_response(prompt, temperature=0.3)
        self.logger.debug(f"LLM响应: {response[:200]}...")

        response = response if response is not None else ""
        self.logger.debug(f"开始验证: {response}")
        try:
            result = eval(response)
            self.logger.debug(f"处理结果: {result}")
            if result["主持的项目"] == [] and result["参与的项目"] == []:
                is_valid = 0
            else:
                is_valid = 1
        except Exception as e:
            self.logger.error(f"解析失败：{e}", exc_info=True)
            raise e

        self.logger.debug(f"处理完成，结果: {result}，有效: {is_valid}")
        return result, is_valid
