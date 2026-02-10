# Smart Resume Matching System

An intelligent resume matching system based on Zhipu AI's large language model, designed to help HR professionals efficiently screen candidates.

## 🌟 Key Features

- 📋 Intelligent job description parsing
- 📄 Multi-format resume parsing (PDF/Word/Images)
- 🤖 Semantic matching powered by large language models
- 📊 Multi-dimensional weighted scoring system
- 🎯 Visualized matching results display

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Git
- Internet connection (for AI API calls)

### Installation

```bash
# Clone the repository
git clone https://github.com/oyt029/smart_resume.git
cd smart_resume

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your Zhipu AI API key
```

### Running the Application

```bash
# Development mode with auto-reload
python app.py --reload

# Production mode
python app.py --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to access the web interface.

## 📖 API Documentation

The system automatically generates interactive API documentation at `/docs`.

### Main Endpoints

- `POST /parse_jd` - Parse job description
- `POST /parse_resume` - Parse resume file
- `POST /match` - Perform matching analysis
- `GET /` - Web interface
- `GET /health` - Health check

## 🏗️ Architecture

```
smart_resume/
├── app.py              # Main application entry point
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
├── README.md          # Chinese documentation
├── README_EN.md       # English documentation
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
│
├── models/            # Data models (Pydantic)
├── parsers/           # Resume and JD parsers
├── matching/          # Matching algorithms
├── utils/             # Utility functions
├── static/            # Static assets
└── templates/         # HTML templates
```

## 🔧 Configuration

Create a `.env` file with your configuration:

```env
ZHIPU_API_KEY=your_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker-compose up -d

# Or build manually
docker build -t smart-resume .
docker run -p 8000:8000 smart-resume
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_parsers.py
```

## 📈 Performance Metrics

- Single resume processing time: < 3s (text) / < 8s (images)
- Batch processing capacity: 100 resumes/5 minutes
- Concurrent support: ≥20 simultaneous users
- Parsing accuracy: >95% (key fields)
- Matching success rate: Top 10 recommendations >80%

## 🔒 Security & Privacy

- Encrypted resume storage
- Sensitive information redaction
- Data deletion support
- Compliance with data protection regulations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Contact the development team

---
*Version: 1.0.0 | Last Updated: February 2026*