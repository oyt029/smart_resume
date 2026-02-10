# -*- coding: utf-8 -*-
import numpy as np
from typing import Dict, List
from models import JobProfile, ResumeProfile, MatchResult
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba


class MatchingEngine:
    """人岗匹配算法引擎"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            'hard_requirement': 0.3,    # 硬性条件权重
            'skill_match': 0.4,         # 技能匹配权重
            'experience_relevance': 0.2, # 经验相关性权重
            'soft_skill': 0.1           # 软技能权重
        }
        
        # 学历等级映射
        self.education_hierarchy = {
            '博士': 5,
            '硕士': 4,
            '本科': 3,
            '大专': 2,
            '高中及以下': 1
        }

    def calculate_match_score(self, job_profile: JobProfile, 
                            resume_profile: ResumeProfile) -> MatchResult:
        """计算匹配度总分"""
        from datetime import datetime
        match_result = MatchResult(
            job_id=job_profile.job_id,
            resume_id=resume_profile.resume_id,
            total_score=0.0,
            created_at=datetime.now()
        )
        
        # 计算各维度分数
        hard_score = self._calculate_hard_requirement_score(job_profile, resume_profile)
        skill_score = self._calculate_skill_match_score(job_profile, resume_profile)
        exp_score = self._calculate_experience_relevance_score(job_profile, resume_profile)
        soft_score = self._calculate_soft_skill_score(job_profile, resume_profile)
        
        # 加权计算总分
        total_score = (
            hard_score * self.weights['hard_requirement'] +
            skill_score * self.weights['skill_match'] +
            exp_score * self.weights['experience_relevance'] +
            soft_score * self.weights['soft_skill']
        )
        
        # 更新结果对象
        match_result.hard_requirement_score = hard_score
        match_result.skill_match_score = skill_score
        match_result.experience_relevance_score = exp_score
        match_result.soft_skill_score = soft_score
        match_result.total_score = round(total_score, 2)
        
        # 生成分析报告
        self._generate_analysis_report(match_result, job_profile, resume_profile)
        
        return match_result

    def _calculate_hard_requirement_score(self, job_profile: JobProfile, 
                                        resume_profile: ResumeProfile) -> float:
        """计算硬性条件匹配分数"""
        score = 100.0
        
        # 学历要求检查
        if job_profile.min_education and resume_profile.highest_education:
            job_edu_level = self.education_hierarchy.get(job_profile.min_education, 0)
            resume_edu_level = self.education_hierarchy.get(resume_profile.highest_education, 0)
            
            if resume_edu_level < job_edu_level:
                score -= 30  # 学历不达标大幅扣分
            elif resume_edu_level > job_edu_level:
                score += 5   # 学历超岀适当加分
        
        # 工作年限检查
        if job_profile.min_experience and resume_profile.total_experience_years:
            if resume_profile.total_experience_years < job_profile.min_experience:
                # 年限不足，按差距比例扣分
                gap = job_profile.min_experience - resume_profile.total_experience_years
                score -= min(40, gap * 10)  # 最多扣40分
            elif resume_profile.total_experience_years > job_profile.min_experience:
                # 年限超出适当加分
                extra_years = resume_profile.total_experience_years - job_profile.min_experience
                score += min(10, extra_years * 2)  # 最多加10分
        
        return max(0, min(100, score))

    def _calculate_skill_match_score(self, job_profile: JobProfile, 
                                   resume_profile: ResumeProfile) -> float:
        """计算技能匹配分数"""
        if not job_profile.required_skills and not job_profile.preferred_skills:
            return 80.0  # 如果没有明确技能要求，给基础分
        
        # 必备技能匹配
        required_skills = set(job_profile.required_skills)
        resume_skills = set(resume_profile.skills)
        
        if not required_skills:
            required_match_rate = 1.0
        else:
            required_match_count = len(required_skills.intersection(resume_skills))
            required_match_rate = required_match_count / len(required_skills)
        
        # 优选技能匹配
        preferred_skills = set(job_profile.preferred_skills)
        if not preferred_skills:
            preferred_match_rate = 1.0
        else:
            preferred_match_count = len(preferred_skills.intersection(resume_skills))
            preferred_match_rate = preferred_match_count / len(preferred_skills)
        
        # 综合技能匹配度（必备技能占70%，优选技能占30%）
        skill_match_rate = required_match_rate * 0.7 + preferred_match_rate * 0.3
        
        # 转换为分数（0-100）
        base_score = skill_match_rate * 100
        
        # 根据技能数量适当调整
        if len(resume_skills) >= len(required_skills) * 2:
            base_score += 5  # 技能丰富度加分
        elif len(resume_skills) < len(required_skills) * 0.5:
            base_score -= 10  # 技能过少扣分
        
        return max(0, min(100, base_score))

    def _calculate_experience_relevance_score(self, job_profile: JobProfile, 
                                            resume_profile: ResumeProfile) -> float:
        """计算经验相关性分数"""
        if not resume_profile.work_descriptions and not resume_profile.project_descriptions:
            return 60.0  # 没有经验信息给基础分
        
        # 使用TF-IDF计算文本相似度
        job_text = job_profile.jd_text
        resume_text = resume_profile.full_text
        
        # 文本预处理
        job_tokens = ' '.join(jieba.cut(job_text))
        resume_tokens = ' '.join(jieba.cut(resume_text))
        
        if not job_tokens.strip() or not resume_tokens.strip():
            return 60.0
        
        # 计算TF-IDF相似度
        try:
            vectorizer = TfidfVectorizer(max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([job_tokens, resume_tokens])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            relevance_score = similarity * 100
        except:
            # 如果TF-IDF失败，使用简单的关键词匹配
            relevance_score = self._simple_keyword_match(job_text, resume_text)
        
        # 行业背景加分
        if (job_profile.industry_background and 
            job_profile.industry_background in resume_profile.full_text):
            relevance_score += 10
        
        return max(0, min(100, relevance_score))

    def _simple_keyword_match(self, text1: str, text2: str) -> float:
        """简单的关键词匹配算法"""
        # 提取关键词
        words1 = set(jieba.cut(text1.lower()))
        words2 = set(jieba.cut(text2.lower()))
        
        # 移除停用词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 50.0
        
        # 计算交集比例
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        similarity = intersection / union if union > 0 else 0
        
        return similarity * 100

    def _calculate_soft_skill_score(self, job_profile: JobProfile, 
                                  resume_profile: ResumeProfile) -> float:
        """计算软技能匹配分数"""
        if not job_profile.soft_skills_keywords:
            return 80.0  # 没有软技能要求给基础分
        
        job_soft_skills = set(job_profile.soft_skills_keywords)
        resume_full_text = resume_profile.full_text.lower()
        
        matched_count = 0
        total_count = len(job_soft_skills)
        
        for skill in job_soft_skills:
            if skill.lower() in resume_full_text:
                matched_count += 1
        
        if total_count == 0:
            return 80.0
        
        match_rate = matched_count / total_count
        score = match_rate * 100
        
        # 自我评价加分
        if '自我评价' in resume_profile.full_text or '个人总结' in resume_profile.full_text:
            score += 5
        
        return max(0, min(100, score))

    def _generate_analysis_report(self, match_result: MatchResult, 
                                job_profile: JobProfile, 
                                resume_profile: ResumeProfile):
        """生成分析报告"""
        highlights = []
        missing_points = []
        
        # 分析硬性条件
        if match_result.hard_requirement_score >= 80:
            highlights.append("满足岗位基本要求")
        elif match_result.hard_requirement_score >= 60:
            missing_points.append("部分硬性条件有待提升")
        else:
            missing_points.append("硬性条件不符合要求")
        
        # 分析技能匹配
        if match_result.skill_match_score >= 80:
            highlights.append("技能匹配度高")
        elif match_result.skill_match_score >= 60:
            missing_points.append("技能匹配一般，建议补充相关技能")
        else:
            missing_points.append("技能匹配度较低")
        
        # 分析经验相关性
        if match_result.experience_relevance_score >= 80:
            highlights.append("工作经验高度相关")
        elif match_result.experience_relevance_score >= 60:
            missing_points.append("工作经验相关性一般")
        else:
            missing_points.append("工作经验相关性较低")
        
        # 生成推荐意见
        total_score = match_result.total_score
        if total_score >= 90:
            recommendation = "强烈推荐，候选人非常符合岗位要求"
        elif total_score >= 80:
            recommendation = "推荐，候选人基本符合岗位要求"
        elif total_score >= 60:
            recommendation = "待定，建议进一步了解或面试评估"
        else:
            recommendation = "不推荐，候选人与岗位匹配度较低"
        
        match_result.match_highlights = highlights
        match_result.missing_points = missing_points
        match_result.recommendation = recommendation