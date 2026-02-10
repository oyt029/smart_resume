# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from typing import Dict, Any, List


class ZhipuAIHelper:
    """智谱AI助手类（简化版）"""
    
    def __init__(self):
        load_dotenv()
        # 简化版本暂时不使用真实的API调用
        self.api_key = os.getenv('ZHIPU_API_KEY')
        if not self.api_key:
            print("警告：未设置ZHIPU_API_KEY，将使用模拟数据")
        
    def analyze_semantic_similarity(self, job_description: str, 
                                  resume_text: str) -> Dict[str, Any]:
        """模拟语义相似度分析"""
        # 简化版本返回模拟数据
        return {
            "technical_match": 85,
            "business_relevance": 78,
            "project_fit": 82,
            "potential_match": 90,
            "overall_score": 84,
            "key_strengths": ["技术能力强", "项目经验丰富"],
            "improvement_suggestions": ["可以加强XX技能"]
        }

    def extract_skills_with_context(self, text: str) -> List[Dict[str, Any]]:
        """模拟技能提取"""
        # 简化版本返回空列表，让基础算法处理
        return []

    def generate_match_analysis_report(self, job_profile: Dict, 
                                     resume_profile: Dict,
                                     match_scores: Dict) -> str:
        """生成模拟分析报告"""
        return """
        基于系统分析，候选人与岗位匹配度较高。
        
        优势：
        • 技术栈匹配良好
        • 项目经验丰富
        • 学历符合要求
        
        建议：
        • 可进一步了解具体业务场景经验
        • 建议面试中重点考察实际能力
        
        总体推荐指数：★★★★☆
        """

    def optimize_jd_description(self, original_jd: str) -> str:
        """模拟JD优化"""
        return original_jd

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