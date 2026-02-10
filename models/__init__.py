# -*- coding: utf-8 -*-
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class JobProfile(BaseModel):
    """岗位画像对象"""
    job_id: str
    job_title: str
    jd_text: str
    
    # 硬性约束
    min_education: Optional[str] = None  # 最低学历要求
    min_experience: Optional[int] = None  # 最低工作年限
    required_skills: List[str] = []       # 必须掌握的技能列表
    industry_background: Optional[str] = None  # 期望行业背景
    
    # 软性约束
    preferred_skills: List[str] = []      # 偏好技能列表
    soft_skills_keywords: List[str] = []  # 关键软技能关键词
    
    # 解析后的结构化信息
    parsed_requirements: Dict[str, Any] = {}


class ResumeProfile(BaseModel):
    """简历画像对象"""
    resume_id: str
    candidate_name: Optional[str] = None
    contact_info: Dict[str, str] = {}     # 联系方式
    
    # 统计属性
    total_experience_years: Optional[float] = None
    highest_education: Optional[str] = None
    recent_company: Optional[str] = None
    recent_position: Optional[str] = None
    
    # 教育背景
    education_history: List[Dict[str, Any]] = []
    
    # 工作经历
    work_experience: List[Dict[str, Any]] = []
    
    # 项目经验
    project_experience: List[Dict[str, Any]] = []
    
    # 技能列表
    skills: List[str] = []
    skills_with_confidence: Dict[str, float] = {}  # 技能及其置信度
    
    # 文本库（用于语义匹配）
    work_descriptions: str = ""
    project_descriptions: str = ""
    full_text: str = ""  # 所有文本的合集


class MatchResult(BaseModel):
    """匹配结果对象"""
    job_id: str
    resume_id: str
    total_score: float  # 总分(0-100)
    
    # 各维度评分
    hard_requirement_score: float = 0.0    # 硬性条件匹配分
    skill_match_score: float = 0.0         # 技能匹配分
    experience_relevance_score: float = 0.0 # 经验相关性分
    soft_skill_score: float = 0.0          # 软性素质分
    
    # 分析报告
    match_highlights: List[str] = []       # 匹配亮点
    missing_points: List[str] = []         # 缺失点
    recommendation: str = ""               # 推荐意见
    
    # 时间戳
    created_at: datetime = datetime.now()


class MatchAnalysisRequest(BaseModel):
    """匹配分析请求"""
    job_profile: JobProfile
    resume_profile: ResumeProfile


class JDAnalysisResponse(BaseModel):
    """JD分析响应"""
    job_profile: JobProfile
    analysis_result: Dict[str, Any]


class ResumeAnalysisResponse(BaseModel):
    """简历分析响应"""
    resume_profile: ResumeProfile
    analysis_result: Dict[str, Any]