# -*- coding: utf-8 -*-
"""
大数据架构师专用匹配引擎
针对大数据架构师岗位特点优化的匹配算法
"""

import numpy as np
from typing import Dict, List
from models import JobProfile, ResumeProfile, MatchResult
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba


class BigDataMatchingEngine:
    """大数据架构师专用匹配引擎"""
    
    def __init__(self):
        # 针对大数据架构师的权重配置
        self.weights = {
            'hard_requirement': 0.25,    # 硬性条件权重（稍降低）
            'skill_match': 0.35,         # 技能匹配权重（提高）
            'experience_relevance': 0.25, # 经验相关性权重（提高）
            'soft_skill': 0.10,          # 软技能权重
            'achievements': 0.05         # 成就权重（新增）
        }
        
        # 学历等级映射
        self.education_hierarchy = {
            '博士': 5,
            '硕士': 4,
            '本科': 3,
            '大专': 2,
            '高中及以下': 1
        }
        
        # 大数据核心技术重要性权重
        self.bigdata_core_skills = {
            'hadoop': 1.2,
            'spark': 1.2,
            'flink': 1.1,
            'kafka': 1.1,
            'java': 1.1,
            'python': 1.0,
            'scala': 1.0,
            '架构设计': 1.3,
            '数据治理': 1.2,
            '平台建设': 1.2
        }

    def calculate_match_score(self, job_profile: JobProfile, 
                            resume_profile: ResumeProfile) -> MatchResult:
        """计算大数据架构师匹配度总分"""
        from datetime import datetime
        match_result = MatchResult(
            job_id=job_profile.job_id,
            resume_id=resume_profile.resume_id,
            total_score=0.0,
            created_at=datetime.now()
        )
        
        # 计算各维度分数
        hard_score = self._calculate_hard_requirement_score(job_profile, resume_profile)
        skill_score = self._calculate_bigdata_skill_match_score(job_profile, resume_profile)
        exp_score = self._calculate_experience_relevance_score(job_profile, resume_profile)
        soft_score = self._calculate_soft_skill_score(job_profile, resume_profile)
        achieve_score = self._calculate_achievement_score(job_profile, resume_profile)
        
        # 加权计算总分
        total_score = (
            hard_score * self.weights['hard_requirement'] +
            skill_score * self.weights['skill_match'] +
            exp_score * self.weights['experience_relevance'] +
            soft_score * self.weights['soft_skill'] +
            achieve_score * self.weights['achievements']
        )
        
        # 更新结果对象
        match_result.hard_requirement_score = hard_score
        match_result.skill_match_score = skill_score
        match_result.experience_relevance_score = exp_score
        match_result.soft_skill_score = soft_score
        match_result.total_score = round(total_score, 2)
        
        # 生成分析报告
        self._generate_bigdata_analysis_report(match_result, job_profile, resume_profile)
        
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
                score -= 25  # 学历不达标扣分
            elif resume_edu_level > job_edu_level:
                score += 3   # 学历超岀加分
        
        # 工作年限检查（大数据架构师通常要求更高经验）
        if job_profile.min_experience and resume_profile.total_experience_years:
            if resume_profile.total_experience_years < job_profile.min_experience:
                gap = job_profile.min_experience - resume_profile.total_experience_years
                score -= min(35, gap * 8)  # 最多扣35分
            elif resume_profile.total_experience_years > job_profile.min_experience:
                extra_years = resume_profile.total_experience_years - job_profile.min_experience
                score += min(8, extra_years * 1.5)  # 最多加8分
        
        return max(0, min(100, score))

    def _calculate_bigdata_skill_match_score(self, job_profile: JobProfile, 
                                           resume_profile: ResumeProfile) -> float:
        """计算大数据技能匹配分数（优化版）"""
        if not job_profile.required_skills and not job_profile.preferred_skills:
            return 85.0  # 大数据岗位通常有明确技能要求
        
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
        
        # 大数据核心技术加权
        core_skill_bonus = 0
        core_matched = 0
        total_core_skills = 0
        
        for skill, weight in self.bigdata_core_skills.items():
            if skill.lower() in [s.lower() for s in required_skills]:
                total_core_skills += 1
                if skill.lower() in [s.lower() for s in resume_skills]:
                    core_matched += 1
                    core_skill_bonus += (weight - 1.0) * 20  # 核心技能额外加分
        
        # 综合技能匹配度
        core_ratio = core_matched / total_core_skills if total_core_skills > 0 else 1.0
        skill_match_rate = required_match_rate * 0.7 + preferred_match_rate * 0.3
        
        # 转换为分数
        base_score = skill_match_rate * 100 + core_skill_bonus
        
        # 根据技能丰富度调整
        if len(resume_skills) >= len(required_skills) * 2:
            base_score += 3  # 技能丰富度加分
        elif len(resume_skills) < len(required_skills) * 0.5:
            base_score -= 8  # 技能不足扣分
        
        return max(0, min(100, base_score))

    def _calculate_experience_relevance_score(self, job_profile: JobProfile, 
                                            resume_profile: ResumeProfile) -> float:
        """计算经验相关性分数（大数据专项）"""
        if not resume_profile.work_descriptions and not resume_profile.project_descriptions:
            return 70.0  # 没有详细经验信息给中等分
        
        # 使用TF-IDF计算文本相似度
        job_text = job_profile.jd_text
        resume_text = resume_profile.full_text
        
        # 文本预处理
        job_tokens = ' '.join(jieba.cut(job_text))
        resume_tokens = ' '.join(jieba.cut(resume_text))
        
        if not job_tokens.strip() or not resume_tokens.strip():
            return 70.0
        
        # 计算TF-IDF相似度
        try:
            vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
            tfidf_matrix = vectorizer.fit_transform([job_tokens, resume_tokens])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            relevance_score = similarity * 100
        except:
            # 如果TF-IDF失败，使用简单的关键词匹配
            relevance_score = self._simple_bigdata_keyword_match(job_text, resume_text)
        
        # 大数据架构师经验加分
        bigdata_exp_bonus = self._calculate_bigdata_experience_bonus(resume_profile)
        relevance_score += bigdata_exp_bonus
        
        # 行业背景加分
        if (job_profile.industry_background and 
            job_profile.industry_background in resume_profile.full_text):
            relevance_score += 8
        
        return max(0, min(100, relevance_score))

    def _simple_bigdata_keyword_match(self, text1: str, text2: str) -> float:
        """大数据领域的关键词匹配算法"""
        # 提取大数据相关关键词
        bigdata_keywords = [
            '大数据', 'hadoop', 'spark', 'flink', 'kafka', 'hive', 'hbase',
            '数据湖', '数据治理', '数据仓库', 'etl', '架构设计', '平台建设',
            '数据处理', '实时计算', '批处理', '流处理'
        ]
        
        words1 = set(jieba.cut(text1.lower()))
        words2 = set(jieba.cut(text2.lower()))
        
        # 计算大数据关键词匹配度
        bigdata_matches = 0
        total_bigdata_keywords = 0
        
        for keyword in bigdata_keywords:
            if keyword in text1.lower():
                total_bigdata_keywords += 1
                if keyword in text2.lower():
                    bigdata_matches += 1
        
        if total_bigdata_keywords == 0:
            return 60.0  # 没有大数据关键词，给基础分
        
        match_rate = bigdata_matches / total_bigdata_keywords
        return match_rate * 100

    def _calculate_bigdata_experience_bonus(self, resume_profile: ResumeProfile) -> float:
        """计算大数据相关经验加分"""
        bonus = 0
        
        # 检查工作经历中的大数据相关性
        bigdata_work_count = sum(1 for work in resume_profile.work_experience 
                               if work.get('bigdata_related', False))
        if bigdata_work_count > 0:
            bonus += min(15, bigdata_work_count * 3)  # 最多15分加分
        
        # 检查项目经验中的大数据相关性
        bigdata_project_count = sum(1 for project in resume_profile.project_experience 
                                  if project.get('bigdata_related', False))
        if bigdata_project_count > 0:
            bonus += min(10, bigdata_project_count * 2)  # 最多10分加分
        
        return bonus

    def _calculate_soft_skill_score(self, job_profile: JobProfile, 
                                  resume_profile: ResumeProfile) -> float:
        """计算软技能匹配分数"""
        if not job_profile.soft_skills_keywords:
            return 85.0  # 大数据架构师对软技能要求较高
        
        job_soft_skills = set(job_profile.soft_skills_keywords)
        resume_full_text = resume_profile.full_text.lower()
        
        matched_count = 0
        total_count = len(job_soft_skills)
        
        for skill in job_soft_skills:
            if skill.lower() in resume_full_text:
                matched_count += 1
        
        if total_count == 0:
            return 85.0
        
        match_rate = matched_count / total_count
        score = match_rate * 100
        
        # 团队管理和领导经验加分
        leadership_keywords = ['团队', '管理', '领导', '带领', '负责']
        if any(keyword in resume_full_text for keyword in leadership_keywords):
            score += 5
        
        # 技术文档和分享经验加分
        tech_doc_keywords = ['文档', '分享', '培训', '演讲', '技术博客']
        if any(keyword in resume_full_text for keyword in tech_doc_keywords):
            score += 3
        
        return max(0, min(100, score))

    def _calculate_achievement_score(self, job_profile: JobProfile, 
                                   resume_profile: ResumeProfile) -> float:
        """计算成就分数（大数据架构师特有）"""
        achievements = list(resume_profile.skills_with_confidence.keys())
        achievement_score = 70.0  # 基础分
        
        # 专利加分
        patents = [a for a in achievements if '专利' in a or 'cn' in a.lower()]
        achievement_score += len(patents) * 8
        
        # 论文著作加分
        publications = [a for a in achievements if '论文' in a or '著作' in a or 'ei' in a.lower()]
        achievement_score += len(publications) * 6
        
        # 开源贡献加分
        oss_contributions = [a for a in achievements if '开源' in a or 'github' in a.lower()]
        achievement_score += len(oss_contributions) * 5
        
        # 技术影响力加分
        influence_keywords = ['社区', '分享', '演讲', '培训']
        influence_count = sum(1 for keyword in influence_keywords 
                            if any(keyword in a.lower() for a in achievements))
        achievement_score += influence_count * 3
        
        return max(0, min(100, achievement_score))

    def _generate_bigdata_analysis_report(self, match_result: MatchResult, 
                                        job_profile: JobProfile, 
                                        resume_profile: ResumeProfile):
        """生成大数据架构师专项分析报告"""
        highlights = []
        missing_points = []
        
        # 分析硬性条件
        if match_result.hard_requirement_score >= 85:
            highlights.append("学历和经验完全符合要求")
        elif match_result.hard_requirement_score >= 70:
            highlights.append("基本满足硬性条件要求")
        else:
            missing_points.append("学历或工作经验不满足最低要求")
        
        # 分析技能匹配
        if match_result.skill_match_score >= 90:
            highlights.append("大数据核心技术掌握全面，技能匹配度极高")
        elif match_result.skill_match_score >= 75:
            highlights.append("具备扎实的大数据技术基础")
        else:
            missing_points.append("大数据核心技能有待加强")
        
        # 分析经验相关性
        if match_result.experience_relevance_score >= 85:
            highlights.append("具有丰富的相关项目经验")
        elif match_result.experience_relevance_score >= 70:
            highlights.append("具备一定的相关工作经验")
        else:
            missing_points.append("缺乏足够的大数据项目实践经验")
        
        # 分析成就
        achievements = list(resume_profile.skills_with_confidence.keys())
        patent_count = len([a for a in achievements if '专利' in a])
        paper_count = len([a for a in achievements if '论文' in a or '著作' in a])
        
        if patent_count > 0:
            highlights.append(f"拥有{patent_count}项技术专利")
        if paper_count > 0:
            highlights.append(f"发表{paper_count}篇学术论文或技术著作")
        
        # 生成推荐意见
        total_score = match_result.total_score
        if total_score >= 92:
            recommendation = "🌟 强烈推荐！候选人各项指标都非常优秀，是理想的大数据架构师人选"
        elif total_score >= 85:
            recommendation = "👍 高度推荐！候选人综合素质优秀，具备成为优秀大数据架构师的潜质"
        elif total_score >= 75:
            recommendation = "👌 推荐！候选人基本符合条件，建议安排技术面试深入了解"
        elif total_score >= 65:
            recommendation = "🤔 待定！候选人有一定基础，但某些方面还需提升，建议谨慎考虑"
        else:
            recommendation = "👎 不推荐！候选人与大数据架构师岗位要求差距较大"
        
        match_result.match_highlights = highlights
        match_result.missing_points = missing_points
        match_result.recommendation = recommendation