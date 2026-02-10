# -*- coding: utf-8 -*-
"""
大数据架构师专用简历解析器
针对大数据架构师简历的特点进行优化解析
"""

import re
from typing import Dict, List
from models import ResumeProfile
import tempfile
import os


class BigDataResumeParser:
    """大数据架构师专用简历解析器"""
    
    def __init__(self):
        # 联系信息正则表达式
        self.phone_pattern = r'(1[3-9]\d{9})'
        self.email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        
        # 大数据架构师特定关键词
        self.bigdata_keywords = {
            'platforms': ['hadoop', 'spark', 'flink', 'kafka', 'hive', 'hbase', 'presto'],
            'datalake': ['delta lake', 'iceberg', 'hudi', 'lakehouse'],
            'cloud': ['aws', 'emr', 'azure', 'databricks', '阿里云', '腾讯云', '华为云'],
            'architecture': ['架构设计', '平台建设', '系统架构', '技术架构'],
            'governance': ['数据治理', '元数据管理', '数据质量', '主数据管理'],
            'patents': ['专利', '发明', 'cn\d+', '专利授权'],
            'publications': ['论文', '著作', 'ei', 'sci', '软著'],
            'open_source': ['开源', 'github', 'apache', '社区贡献']
        }

    def parse_resume(self, file_path: str, file_type: str) -> ResumeProfile:
        """解析大数据架构师简历"""
        resume_id = f"bd_resume_{hash(file_path) % 10000}"
        
        resume_profile = ResumeProfile(resume_id=resume_id)
        
        # 根据文件类型选择解析方法
        if file_type == 'pdf':
            text_content = self._parse_pdf(file_path)
        elif file_type == 'docx':
            text_content = self._parse_docx(file_path)
        elif file_type in ['jpg', 'jpeg', 'png']:
            text_content = self._parse_image(file_path)
        elif file_type == 'md':
            text_content = self._parse_markdown(file_path)
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
        
        # 提取大数据相关技能
        self._extract_bigdata_skills(resume_profile, text_content)
        
        # 提取专利著作等成就
        self._extract_achievements(resume_profile, text_content)
        
        # 构建文本库
        self._build_text_corpus(resume_profile)
        
        return resume_profile

    def _parse_markdown(self, file_path: str) -> str:
        """解析Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Markdown解析错误: {e}")
            return ""

    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        text_content = ""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF解析错误: {e}")
        return text_content

    def _parse_docx(self, file_path: str) -> str:
        """解析Word文档"""
        try:
            import docx
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
            from PIL import Image
            import pytesseract
            image = Image.open(file_path)
            image = image.convert('L')
            text_content = pytesseract.image_to_string(image, lang='chi_sim+eng')
            return text_content
        except Exception as e:
            print(f"图片OCR解析错误: {e}")
            return ""

    def _extract_basic_info(self, profile: ResumeProfile, text: str):
        """提取基本信息"""
        # 提取姓名
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
        education_keywords = ['教育', '学历', '毕业', '学位', '学校']
        education_section = self._find_section(text, education_keywords)
        
        if education_section:
            # 简单的时间段提取
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
                            'description': education_section[:200]
                        })
            
            # 计算最高学历
            profile.highest_education = self._determine_highest_education(education_section)

    def _extract_work_experience(self, profile: ResumeProfile, text: str):
        """提取工作经历（特别关注大数据相关经验）"""
        work_keywords = ['工作', '经历', '经验', '公司', '职位', '岗位']
        work_section = self._find_section(text, work_keywords)
        
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
                            end_year = 2024
                        
                        # 特别标记大数据相关的工作经验
                        is_bigdata_related = self._is_bigdata_experience(desc)
                        
                        profile.work_experience.append({
                            'company': current_company,
                            'position': current_position,
                            'start_year': start_year,
                            'end_year': int(end_year) if isinstance(end_year, str) and end_year.isdigit() else end_year,
                            'description': desc.strip(),
                            'bigdata_related': is_bigdata_related
                        })
            
            # 设置最近工作信息
            if profile.work_experience:
                latest_job = profile.work_experience[-1]
                profile.recent_company = latest_job.get('company', '')
                profile.recent_position = latest_job.get('position', '')
                profile.total_experience_years = sum(
                    job['end_year'] - job['start_year'] for job in profile.work_experience
                )

    def _is_bigdata_experience(self, description: str) -> bool:
        """判断是否为大数据相关工作经验"""
        bigdata_terms = [
            '大数据', 'hadoop', 'spark', '数据平台', '数据架构', 
            '数据治理', '数据湖', 'etl', '数据仓库', '数据处理'
        ]
        desc_lower = description.lower()
        return any(term in desc_lower for term in bigdata_terms)

    def _extract_project_experience(self, profile: ResumeProfile, text: str):
        """提取项目经验"""
        project_keywords = ['项目', '参与', '负责', '开发', '设计']
        project_section = self._find_section(text, project_keywords)
        
        if project_section:
            projects = project_section.split('\n\n')
            for project_desc in projects[:8]:  # 提取更多项目
                if len(project_desc.strip()) > 30:  # 过滤过短的内容
                    # 判断是否为大数据相关项目
                    is_bigdata_project = self._is_bigdata_project(project_desc)
                    
                    profile.project_experience.append({
                        'name': project_desc[:100],
                        'description': project_desc,
                        'bigdata_related': is_bigdata_project
                    })

    def _is_bigdata_project(self, description: str) -> bool:
        """判断是否为大数据相关项目"""
        bigdata_project_terms = [
            '大数据平台', '数据湖', '数据治理', 'hadoop', 'spark', 'flink',
            '数据仓库', 'etl', '数据处理', '数据架构', '湖仓一体'
        ]
        desc_lower = description.lower()
        return any(term in desc_lower for term in bigdata_project_terms)

    def _extract_bigdata_skills(self, profile: ResumeProfile, text: str):
        """提取大数据相关技能"""
        # 大数据技术栈
        bigdata_skills = [
            # 核心组件
            'hadoop', 'spark', 'flink', 'kafka', 'hive', 'hbase',
            'presto', 'clickhouse', 'doris', 'trino', 'impala',
            
            # 数据湖技术
            'delta lake', 'iceberg', 'hudi', 'lakehouse',
            
            # 云平台
            'aws', 'emr', 's3', 'redshift', 'azure', 'databricks',
            '阿里云', '腾讯云', '华为云', 'maxcompute',
            
            # 编程语言
            'java', 'python', 'scala', 'sql',
            
            # 容器化与DevOps
            'docker', 'kubernetes', 'helm', 'jenkins',
            
            # 调度与监控
            'airflow', 'dolphinscheduler', 'linkis',
            'prometheus', 'grafana', 'elk'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in bigdata_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
                profile.skills_with_confidence[skill] = 0.9  # 大数据技能给高置信度
        
        profile.skills = list(set(found_skills))

    def _extract_achievements(self, profile: ResumeProfile, text: str):
        """提取专利、著作、开源贡献等成就"""
        achievements = []
        
        # 检查专利
        patent_patterns = [r'专利.*?(cn\d+)', r'(cn\d+).*?专利', r'发明专利']
        for pattern in patent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                achievements.extend([f"专利: {match}" for match in matches])
        
        # 检查论文著作
        publication_terms = ['ei论文', 'sci论文', '著作', '软著', '清华大学出版社']
        for term in publication_terms:
            if term in text:
                achievements.append(f"学术成果: {term}")
        
        # 检查开源贡献
        oss_terms = ['开源', 'github', 'apache', '社区贡献', 'pr提交']
        for term in oss_terms:
            if term in text:
                achievements.append(f"开源贡献: {term}")
        
        # 将成就添加到技能置信度中
        for achievement in achievements:
            profile.skills_with_confidence[achievement] = 1.0

    def _find_section(self, text: str, keywords: List[str]) -> str:
        """根据关键词找到对应的章节内容"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in keywords):
                in_section = True
                continue
                
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
        work_descriptions = []
        for work in profile.work_experience:
            if 'description' in work:
                work_descriptions.append(work['description'])
        profile.work_descriptions = '\n'.join(work_descriptions)
        
        project_descriptions = []
        for project in profile.project_experience:
            if 'description' in project:
                project_descriptions.append(project['description'])
        profile.project_descriptions = '\n'.join(project_descriptions)
        
        all_texts = [
            profile.work_descriptions,
            profile.project_descriptions,
            str(profile.education_history),
            str(profile.skills),
            str(list(profile.skills_with_confidence.keys()))
        ]
        profile.full_text = '\n'.join(filter(None, all_texts))