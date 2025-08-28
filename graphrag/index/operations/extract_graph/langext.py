import langextract as lx
import textwrap
import os
import asyncio
from typing import List


class LangExtractor:
    def __init__(self, api_key: str):
        """
        :param api_key: 用于访问 Gemini API 的密钥。
        """
        if not api_key:
            raise ValueError("API key must be provided.")
        self.api_key = api_key

        self.prompt_description = textwrap.dedent("""
            从以下历史文本中，提取所有定义的实体，包括：“人物”、“组织”、“地点”、“时间”、“事件”、“群体”、“会议”、“军事行动”、“重大政策”、“思想概念与理论”。
            对于每一个实体，请根据上下文提供一句简洁的描述。
            同时，识别并描述实体之间的关系，并为每个关系评估其紧密程度（1-10分）。
        """)
        self.examples = [
            lx.data.ExampleData(
                text="一九四六年八月六日，毛泽东在与美国记者安娜·路易斯·斯特朗的谈话中指出，一切反动派都是纸老虎。他强调，如果美国人民能阻止美国反动派帮助蒋介石打内战，那么中国和平有望。他还提到，帝国主义和一切反动派都具有两重性，既是吃人的真老虎，也是终将被人民推翻的纸老虎。革命者必须在战略上藐视敌人，在战术上重视敌人。",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="人物",
                        extraction_text="毛泽东",
                        attributes={
                            "entity_description": "中共中央主席，在与美国记者斯特朗的谈话中提出“一切反动派都是纸老虎”的著名论点。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="人物",
                        extraction_text="安娜·路易斯·斯特朗",
                        attributes={
                            "entity_description": "一位美国进步作家和记者，于一九四六年八月六日在延安会见了毛泽东。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="人物",
                        extraction_text="蒋介石",
                        attributes={"entity_description": "国民党反动派的代表，意图在美国的帮助下发动内战。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="组织",
                        extraction_text="美国政府",
                        attributes={"entity_description": "其态度和反动派的行动直接影响中国和平前景。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="地点",
                        extraction_text="中国",
                        attributes={
                            "entity_description": "毛泽东与斯特朗谈话的背景地，也是内战和“纸老虎”理论作用的场域。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="时间",
                        extraction_text="一九四六年八月六日",
                        attributes={"entity_description": "毛泽东与美国记者安娜·路易斯·斯特朗进行谈话的具体日期。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="事件",
                        extraction_text="毛泽东与安娜·路易斯·斯特朗的谈话",
                        attributes={
                            "entity_description": "一次重要的国际对话，毛泽东在此次谈话中提出了“一切反动派都是纸老虎”的著名论点。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="事件",
                        extraction_text="内战",
                        attributes={
                            "entity_description": "蒋介石在美国援助下试图发动的反人民战争，与中国人民争取和平的愿望相对立。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="群体",
                        extraction_text="美国人民",
                        attributes={
                            "entity_description": "被毛泽东寄予希望的力量，认为其能够阻止美国反动派对中国内战的干涉。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="群体",
                        extraction_text="美国反动派",
                        attributes={
                            "entity_description": "美国政府中支持蒋介石打内战的势力，被毛泽东视为“纸老虎”的一部分。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="群体",
                        extraction_text="人民",
                        attributes={"entity_description": "决定战争胜败的关键力量，最终将推翻反动派统治。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="群体",
                        extraction_text="革命者",
                        attributes={"entity_description": "在对敌斗争中应遵循“战略上藐视敌人，战术上重视敌人”原则的人。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="军事行动",
                        extraction_text="打内战",
                        attributes={"entity_description": "蒋介石在美国帮助下进行的旨在消灭人民力量的军事行动。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="思想概念与理论",
                        extraction_text="纸老虎",
                        attributes={
                            "entity_description": "毛泽东提出的著名论点，认为一切反动派从本质和长远来看是虚弱的，最终会被人民战胜。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="思想概念与理论",
                        extraction_text="战略上藐视敌人，战术上重视敌人",
                        attributes={"entity_description": "毛泽东提出的革命者在对敌斗争中应采取的基本策略思想。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="毛泽东指出一切反动派都是纸老虎。",
                        attributes={"entity1": "毛泽东", "entity2": "纸老虎", "strength": "10",
                                    "relationship_description": "毛泽东是“纸老虎”理论的提出者和核心阐释者。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="美国反动派帮助蒋介石打内战。",
                        attributes={"entity1": "美国反动派", "entity2": "蒋介石", "strength": "9",
                                    "relationship_description": "美国反动派向蒋介石提供援助，以支持其发动内战。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="美国人民能阻止美国反动派。",
                        attributes={"entity1": "美国人民", "entity2": "美国反动派", "strength": "8",
                                    "relationship_description": "毛泽东认为美国人民有力量阻止美国反动派的干涉行为，从而影响中国和平。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="反动派具有两重性。",
                        attributes={"entity1": "反动派", "entity2": "两重性", "strength": "10",
                                    "relationship_description": "“两重性”是毛泽东对反动派本质特征的哲学概括，即其既有强大的一面也有虚弱的一面。"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="革命者在战略上藐视敌人，在战术上重视敌人。",
                        attributes={"entity1": "革命者", "entity2": "战略上藐视敌人，战术上重视敌人", "strength": "9",
                                    "relationship_description": "这是革命者面对敌人时应遵循的基本斗争原则和策略。"}
                    )
                ]
            )
        ]

    @staticmethod
    def _format_extractions(
            extractions: List[lx.data.Extraction],
            tuple_delimiter: str = "<|>",
            record_delimiter: str = "##",
            completion_delimiter: str = "<|COMPLETE|>"
    ) -> str:
        if not extractions:
            return f"未能提取到任何信息。{completion_delimiter}"

        output_parts = []
        relationships = []
        entity_types = ["人物", "组织", "地点", "时间", "事件", "群体", "会议", "军事行动", "重大政策",
                        "思想概念与理论"]

        for ext in extractions:
            if ext.extraction_class in entity_types:
                description = ext.attributes.get("entity_description", "没有找到描述")
                record = (
                    f'("entity"{tuple_delimiter}'
                    f'{ext.extraction_text.upper()}{tuple_delimiter}'
                    f'{ext.extraction_class.upper()}{tuple_delimiter}'
                    f'{description})'
                )
                output_parts.append(record)
            elif ext.extraction_class == "relationship":
                relationships.append(ext)

        for rel in relationships:
            entity1 = rel.attributes.get("entity1", "其他")
            entity2 = rel.attributes.get("entity2", "其他")
            strength = rel.attributes.get("strength", "0")
            description = rel.extraction_text
            record = (
                f'("relationship"{tuple_delimiter}'
                f'{entity1.upper()}{tuple_delimiter}'
                f'{entity2.upper()}{tuple_delimiter}'
                f'{description}{tuple_delimiter}'
                f'{strength})'
            )
            output_parts.append(record)

        final_output = record_delimiter.join(output_parts)
        final_output += completion_delimiter
        return final_output

    def _run_sync_extraction(self, text: str) -> List[lx.data.Extraction]:
        """
        同步的包装函数，因为 lx.extract 是同步的。
        """
        result = lx.extract(
            text_or_documents=text,
            prompt_description=self.prompt_description,
            examples=self.examples,
            model_id="gemini-2.5-flash",
            api_key=self.api_key,
            use_schema_constraints=True,
            format_type=lx.data.FormatType.JSON,
            debug=False
        )
        return result.extractions

    async def extract_and_format(self, text: str) -> str:
        """
        异步方法，接收输入文本，返回最终格式化的字符串。
        """
        extractions = await asyncio.to_thread(self._run_sync_extraction, text)

        final_string = self._format_extractions(extractions)
        return final_string


async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("error：API key must be provided.")
        return
    extractor = LangExtractor(api_key=api_key)

    input_text = """
    中国迫切需要一个资产阶级的民主革命，这个革命必须由无产阶级领导才能完成。从广东出发向长江发展的一九二六年到一九二七年的革命，因为无产阶级没有坚决地执行自己的领导权，被买办豪绅阶级夺取了领导，以反革命代替了革命。资产阶级民主革命乃遭遇到暂时的失败。中国无产阶级和农民在此次失败中，受到很大的打击，中国资产阶级（非买办豪绅阶级）也受了打击。但最近数个月来，工农阶级在共产党领导之下的有组织的城市罢工和农村暴动，在南北各地发展起来。军阀军队中的士兵因饥寒而酝酿着很大的不安。同时资产阶级在汪精卫、陈公博一派鼓动之下，亦在沿海沿江各地发展着颇大的改良主义运动。这种运动的发展是新的事实。

    """
    final_output = await extractor.extract_and_format(input_text)
    print(final_output)


if __name__ == "__main__":
    asyncio.run(main())
