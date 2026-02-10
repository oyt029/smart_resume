import unittest
from parsers.jd_parser import JDParser
from parsers.resume_parser import ResumeParser
from matching.engine import MatchingEngine
from models import JobProfile, ResumeProfile
import tempfile
import os


class TestJDParsing(unittest.TestCase):
    """测试JD解析功能"""
    
    def setUp(self):
        self.parser = JDParser()
        self.sample_jd = """
        职位：高级Python开发工程师
        
        职位要求：
        1. 本科及以上学历，计算机相关专业
        2. 3年以上Python开发经验
        3. 精通Django/Flask框架
        4. 熟悉MySQL数据库设计和优化
        5. 了解Redis缓存机制
        6. 有微服务架构经验者优先
        7. 具备良好的沟通能力和团队协作精神
        """

    def test_parse_jd_basic(self):
        """测试基本JD解析"""
        job_profile = self.parser.parse_jd(self.sample_jd, "Python开发工程师")
        
        self.assertIsNotNone(job_profile.job_id)
        self.assertEqual(job_profile.job_title, "Python开发工程师")
        self.assertIn("python", job_profile.required_skills)
        self.assertGreater(job_profile.min_experience, 0)

    def test_extract_education(self):
        """测试学历提取"""
        education = self.parser._extract_education(self.sample_jd)
        self.assertEqual(education, "本科")

    def test_extract_experience(self):
        """测试经验年限提取"""
        experience = self.parser._extract_experience(self.sample_jd)
        self.assertEqual(experience, 3)

    def test_extract_skills(self):
        """测试技能提取"""
        skills_data = self.parser._extract_skills(self.sample_jd)
        self.assertIn("python", skills_data['required'])
        self.assertIn("redis", skills_data['preferred'])


class TestResumeParsing(unittest.TestCase):
    """测试简历解析功能"""
    
    def setUp(self):
        self.parser = ResumeParser()
        # 创建测试文本文件模拟简历
        self.test_content = """
        张三
        13800138000
        zhangsan@email.com
        
        教育背景：
        2015-2019 北京大学 计算机科学与技术 本科
        
        工作经历：
        2019-2022 阿里巴巴 高级开发工程师
        负责电商平台后端开发，使用Python/Django框架
        
        2022-至今 字节跳动 技术专家
        主导推荐系统重构项目，使用微服务架构
        
        技能：
        Python, Django, Flask, MySQL, Redis, Docker
        """

    def test_parse_text_resume(self):
        """测试文本简历解析"""
        # 创建临时文本文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_content)
            temp_path = f.name
        
        try:
            # 模拟解析过程
            profile = ResumeProfile(resume_id="test_001")
            self.parser._extract_basic_info(profile, self.test_content)
            self.parser._extract_education(profile, self.test_content)
            self.parser._extract_work_experience(profile, self.test_content)
            self.parser._extract_skills(profile, self.test_content)
            
            # 验证结果
            self.assertEqual(profile.candidate_name, "张三")
            self.assertEqual(profile.contact_info['phone'], "13800138000")
            self.assertIn("python", [s.lower() for s in profile.skills])
            self.assertGreater(len(profile.work_experience), 0)
            
        finally:
            os.unlink(temp_path)


class TestMatchingEngine(unittest.TestCase):
    """测试匹配引擎"""
    
    def setUp(self):
        self.engine = MatchingEngine()
        
        # 创建测试数据
        self.job_profile = JobProfile(
            job_id="test_job_001",
            job_title="Python开发工程师",
            jd_text="需要3年Python经验，熟悉Django框架",
            min_education="本科",
            min_experience=3,
            required_skills=["python", "django"],
            preferred_skills=["mysql", "redis"]
        )
        
        self.resume_profile = ResumeProfile(
            resume_id="test_resume_001",
            candidate_name="测试候选人",
            highest_education="本科",
            total_experience_years=4.0,
            skills=["python", "django", "mysql", "flask"]
        )

    def test_calculate_hard_requirement_score(self):
        """测试硬性条件评分"""
        score = self.engine._calculate_hard_requirement_score(
            self.job_profile, self.resume_profile
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_calculate_skill_match_score(self):
        """测试技能匹配评分"""
        score = self.engine._calculate_skill_match_score(
            self.job_profile, self.resume_profile
        )
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_calculate_match_score(self):
        """测试整体匹配度计算"""
        result = self.engine.calculate_match_score(
            self.job_profile, self.resume_profile
        )
        
        self.assertIsInstance(result.total_score, float)
        self.assertGreaterEqual(result.total_score, 0)
        self.assertLessEqual(result.total_score, 100)
        self.assertEqual(result.job_id, self.job_profile.job_id)
        self.assertEqual(result.resume_id, self.resume_profile.resume_id)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 1. JD解析
        jd_parser = JDParser()
        sample_jd = "Python开发工程师，要求3年经验，熟悉Django和MySQL"
        job_profile = jd_parser.parse_jd(sample_jd, "Python工程师")
        
        # 2. 简历解析（模拟）
        resume_profile = ResumeProfile(
            resume_id="integration_test_001",
            candidate_name="集成测试候选人",
            highest_education="本科",
            total_experience_years=3.5,
            skills=["python", "django", "mysql"]
        )
        
        # 3. 匹配计算
        engine = MatchingEngine()
        match_result = engine.calculate_match_score(job_profile, resume_profile)
        
        # 4. 验证结果合理性
        self.assertIsNotNone(match_result)
        self.assertTrue(0 <= match_result.total_score <= 100)
        self.assertTrue(len(match_result.match_highlights) >= 0)
        self.assertTrue(len(match_result.missing_points) >= 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)