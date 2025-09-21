"""Modified knowledge upload to use backend API."""

import streamlit as st
from utils.api_client import APIClient
from utils.youtube_handler import is_valid_youtube_url

def render_knowledge_upload():
    """Render the knowledge upload interface"""
    
    api_client = APIClient()
    
    st.markdown("## 📤 Upload Study Materials")
    st.markdown("""
    Upload your study materials to create a personalized AI tutor. The more comprehensive 
    your materials, the better your AI assistant will be at answering questions.
    """)
    
    # Create tabs for different upload types
    tab1, tab2, tab3 = st.tabs(["📄 Documents", "🎥 YouTube Videos", "📊 Summary"])
    
    with tab1:
        render_document_upload(api_client)
    
    with tab2:
        render_youtube_upload(api_client)
    
    with tab3:
        render_knowledge_summary(api_client)

def render_document_upload(api_client: APIClient):
    """Render document upload section"""
    
    st.markdown("### 📄 Upload Documents")
    st.markdown("""
    Upload PDFs, Word documents, PowerPoint presentations, and other text files. 
    These will be analyzed and used to answer your questions.
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'docx', 'pptx', 'txt', 'md'],
        accept_multiple_files=True,
        help="Supported formats: PDF, Word (.docx), PowerPoint (.pptx), Text (.txt), Markdown (.md)"
    )
    
    # File size warning
    if uploaded_files:
        total_size = sum(file.size for file in uploaded_files)
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb > 100:
            st.warning(f"⚠️ Total file size: {total_size_mb:.1f}MB. Consider uploading files in smaller batches for better performance.")
        else:
            st.info(f"📊 Total file size: {total_size_mb:.1f}MB")
        
        # Show file details
        with st.expander("📋 File Details", expanded=True):
            for i, file in enumerate(uploaded_files):
                file_size_mb = file.size / (1024 * 1024)
                st.write(f"**{i+1}.** {file.name} ({file_size_mb:.1f}MB)")
        
        # Process files button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                f"🚀 Upload {len(uploaded_files)} File(s)",
                type="primary",
                use_container_width=True
            ):
                upload_documents(uploaded_files, api_client)

def render_youtube_upload(api_client: APIClient):
    """Render YouTube upload section"""
    
    st.markdown("### 🎥 YouTube Videos")
    st.markdown("""
    Add YouTube video links to extract and analyze the audio content. 
    Great for lectures, tutorials, and educational videos.
    """)
    
    # YouTube URL input
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help="Paste a YouTube video link here"
    )
    
    # Optional title
    video_title = st.text_input(
        "Title (Optional)",
        placeholder="Give this video a custom title",
        help="Leave blank to use the video's original title"
    )
    
    # Validate and show video info
    if youtube_url:
        if is_valid_youtube_url(youtube_url):
            # Show video preview
            col1, col2 = st.columns([1, 2])
            
            with col1:
                try:
                    st.video(youtube_url)
                except:
                    st.info("Video preview not available")
            
            with col2:
                st.markdown("#### Video Preview")
                st.info("👆 This video will be processed to extract audio and create a transcript for your AI tutor.")
                
                if st.button(
                    "🎵 Add Video to Knowledge Base",
                    type="primary",
                    use_container_width=True
                ):
                    upload_youtube_video(youtube_url, video_title, api_client)
        else:
            st.error("❌ Please enter a valid YouTube URL")

def render_knowledge_summary(api_client: APIClient):
    """Render knowledge summary and processing status"""
    
    st.markdown("### 📊 Knowledge Base Summary")
    
    # Get documents from backend
    docs_result = api_client.get_documents()
    
    if not docs_result["success"]:
        st.error(f"❌ Error loading documents: {docs_result['error']}")
        return
    
    documents = docs_result["data"]
    
    # Statistics
    total_files = len(documents)
    completed_docs = len([doc for doc in documents if doc.get('status') == 'completed'])
    processing_docs = len([doc for doc in documents if doc.get('status') == 'processing'])
    failed_docs = len([doc for doc in documents if doc.get('status') == 'failed'])
    total_pages = sum(doc.get('page_count', 0) for doc in documents)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Documents", total_files)
    with col2:
        st.metric("✅ Completed", completed_docs)
    with col3:
        st.metric("⏳ Processing", processing_docs)
    with col4:
        st.metric("📰 Total Pages", total_pages)
    
    # Document list
    if documents:
        st.markdown("#### 📋 Your Documents")
        
        for doc in documents:
            with st.expander(f"{doc['filename']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Type:** {doc.get('file_type', 'Unknown')}")
                    st.write(f"**Size:** {doc.get('file_size', 0) / (1024*1024):.1f}MB")
                    st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                    st.write(f"**Status:** {doc.get('status', 'Unknown')}")
                    st.write(f"**Uploaded:** {doc.get('created_at', 'Unknown')[:10]}")
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_doc_{doc['id']}"):
                        delete_document(doc['id'], api_client)
    
    else:
        st.info("👆 Upload some documents or add YouTube videos to get started!")

def upload_documents(uploaded_files, api_client: APIClient):
    """Upload documents to backend"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    success_count = 0
    error_count = 0
    
    for i, file in enumerate(uploaded_files):
        status_text.text(f"Uploading {file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Upload to backend
        result = api_client.upload_document(
            file_data=file.getvalue(),
            filename=file.name,
            content_type=file.type
        )
        
        if result["success"]:
            success_count += 1
        else:
            error_count += 1
            st.error(f"Failed to upload {file.name}: {result['error']}")
    
    status_text.text("✅ Upload complete!")
    
    if success_count > 0:
        st.success(f"🎉 Successfully uploaded {success_count} file(s)!")
    
    if error_count > 0:
        st.warning(f"⚠️ {error_count} file(s) failed to upload")
    
    # Refresh the page
    st.rerun()

def upload_youtube_video(url: str, title: str, api_client: APIClient):
    """Upload YouTube video to backend"""
    
    with st.spinner("🎵 Adding YouTube video..."):
        result = api_client.add_youtube_video(url, title if title else None)
    
    if result["success"]:
        st.success("🎥 YouTube video added successfully!")
        st.rerun()
    else:
        st.error(f"❌ Error adding video: {result['error']}")

def delete_document(document_id: int, api_client: APIClient):
    """Delete a document"""
    
    result = api_client.delete_document(document_id)
    
    if result["success"]:
        st.success("🗑️ Document deleted successfully!")
        st.rerun()
    else:
        st.error(f"❌ Error deleting document: {result['error']}")

