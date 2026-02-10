# -*- coding: utf-8 -*-
import re
from typing import Dict, List, Tuple
from models import JobProfile
import jieba


class JDParser:
    """岗位需求解析器"""
    
    def __init__(self):
        # 学历关键词映射
        self.education_keywords = {
            '博士': ['博士', 'phd', 'doctorate'],
            '硕士': ['硕士', '研究生', 'master'],
            '本科': ['本科', '学士', 'bachelor', '大学'],
            '大专': ['大专', '专科', 'college']
        }
        
        # 技能等级关键词
        self.skill_levels = {
            'must': ['必须', '要求', '精通', '熟练掌握', '必备', 'required', 'proficient'],
            'preferred': ['优先', '加分', '熟悉', '了解', 'prefer', 'familiar'],
            'bonus': ['会更好', '优势', '经验', 'experience']
        }
        
        # 工作年限模式
        self.experience_patterns = [
            r'(\d+)\s*年.*经验',
            r'经验.*(\d+)\s*年',
            r'(\d+)\s*年以上',
            r'至少.*(\d+)\s*年'
        ]

    def parse_jd(self, jd_text: str, job_title: str = "") -> JobProfile:
        """解析JD文本，生成岗位画像"""
        job_id = f"job_{hash(jd_text) % 10000}"
        
        job_profile = JobProfile(
            job_id=job_id,
            job_title=job_title,
            jd_text=jd_text
        )
        
        # 提取硬性指标
        job_profile.min_education = self._extract_education(jd_text)
        job_profile.min_experience = self._extract_experience(jd_text)
        
        # 提取技能要求
        skills_data = self._extract_skills(jd_text)
        job_profile.required_skills = skills_data['required']
        job_profile.preferred_skills = skills_data['preferred']
        
        # 提取行业背景
        job_profile.industry_background = self._extract_industry(jd_text)
        
        # 提取软技能关键词
        job_profile.soft_skills_keywords = self._extract_soft_skills(jd_text)
        
        # 结构化解析结果
        job_profile.parsed_requirements = {
            'education': job_profile.min_education,
            'experience': job_profile.min_experience,
            'required_skills': job_profile.required_skills,
            'preferred_skills': job_profile.preferred_skills,
            'industry': job_profile.industry_background,
            'soft_skills': job_profile.soft_skills_keywords
        }
        
        return job_profile

    def _extract_education(self, text: str) -> str:
        """提取学历要求"""
        text_lower = text.lower()
        
        for edu_level, keywords in self.education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return edu_level
        return ""

    def _extract_experience(self, text: str) -> int:
        """提取工作年限要求"""
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # 返回最大的年限要求
                years = [int(match) for match in matches if match.isdigit()]
                return max(years) if years else 0
        return 0

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """提取技能要求"""
        required_skills = []
        preferred_skills = []
        
        # 大数据相关技术技能词汇
        tech_skills = [
            # 大数据核心组件
            'hadoop', 'spark', 'flink', 'kafka', 'hive', 'hbase',
            'presto', 'clickhouse', 'doris', 'trino', 'impala',
            
            # 数据湖相关
            'delta lake', 'iceberg', 'hudi', 'lakehouse',
            
            # 云平台
            'aws', 'emr', 's3', 'redshift', 'azure', 'databricks',
            '阿里云', '腾讯云', '华为云', 'maxcompute',
            
            # 编程语言
            'java', 'python', 'scala', 'sql', 'shell',
            
            # 容器化与DevOps
            'docker', 'kubernetes', 'helm', 'jenkins', 'gitlab ci',
            
            # 调度与监控
            'airflow', 'dolphinscheduler', 'linkis',
            'prometheus', 'grafana', 'elk',
            
            # 传统技能
            'javascript', 'c++', 'go', 'rust',
            'mysql', 'postgresql', 'mongodb', 'redis',
            'react', 'vue', 'angular', 'node.js', 'spring',
            'gcp', 'tensorflow', 'pytorch', 'machine learning', 'ai',
            'git', 'linux', 'nginx', 'apache'
        ]
        
        text_lower = text.lower()
        
        # 根据上下文判断技能等级
        for skill in tech_skills:
            if skill in text_lower:
                # 判断是必需还是优选
                context_window = self._get_context_window(text_lower, skill)
                if any(keyword in context_window for keyword in self.skill_levels['must']):
                    required_skills.append(skill)
                elif any(keyword in context_window for keyword in self.skill_levels['preferred']):
                    preferred_skills.append(skill)
                else:
                    # 默认加入优选技能
                    preferred_skills.append(skill)
        
        return {
            'required': list(set(required_skills)),
            'preferred': list(set(preferred_skills))
        }

    def _get_context_window(self, text: str, keyword: str, window_size: int = 20) -> str:
        """获取关键词前后文"""
        pos = text.find(keyword)
        if pos == -1:
            return ""
        
        start = max(0, pos - window_size)
        end = min(len(text), pos + len(keyword) + window_size)
        return text[start:end]

    def _extract_industry(self, text: str) -> str:
        """提取行业背景要求"""
        industries = [
            '互联网', '金融', '电商', '教育', '医疗', '游戏',
            '人工智能', '大数据', '云计算', '区块链'
        ]
        
        for industry in industries:
            if industry in text:
                return industry
        return ""

    def _extract_soft_skills(self, text: str) -> List[str]:
        """提取软技能关键词"""
        soft_skill_keywords = [
            '沟通能力', '团队合作', '领导力', '项目管理',
            '学习能力', '抗压能力', '责任心', '执行力',
            'problem solving', 'teamwork', 'leadership',
            'communication', 'adaptability'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in soft_skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))