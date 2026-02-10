# -*- coding: utf-8 -*-
"""
简历智能匹配系统
基于智谱AI大模型的智能简历筛选和匹配平台

Author: Smart Resume Team
Version: 1.0.0
"""
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import tempfile
import json
from pathlib import Path

# 导入所有必要的模块
from parsers.jd_parser import JDParser
from parsers.resume_parser import ResumeParser
from parsers.bigdata_jd_parser import BigDataJDParser
from parsers.bigdata_resume_parser import BigDataResumeParser
from matching.engine import MatchingEngine
from matching.bigdata_engine import BigDataMatchingEngine
from utils.zhipuai_helper_simple import ZhipuAIHelper
from models import JobProfile, ResumeProfile, MatchResult, MatchAnalysisRequest

app = FastAPI(title="简历智能匹配系统", version="1.0.0")

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 初始化各个组件
jd_parser = JDParser()
resume_parser = ResumeParser()
matching_engine = MatchingEngine()
zhipu_helper = ZhipuAIHelper()

# 大数据架构师专用组件
bigdata_jd_parser = BigDataJDParser()
bigdata_resume_parser = BigDataResumeParser()
bigdata_matching_engine = BigDataMatchingEngine()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/parse_jd")
async def parse_jd(request: dict):
    """解析岗位需求"""
    try:
        jd_text = request.get("jd_text", "")
        job_title = request.get("job_title", "未知职位")
        
        if not jd_text:
            return JSONResponse(
                status_code=400,
                content={"error": "请提供岗位描述"}
            )
        
        # 解析JD
        job_profile = jd_parser.parse_jd(jd_text, job_title)
        
        return {
            "job_profile": job_profile.model_dump(),
            "ai_analysis": {}
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"JD解析失败: {str(e)}"}
        )

@app.post("/parse_bigdata_jd")
async def parse_bigdata_jd(request: dict):
    """解析大数据架构师岗位需求（专用版）"""
    try:
        jd_text = request.get("jd_text", "")
        job_title = request.get("job_title", "大数据架构师")
        
        if not jd_text:
            return JSONResponse(
                status_code=400,
                content={"error": "请提供岗位描述"}
            )
        
        # 使用大数据专用解析器
        job_profile = bigdata_jd_parser.parse_jd(jd_text, job_title)
        
        return {
            "job_profile": job_profile.model_dump(),
            "parser_type": "bigdata_specialized"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"大数据JD解析失败: {str(e)}"}
        )

@app.post("/parse_bigdata_resume")
async def parse_bigdata_resume(file: UploadFile = File(...)):
    """解析大数据架构师简历（专用版）"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 确定文件类型
        file_extension = Path(file.filename).suffix.lower().replace('.', '')
        if file_extension in ['jpg', 'jpeg', 'png']:
            file_type = 'image'
        elif file_extension == 'pdf':
            file_type = 'pdf'
        elif file_extension in ['docx', 'doc']:
            file_type = 'docx'
        elif file_extension == 'md':
            file_type = 'md'
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支持的文件格式: {file_extension}"}
            )
        
        # 使用大数据专用解析器
        resume_profile = bigdata_resume_parser.parse_resume(tmp_file_path, file_extension)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return {
            "resume_profile": resume_profile.model_dump(),
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "type": file.content_type,
                "parser_type": "bigdata_specialized"
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"大数据简历解析失败: {str(e)}"}
        )

@app.post("/parse_resume")
async def parse_resume(file: UploadFile = File(...)):
    """解析简历文件（通用版）"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 确定文件类型 - 修复文件扩展名处理问题
        file_extension = Path(file.filename).suffix.lower()
        if file_extension in ['.jpg', '.jpeg', '.png']:
            file_type = 'image'
        elif file_extension == '.pdf':
            file_type = 'pdf'
        elif file_extension in ['.docx', '.doc']:
            file_type = 'docx'
        elif file_extension == '.md':
            file_type = 'md'
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"不支持的文件格式: {file_extension}"}
            )
        
        # 使用通用解析器
        resume_profile = resume_parser.parse_resume(tmp_file_path, file_type)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return {
            "resume_profile": resume_profile.model_dump(),
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "type": file.content_type
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"简历解析失败: {str(e)}"}
        )

@app.post("/match_bigdata")
async def match_bigdata_analysis(request: dict):
    """进行大数据架构师匹配分析（专用版）"""
    try:
        # 解析请求数据
        job_profile_data = request.get("job_profile")
        resume_profile_data = request.get("resume_profile")
        
        if not job_profile_data or not resume_profile_data:
            return JSONResponse(
                status_code=400,
                content={"error": "请提供完整的岗位和简历数据"}
            )
        
        # 转换为模型对象
        job_profile = JobProfile(**job_profile_data)
        resume_profile = ResumeProfile(**resume_profile_data)
        
        # 使用大数据专用匹配引擎
        match_result = bigdata_matching_engine.calculate_match_score(job_profile, resume_profile)
        
        return {
            "match_result": match_result.model_dump(),
            "analysis_type": "bigdata_specialized"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"大数据匹配分析失败: {str(e)}"}
        )

@app.post("/match")
async def match_analysis(request: dict):
    """进行通用匹配分析"""
    try:
        # 解析请求数据
        job_profile_data = request.get("job_profile")
        resume_profile_data = request.get("resume_profile")
        
        if not job_profile_data or not resume_profile_data:
            return JSONResponse(
                status_code=400,
                content={"error": "请提供完整的岗位和简历数据"}
            )
        
        # 转换为模型对象
        job_profile = JobProfile(**job_profile_data)
        resume_profile = ResumeProfile(**resume_profile_data)
        
        # 使用通用匹配引擎
        match_result = matching_engine.calculate_match_score(job_profile, resume_profile)
        
        return {
            "match_result": match_result.model_dump(),
            "analysis_type": "general"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"通用匹配分析失败: {str(e)}"}
        )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='简历智能匹配系统')
    parser.add_argument('--host', default='0.0.0.0', help='绑定主机地址')
    parser.add_argument('--port', type=int, default=8000, help='端口号')
    parser.add_argument('--reload', action='store_true', help='启用热重载(开发模式)')
    
    args = parser.parse_args()
    
    print("🚀 启动简历智能匹配系统...")
    print(f"📝 访问地址: http://{args.host}:{args.port}")
    print(f"📊 API文档: http://{args.host}:{args.port}/docs")
    print(f"🏥 健康检查: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1 if args.reload else None
    )