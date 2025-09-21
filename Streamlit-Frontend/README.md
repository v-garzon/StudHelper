# 🎓 StudHelper - Streamlit Frontend

StudHelper is an AI-powered study assistant that allows you to upload documents and chat with an AI tutor that has knowledge of your specific materials.

## ✨ Features

- **📚 Class Management**: Create and organize multiple study classes
- **📄 Document Upload**: Support for PDFs, Word docs, PowerPoint, and text files
- **🎥 YouTube Integration**: Add YouTube video links for transcript analysis
- **💬 AI Chat**: Interactive chat with AI tutor based on your materials
- **📊 Progress Tracking**: Monitor your knowledge base and study progress

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or download the project
mkdir StudHelper-Streamlit
cd StudHelper-Streamlit

# Create folder structure
./setup_folders.sh

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure

```
StudHelper-Streamlit/
├── main.py                     # Main Streamlit application
├── components/                 # UI components
│   ├── sidebar.py             # Class selection sidebar
│   ├── welcome.py             # Welcome page
│   ├── knowledge_upload.py    # File upload interface
│   └── chat_interface.py      # Chat functionality
├── utils/                      # Utility functions
│   ├── session_state.py       # Session management
│   ├── file_processing.py     # File processing
│   └── youtube_handler.py     # YouTube integration
├── storage/                    # Local storage
│   ├── uploads/               # Uploaded files
│   └── vectors/               # Vector database
└── requirements.txt           # Dependencies
```

### 3. Run Application

```bash
streamlit run main.py
```

The application will start on `http://localhost:8501`

## 📖 How to Use

### Creating Your First Class

1. **Start the app** - Run `streamlit run main.py`
1. **Create a class** - Use the sidebar to create a new study class
1. **Upload knowledge** - Add PDFs, documents, or YouTube links
1. **Start chatting** - Ask questions about your materials!

### Supported File Types

- **📄 PDF Documents** (.pdf)
- **📝 Word Documents** (.docx)
- **📊 PowerPoint Presentations** (.pptx)
- **📄 Text Files** (.txt)
- **📝 Markdown Files** (.md)
- **🎥 YouTube Videos** (via URL)

### File Size Limits

- Maximum file size: 50MB per file
- Maximum total upload: 100MB per batch
- Recommended: Keep individual PDFs under 20MB for faster processing

## 💬 Chat Features

### What You Can Ask

- **📖 Summarization**: “Summarize chapter 3”
- **🔍 Specific Questions**: “What are the key formulas?”
- **📚 Study Help**: “Create practice questions”
- **💡 Explanations**: “Explain this concept simply”
- **📋 Study Plans**: “Help me create a study schedule”

### Chat Tips

- Be specific in your questions
- Reference page numbers or chapters when possible
- Use follow-up questions to dive deeper
- Ask for examples or practice problems

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API (for future backend integration)
OPENAI_API_KEY=your_openai_api_key_here

# Storage settings
UPLOAD_DIR=./storage/uploads
VECTOR_DB_DIR=./storage/vectors

# Processing settings
MAX_FILE_SIZE=52428800  # 50MB
MAX_TOTAL_SIZE=104857600  # 100MB
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Customization

You can customize the app by modifying:

- **UI styling**: Edit the CSS in `main.py`
- **Processing settings**: Modify chunk sizes in `utils/file_processing.py`
- **Supported file types**: Add new processors in `utils/file_processing.py`

## 🔧 Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run main.py --server.runOnSave=true
```

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Format code
black .
isort .
```

## 📊 Current Limitations

This is the **frontend-only version** with placeholder implementations:

- **AI Responses**: Currently mock responses (AI integration coming in backend)
- **File Processing**: Basic text extraction (advanced processing in backend)
- **Vector Search**: Placeholder (real vector database in backend)
- **User Authentication**: Not implemented (single-user mode)

## 🚀 Roadmap

### Phase 1: Current - Streamlit Frontend ✅

- Complete UI/UX for all features
- File upload and management
- Mock chat interface
- Session state management

### Phase 2: Backend Integration (Coming Next)

- FastAPI backend with real AI processing
- OpenAI integration for embeddings and chat
- ChromaDB for vector storage
- Real document processing pipeline

### Phase 3: Production Features

- User authentication
- Cloud deployment
- Advanced file processing
- Performance optimizations

## 🆘 Troubleshooting

### Common Issues

**Streamlit won’t start:**

```bash
# Check Python version (3.8+ required)
python --version

# Reinstall streamlit
pip uninstall streamlit
pip install streamlit==1.28.1
```

**File upload fails:**

- Check file size (must be < 50MB)
- Verify file type is supported
- Ensure storage/uploads folder exists

**Session state errors:**

- Clear browser cache
- Restart Streamlit app
- Check browser console for errors

### Getting Help

1. Check the [Streamlit documentation](https://docs.streamlit.io/)
1. Review error messages in the terminal
1. Check browser console for JavaScript errors
1. Create an issue with error details

## 📄 License

This project is for educational and personal use.

## 🤝 Contributing

This is a personal learning project, but suggestions and improvements are welcome!

-----

**Built with ❤️ using Streamlit and Python**

*StudHelper v1.0 - Your AI-Powered Study Assistant*