# -*- coding: utf-8 -*-
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv
from typing import Dict, Any, List


class ZhipuAIHelper:
    """智谱AI助手类"""
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('ZHIPU_API_KEY')
        if not api_key:
            raise ValueError("请设置ZHIPU_API_KEY环境变量")
        
        self.client = ZhipuAiClient(api_key=api_key)
        self.model_name = "glm-4"  # 使用GLM-4模型

    def analyze_semantic_similarity(self, job_description: str, 
                                  resume_text: str) -> Dict[str, Any]:
        """使用大模型分析语义相似度"""
        prompt = f"""
        请分析以下岗位描述和候选人简历的语义匹配度：
        
        岗位描述：
        {job_description}
        
        候选人简历：
        {resume_text}
        
        请从以下几个维度进行分析并给出0-100分的评分：
        1. 技术栈匹配度
        2. 业务场景相关性  
        3. 项目经验契合度
        4. 发展潜力匹配度
        
        输出格式要求：
        {{
            "technical_match": 85,
            "business_relevance": 78,
            "project_fit": 82,
            "potential_match": 90,
            "overall_score": 84,
            "key_strengths": ["技术能力强", "项目经验丰富"],
            "improvement_suggestions": ["可以加强XX技能"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return self._parse_json_response(response.choices[0].message.content)
        except Exception as e:
            print(f"大模型调用出错: {e}")
            return self._get_default_analysis()

    def extract_skills_with_context(self, text: str) -> List[Dict[str, Any]]:
        """使用大模型提取技能及其上下文信息"""
        prompt = f"""
        请从以下文本中提取技能信息，包括技能名称、熟练程度、使用场景：
        
        文本内容：
        {text}
        
        输出格式要求：
        [
            {{
                "skill": "Python",
                "proficiency": "熟练",
                "context": "用于数据分析和机器学习项目",
                "years_of_experience": 3
            }},
            {{
                "skill": "React",
                "proficiency": "精通", 
                "context": "前端开发框架，主导多个大型项目",
                "years_of_experience": 2
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return self._parse_json_array_response(response.choices[0].message.content)
        except Exception as e:
            print(f"技能提取出错: {e}")
            return []

    def generate_match_analysis_report(self, job_profile: Dict, 
                                     resume_profile: Dict,
                                     match_scores: Dict) -> str:
        """生成详细的匹配分析报告"""
        prompt = f"""
        基于以下信息，请生成一份专业的简历匹配分析报告：
        
        岗位信息：
        {job_profile}
        
        候选人信息：
        {resume_profile}
        
        匹配得分：
        {match_scores}
        
        请生成包含以下内容的分析报告：
        1. 总体匹配评价
        2. 核心优势分析
        3. 待提升方面
        4. 具体建议
        5. 面试重点关注问题
        
        报告应该专业、具体、有针对性，字数控制在500字以内。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"报告生成出错: {e}")
            return self._get_default_report()

    def optimize_jd_description(self, original_jd: str) -> str:
        """优化JD描述，使其更清晰明确"""
        prompt = f"""
        请优化以下职位描述，使其更加清晰、吸引人才：
        
        原始JD：
        {original_jd}
        
        优化要求：
        1. 突出核心职责和要求
        2. 明确技能要求层次（必须vs加分）
        3. 增强吸引力和公司优势
        4. 保持专业性和准确性
        
        请直接返回优化后的JD内容。
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"JD优化出错: {e}")
            return original_jd

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """解析JSON格式响应"""
        import json
        try:
            # 尝试提取JSON部分
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # 返回默认值
        return self._get_default_analysis()

    def _parse_json_array_response(self, response_text: str) -> List[Dict[str, Any]]:
        """解析JSON数组格式响应"""
        import json
        try:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return []

    def _get_default_analysis(self) -> Dict[str, Any]:
        """获取默认分析结果"""
        return {
            "technical_match": 75,
            "business_relevance": 70,
            "project_fit": 72,
            "potential_match": 78,
            "overall_score": 74,
            "key_strengths": ["基础技能符合要求"],
            "improvement_suggestions": ["建议深入了解业务场景"]
        }

    def _get_default_report(self) -> str:
        """获取默认报告"""
        return """
        候选人基本情况符合岗位要求，具备相关的技术基础和项目经验。
        在技能匹配度方面表现良好，建议在面试中重点考察实际项目能力和业务理解深度。
        总体来说是一个值得考虑的候选人。
        """