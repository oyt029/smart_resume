# 简历智能匹配系统

基于智谱AI大模型的智能简历匹配系统，帮助HR高效筛选候选人。

[English Version](README_EN.md)

## 🌟 功能特性

- 📋 岗位需求智能解析
- 📄 简历文件智能解析（PDF/Word/图片）
- 🤖 基于大模型的语义匹配
- 📊 多维度加权评分系统
- 🎯 可视化匹配结果展示
- 🔄 实时分析和反馈

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Git
- 网络连接（用于调用AI API）

### 安装部署

```bash
# 克隆项目
git clone https://github.com/oyt029/smart_resume.git
cd smart_resume

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件，填入您的智谱AI API密钥
```

### 启动服务

```bash
# 开发模式（自动重载）
python app.py --reload

# 生产模式
python app.py --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000 查看界面

## 📖 API接口文档

系统会在 `/docs` 路径自动生成交互式API文档。

### 主要接口

- `POST /parse_jd` - 解析岗位需求
- `POST /parse_resume` - 解析简历文件
- `POST /match` - 进行匹配分析
- `GET /` - Web界面
- `GET /health` - 健康检查

## 🏗️ 项目结构

```
smart_resume/
├── app.py              # 主应用入口
├── requirements.txt    # Python依赖包
├── .env               # 环境配置文件
├── README.md          # 中文文档
├── README_EN.md       # 英文文档
├── Dockerfile         # Docker配置
├── docker-compose.yml # Docker编排
│
├── models/            # 数据模型定义
├── parsers/           # 解析器模块
├── matching/          # 匹配算法引擎
├── utils/             # 工具函数
├── static/            # 静态资源
├── templates/         # HTML模板
└── tests/             # 测试用例
```

## 🔧 配置说明

创建 `.env` 文件进行配置：

```env
ZHIPU_API_KEY=your_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

## 🐳 Docker部署

```bash
# 使用Docker Compose一键部署
docker-compose up -d

# 或者手动构建
docker build -t smart-resume .
docker run -p 8000:8000 smart-resume
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_parsers.py
```

## 📈 性能指标

- 单份简历处理时间：< 3秒（文本）/< 8秒（图片）
- 批量处理能力：100份简历/5分钟
- 并发支持：≥20个用户同时使用
- 解析准确率：>95%（关键字段）
- 匹配合格率：Top 10推荐>80%

## 🔒 安全与隐私

- 简历文件加密存储
- 敏感信息脱敏显示
- 支持数据彻底删除
- 符合数据保护规范

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证，详情请见LICENSE文件。

## 🆘 技术支持

遇到问题请：
- 在GitHub上提交Issue
- 联系开发团队

---
*版本：1.0.0 | 更新时间：2026年2月*