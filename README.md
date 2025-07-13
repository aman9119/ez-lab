# 📄 Document-Aware AI Assistant

A comprehensive GenAI assistant that reads, understands, and reasons through documents to provide intelligent question answering and educational challenges.

## 🎯 Features

### Core Functionality
- **Document Upload**: Support for PDF and TXT files
- **Auto Summary**: Instant concise summary (≤150 words) upon upload
- **Ask Anything**: Free-form question answering with contextual understanding
- **Challenge Mode**: AI-generated logic-based questions with evaluation
- **Grounded Responses**: All answers backed by document references

### Advanced Capabilities
- **Deep Comprehension**: Understanding beyond surface-level keyword matching
- **Logical Reasoning**: Inference and analysis based on document content
- **Interactive Learning**: Challenge questions with detailed feedback
- **Memory Handling**: Maintains context across conversations
- **Answer Justification**: Every response includes document references

## 🏗️ Architecture

- **Backend**: FastAPI with OpenAI integration
- **Frontend**: Streamlit for intuitive web interface
- **Document Processing**: PyPDF2, text chunking, and vectorization
- **AI Models**: OpenAI GPT for reasoning, embeddings for semantic search
- **Storage**: In-memory session management (production-ready for database integration)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and navigate to the project**:
```bash
git clone <repository-url>
cd document_assistant
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the application**:
```bash
python run_app.py
```

The application will be available at:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000

## 📖 Usage Guide

### 1. Document Upload
- Click "Choose a file" and select a PDF or TXT document
- Supported formats: Structured documents like research papers, reports, manuals
- Click "Process Document" to analyze and generate summary

### 2. Ask Anything Mode
- Type any question about the document content
- Get contextual answers with document references
- Build conversation history with follow-up questions

### 3. Challenge Mode
- Click "Generate Challenge Questions" for AI-created questions
- Answer logic-based questions that test comprehension
- Receive detailed feedback and scoring (0-100)
- View correct answers with document references

## 🔧 Configuration

### Environment Variables (.env)
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Document Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=2000

# Assistant Configuration
SUMMARY_MAX_WORDS=150
CHALLENGE_QUESTIONS_COUNT=3

# Temperature Settings
SUMMARY_TEMPERATURE=0.3
QA_TEMPERATURE=0.1
CHALLENGE_TEMPERATURE=0.7
```

### Customization Options
- **Chunk Size**: Adjust document processing granularity
- **Model Selection**: Choose different OpenAI models
- **Question Count**: Modify number of challenge questions
- **Temperature**: Control AI response creativity

## 🛠️ API Endpoints

### Document Management
- `POST /upload` - Upload and process document
- `GET /session/{session_id}` - Get session information
- `DELETE /session/{session_id}` - Clean up session

### Interactions
- `POST /ask` - Ask questions about document
- `POST /challenge` - Generate challenge questions
- `POST /evaluate` - Evaluate user answers

## 📁 Project Structure

```
document_assistant/
├── backend/
│   ├── main.py              # FastAPI application
│   └── __init__.py
├── frontend/
│   └── streamlit_app.py     # Streamlit interface
├── utils/
│   ├── config.py            # Configuration management
│   ├── document_processor.py # Document processing
│   ├── assistant.py         # AI assistant logic
│   └── __init__.py
├── uploads/                 # Document storage
├── data/                    # Application data
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── run_app.py              # Application launcher
└── README.md               # This file
```

## 🔍 Technical Details

### Document Processing
- **Text Extraction**: PyPDF2 for PDFs, encoding detection for TXT
- **Chunking**: Intelligent paragraph-based splitting with overlap
- **Vectorization**: Sentence-BERT embeddings for semantic search
- **Retrieval**: Cosine similarity for relevant context

### AI Integration
- **Models**: OpenAI GPT-3.5-turbo for reasoning tasks
- **Embeddings**: OpenAI text-embedding-ada-002 for semantic search
- **Prompting**: Specialized prompts for different tasks
- **Evaluation**: Structured scoring with detailed feedback

### Session Management
- **Memory**: Conversation history and document context
- **Cleanup**: Automatic resource management
- **Scaling**: Ready for Redis/database integration

## 🎯 Use Cases

### Educational
- **Students**: Test reading comprehension on academic papers
- **Researchers**: Quick analysis of research documents
- **Professionals**: Understanding complex technical manuals

### Business
- **Legal**: Document analysis and comprehension testing
- **Healthcare**: Medical literature understanding
- **Finance**: Financial report analysis

### Personal
- **Learning**: Interactive document exploration
- **Research**: Deep dive into any text-based content
- **Knowledge**: Building understanding through questions

## 🛡️ Security & Privacy

- **Local Processing**: Documents processed locally
- **API Security**: OpenAI API key required
- **Session Isolation**: Each session is independent
- **Data Cleanup**: Automatic resource cleanup

## 🚧 Future Enhancements

- **Multi-language Support**: Beyond English documents
- **Advanced Highlighting**: Visual source highlighting
- **Collaborative Features**: Shared sessions and discussions
- **Export Options**: Save Q&A sessions and evaluations
- **Analytics**: Learning progress tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section below
2. Review existing issues in the repository
3. Create a new issue with detailed description

## 🔧 Troubleshooting

### Common Issues

**1. "OpenAI API key not configured"**
- Ensure `.env` file exists with valid `OPENAI_API_KEY`
- Check API key has sufficient credits

**2. "Error processing document"**
- Verify file format (PDF/TXT only)
- Check file size and content structure
- Ensure document contains extractable text

**3. "Backend connection failed"**
- Verify backend is running on port 8000
- Check firewall settings
- Ensure all dependencies are installed

**4. "Challenge questions not generating"**
- Check OpenAI API connectivity
- Verify document has sufficient content
- Try with different temperature settings

### Performance Tips
- Use structured documents for best results
- Optimize chunk size for your document type
- Consider using GPT-4 for complex reasoning tasks
- Monitor API usage for cost optimization

## 📊 Metrics & Monitoring

The application tracks:
- Document processing time
- Question response time
- Challenge question difficulty
- User engagement metrics
- API usage statistics

---

Built with ❤️ for intelligent document understanding and interactive learning.