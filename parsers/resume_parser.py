# -*- coding: utf-8 -*-
import pdfplumber
import docx
from PIL import Image
import pytesseract
import re
from typing import Dict, List
from models import ResumeProfile
import tempfile
import os


class ResumeParser:
    """简历解析器"""
    
    def __init__(self):
        # 联系信息正则表达式
        self.phone_pattern = r'(1[3-9]\d{9})'
        self.email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        
        # 教育背景关键词
        self.education_keywords = ['教育', '学历', '毕业', '学位', '学校']
        
        # 工作经历关键词
        self.work_keywords = ['工作', '经历', '经验', '公司', '职位', '岗位']
        
        # 项目经验关键词
        self.project_keywords = ['项目', '参与', '负责', '开发']

    def parse_resume(self, file_path: str, file_type: str) -> ResumeProfile:
        """解析简历文件"""
        resume_id = f"resume_{hash(file_path) % 10000}"
        
        resume_profile = ResumeProfile(resume_id=resume_id)
        
        # 根据文件类型选择解析方法
        if file_type == 'pdf':
            text_content = self._parse_pdf(file_path)
        elif file_type == 'docx':
            text_content = self._parse_docx(file_path)
        elif file_type in ['jpg', 'jpeg', 'png']:
            text_content = self._parse_image(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        # 提取基本信息
        self._extract_basic_info(resume_profile, text_content)
        
        # 提取教育背景
        self._extract_education(resume_profile, text_content)
        
        # 提取工作经历
        self._extract_work_experience(resume_profile, text_content)
        
        # 提取项目经验
        self._extract_project_experience(resume_profile, text_content)
        
        # 提取技能
        self._extract_skills(resume_profile, text_content)
        
        # 构建文本库
        self._build_text_corpus(resume_profile)
        
        return resume_profile

    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF解析错误: {e}")
        return text_content

    def _parse_docx(self, file_path: str) -> str:
        """解析Word文档"""
        try:
            doc = docx.Document(file_path)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            return text_content
        except Exception as e:
            print(f"Word文档解析错误: {e}")
            return ""

    def _parse_image(self, file_path: str) -> str:
        """解析图片文件（OCR）"""
        try:
            image = Image.open(file_path)
            # 转换为灰度图提高识别准确率
            image = image.convert('L')
            # 使用tesseract进行OCR识别
            text_content = pytesseract.image_to_string(image, lang='chi_sim+eng')
            return text_content
        except Exception as e:
            print(f"图片OCR解析错误: {e}")
            return ""

    def _extract_basic_info(self, profile: ResumeProfile, text: str):
        """提取基本信息"""
        # 提取姓名（通常是文本开头的中文姓名）
        name_matches = re.findall(r'^[\u4e00-\u9fa5]{2,4}', text.strip())
        if name_matches:
            profile.candidate_name = name_matches[0]
        
        # 提取手机号
        phone_matches = re.findall(self.phone_pattern, text)
        if phone_matches:
            profile.contact_info['phone'] = phone_matches[0]
        
        # 提取邮箱
        email_matches = re.findall(self.email_pattern, text)
        if email_matches:
            profile.contact_info['email'] = email_matches[0]

    def _extract_education(self, profile: ResumeProfile, text: str):
        """提取教育背景"""
        education_section = self._find_section(text, self.education_keywords)
        if education_section:
            # 简单的时间段提取（年-年格式）
            time_patterns = [
                r'(\d{4})\s*[-~至]\s*(\d{4}|至今)',
                r'(\d{4})年\s*[-~至]\s*(\d{4}|至今)年'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, education_section)
                if matches:
                    for start_year, end_year in matches:
                        profile.education_history.append({
                            'start_year': int(start_year),
                            'end_year': end_year if end_year == '至今' else int(end_year),
                            'description': education_section[:200]  # 截取前200字符
                        })
            
            # 计算最高学历
            profile.highest_education = self._determine_highest_education(education_section)

    def _extract_work_experience(self, profile: ResumeProfile, text: str):
        """提取工作经历"""
        work_section = self._find_section(text, self.work_keywords)
        if work_section:
            # 提取工作时间段
            time_patterns = [
                r'(\d{4})\s*[-~至]\s*(\d{4}|至今)',
                r'(\d{4})年\s*[-~至]\s*(\d{4}|至今)年'
            ]
            
            descriptions = work_section.split('\n')
            current_company = ""
            current_position = ""
            
            for desc in descriptions:
                # 提取公司名和职位
                if any(keyword in desc.lower() for keyword in ['公司', 'corp', 'ltd', 'limited']):
                    current_company = desc.strip()
                if any(keyword in desc.lower() for keyword in ['职位', '岗位', 'role', 'position']):
                    current_position = desc.strip()
                
                # 提取时间段
                for pattern in time_patterns:
                    time_match = re.search(pattern, desc)
                    if time_match:
                        start_year = int(time_match.group(1))
                        end_year = time_match.group(2)
                        if end_year == '至今':
                            end_year = 2024  # 当前年份
                        else:
                            end_year = int(end_year)
                        
                        profile.work_experience.append({
                            'company': current_company,
                            'position': current_position,
                            'start_year': start_year,
                            'end_year': end_year,
                            'description': desc.strip()
                        })
            
            # 设置最近工作信息
            if profile.work_experience:
                latest_job = profile.work_experience[-1]
                profile.recent_company = latest_job.get('company', '')
                profile.recent_position = latest_job.get('position', '')
                profile.total_experience_years = sum(
                    job['end_year'] - job['start_year'] for job in profile.work_experience
                )

    def _extract_project_experience(self, profile: ResumeProfile, text: str):
        """提取项目经验"""
        project_section = self._find_section(text, self.project_keywords)
        if project_section:
            # 简单按段落分割项目
            projects = project_section.split('\n\n')
            for project_desc in projects[:5]:  # 最多提取5个项目
                if len(project_desc.strip()) > 20:  # 过滤过短的内容
                    profile.project_experience.append({
                        'name': project_desc[:50],  # 项目名称（前50字符）
                        'description': project_desc
                    })

    def _extract_skills(self, profile: ResumeProfile, text: str):
        """提取技能"""
        # 大数据相关技能词汇
        common_skills = [
            # 大数据核心技能
            'hadoop', 'spark', 'flink', 'kafka', 'hive', 'hbase',
            'presto', 'clickhouse', 'doris', 'trino', 'impala',
            
            # 数据湖技术
            'delta lake', 'iceberg', 'hudi', 'lakehouse',
            
            # 云平台技能
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
            'javascript', 'c++', 'go',
            'mysql', 'postgresql', 'mongodb', 'redis',
            'react', 'vue', 'angular', 'spring', 'django',
            'linux', '机器学习', '数据分析', '项目管理', '团队协作'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
                profile.skills_with_confidence[skill] = 0.8  # 默认置信度
        
        profile.skills = list(set(found_skills))

    def _find_section(self, text: str, keywords: List[str]) -> str:
        """根据关键词找到对应的章节内容"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            # 检查是否进入目标章节
            if any(keyword in line_lower for keyword in keywords):
                in_section = True
                continue
            
            # 检查是否离开章节（遇到其他明显章节标题）
            if in_section and any(other_keyword in line_lower 
                                for other_keyword in ['个人', '自我', '评价', '总结']):
                break
                
            if in_section and line.strip():
                section_lines.append(line)
        
        return '\n'.join(section_lines)

    def _determine_highest_education(self, education_text: str) -> str:
        """确定最高学历"""
        education_levels = {
            '博士': ['博士', 'phd'],
            '硕士': ['硕士', '研究生'],
            '本科': ['本科', '学士', '大学'],
            '大专': ['大专', '专科']
        }
        
        text_lower = education_text.lower()
        for level, keywords in education_levels.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        return ""

    def _build_text_corpus(self, profile: ResumeProfile):
        """构建文本语料库用于语义匹配"""
        # 收集所有工作描述
        work_descriptions = []
        for work in profile.work_experience:
            if 'description' in work:
                work_descriptions.append(work['description'])
        profile.work_descriptions = '\n'.join(work_descriptions)
        
        # 收集所有项目描述
        project_descriptions = []
        for project in profile.project_experience:
            if 'description' in project:
                project_descriptions.append(project['description'])
        profile.project_descriptions = '\n'.join(project_descriptions)
        
        # 构建完整文本
        all_texts = [
            profile.work_descriptions,
            profile.project_descriptions,
            str(profile.education_history),
            str(profile.skills)
        ]
        profile.full_text = '\n'.join(filter(None, all_texts))