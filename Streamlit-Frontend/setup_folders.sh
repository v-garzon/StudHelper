#!/bin/bash

# StudHelper Streamlit Frontend - Folder Setup Script
echo "🎓 Setting up StudHelper Streamlit Frontend..."

# Create main directory
mkdir -p StudHelper-Streamlit
cd StudHelper-Streamlit

# Create folder structure
echo "📁 Creating folder structure..."
mkdir -p components
mkdir -p utils
mkdir -p storage/{uploads,vectors}
mkdir -p docs

# Create __init__.py files for Python packages
touch components/__init__.py
touch utils/__init__.py

# Create placeholder files to preserve folder structure
touch storage/uploads/.gitkeep
touch storage/vectors/.gitkeep

echo "✅ Folder structure created successfully!"
echo ""
echo "📁 Your structure:"
echo "StudHelper-Streamlit/"
echo "├── components/          # UI components"
echo "├── utils/              # Utility functions"
echo "├── storage/"
echo "│   ├── uploads/        # Uploaded files"
echo "│   └── vectors/        # Vector database"
echo "├── docs/               # Documentation"
echo "├── main.py             # Main Streamlit app"
echo "└── requirements.txt    # Dependencies"
echo ""
echo "🚀 Next steps:"
echo "1. Copy all the component files into their respective folders"
echo "2. pip install -r requirements.txt"
echo "3. streamlit run main.py"
echo ""
echo "Happy coding! 🎯"
