import streamlit as st
from utils.session_state import get_current_class_data, update_class_data
from utils.file_processing import process_uploaded_files
from utils.youtube_handler import extract_youtube_id, is_valid_youtube_url

def render_knowledge_upload():
    """Render the knowledge upload interface"""
    
    class_data = get_current_class_data()
    
    if not class_data:
        st.error("❌ No class selected")
        return
    
    st.markdown(f"## 📤 Add Knowledge to '{class_data['name']}'")
    
    if class_data.get('description'):
        st.markdown(f"*{class_data['description']}*")
    
    st.markdown("""
    Upload your study materials to create a personalized AI tutor. The more comprehensive 
    your materials, the better your AI assistant will be at answering questions.
    """)
    
    # Create tabs for different upload types
    tab1, tab2, tab3 = st.tabs(["📄 Documents", "🎥 YouTube Videos", "📊 Summary"])
    
    with tab1:
        render_document_upload()
    
    with tab2:
        render_youtube_upload()
    
    with tab3:
        render_knowledge_summary()

def render_document_upload():
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
                f"🚀 Process {len(uploaded_files)} File(s)",
                type="primary",
                use_container_width=True
            ):
                process_documents(uploaded_files)

def render_youtube_upload():
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
    
    # Validate and show video info
    if youtube_url:
        if is_valid_youtube_url(youtube_url):
            video_id = extract_youtube_id(youtube_url)
            
            # Show video preview
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.video(youtube_url)
            
            with col2:
                st.markdown("#### Video Preview")
                st.write(f"**Video ID:** {video_id}")
                st.info("👆 This video will be processed to extract audio and create a transcript for your AI tutor.")
                
                if st.button(
                    "🎵 Add Video to Knowledge Base",
                    type="primary",
                    use_container_width=True
                ):
                    process_youtube_video(youtube_url)
        else:
            st.error("❌ Please enter a valid YouTube URL")
    
    # Show existing YouTube videos
    class_data = get_current_class_data()
    if class_data and class_data.get('youtube_links'):
        st.markdown("#### 📹 Added Videos")
        for i, video_data in enumerate(class_data['youtube_links']):
            with st.expander(f"Video {i+1}: {video_data.get('title', 'YouTube Video')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**URL:** {video_data['url']}")
                    st.write(f"**Status:** {video_data.get('status', 'Pending')}")
                    if video_data.get('duration'):
                        st.write(f"**Duration:** {video_data['duration']}")
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_video_{i}"):
                        remove_youtube_video(i)

def render_knowledge_summary():
    """Render knowledge summary and processing status"""
    
    class_data = get_current_class_data()
    
    st.markdown("### 📊 Knowledge Base Summary")
    
    # Statistics
    total_files = len(class_data.get('knowledge_files', []))
    total_youtube = len(class_data.get('youtube_links', []))
    total_pages = class_data.get('total_pages', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Documents", total_files)
    with col2:
        st.metric("🎥 Videos", total_youtube)
    with col3:
        st.metric("📰 Pages", total_pages)
    with col4:
        st.metric("💾 Status", "Ready" if class_data.get('has_knowledge') else "Empty")
    
    # File list
    if total_files > 0:
        st.markdown("#### 📋 Uploaded Documents")
        for i, file_data in enumerate(class_data.get('knowledge_files', [])):
            with st.expander(f"{file_data['name']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Type:** {file_data.get('type', 'Unknown')}")
                    st.write(f"**Size:** {file_data.get('size_mb', 0):.1f}MB")
                    st.write(f"**Pages:** {file_data.get('pages', 'N/A')}")
                    st.write(f"**Uploaded:** {file_data.get('uploaded_at', 'Unknown')[:10]}")
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_file_{i}"):
                        remove_document(i)
    
    # Action buttons
    st.markdown("---")
    
    if total_files > 0 or total_youtube > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if not class_data.get('has_knowledge'):
                if st.button(
                    "🧠 Finalize Knowledge Base",
                    type="primary",
                    use_container_width=True,
                    help="Process all uploaded materials and enable chat"
                ):
                    finalize_knowledge_base()
        
        with col2:
            if st.button(
                "🔄 Reprocess All",
                use_container_width=True,
                help="Reprocess all materials (useful if processing failed)"
            ):
                reprocess_knowledge_base()
        
        with col3:
            if st.button(
                "🗑️ Clear All",
                use_container_width=True,
                help="Remove all uploaded materials"
            ):
                clear_knowledge_base()
    
    else:
        st.info("👆 Upload some documents or add YouTube videos to get started!")

def process_documents(uploaded_files):
    """Process uploaded documents"""
    
    class_data = get_current_class_data()
    
    # Show processing status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # This is a placeholder - actual processing will be implemented later
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}...")
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Simulate processing (replace with actual processing later)
            import time
            time.sleep(1)
            
            # Add file to class data
            file_data = {
                'name': file.name,
                'type': file.type,
                'size_mb': file.size / (1024 * 1024),
                'pages': 10,  # Placeholder
                'uploaded_at': st.session_state.get('current_time', ''),
                'status': 'processed'
            }
            
            if 'knowledge_files' not in class_data:
                class_data['knowledge_files'] = []
            
            class_data['knowledge_files'].append(file_data)
        
        # Update class data
        class_data['file_count'] = len(class_data.get('knowledge_files', []))
        class_data['total_pages'] = sum(f.get('pages', 0) for f in class_data.get('knowledge_files', []))
        
        update_class_data(class_data)
        
        status_text.text("✅ All files processed successfully!")
        st.success(f"🎉 Successfully processed {len(uploaded_files)} file(s)!")
        
        # Auto-rerun to update the interface
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")

def process_youtube_video(url):
    """Process YouTube video"""
    
    class_data = get_current_class_data()
    
    try:
        # This is a placeholder - actual processing will be implemented later
        video_id = extract_youtube_id(url)
        
        video_data = {
            'url': url,
            'video_id': video_id,
            'title': f"YouTube Video {video_id}",
            'duration': "10:30",  # Placeholder
            'status': 'processed',
            'added_at': st.session_state.get('current_time', '')
        }
        
        if 'youtube_links' not in class_data:
            class_data['youtube_links'] = []
        
        class_data['youtube_links'].append(video_data)
        update_class_data(class_data)
        
        st.success("🎥 YouTube video added successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing YouTube video: {str(e)}")

def finalize_knowledge_base():
    """Mark knowledge base as ready for chat"""
    
    class_data = get_current_class_data()
    class_data['has_knowledge'] = True
    update_class_data(class_data)
    
    st.success("🧠 Knowledge base finalized! You can now start chatting.")
    st.balloons()
    st.rerun()

def reprocess_knowledge_base():
    """Reprocess all materials in knowledge base"""
    
    with st.spinner("🔄 Reprocessing knowledge base..."):
        # Placeholder for reprocessing logic
        import time
        time.sleep(2)
        
        st.success("✅ Knowledge base reprocessed successfully!")

def clear_knowledge_base():
    """Clear all knowledge from the class"""
    
    class_data = get_current_class_data()
    
    # Confirmation
    if st.button("⚠️ Confirm Clear All", type="primary"):
        class_data['knowledge_files'] = []
        class_data['youtube_links'] = []
        class_data['has_knowledge'] = False
        class_data['file_count'] = 0
        class_data['total_pages'] = 0
        
        update_class_data(class_data)
        
        st.success("🗑️ All knowledge cleared!")
        st.rerun()

def remove_document(index):
    """Remove a specific document"""
    
    class_data = get_current_class_data()
    
    if 'knowledge_files' in class_data and index < len(class_data['knowledge_files']):
        removed_file = class_data['knowledge_files'].pop(index)
        
        # Update counters
        class_data['file_count'] = len(class_data.get('knowledge_files', []))
        class_data['total_pages'] = sum(f.get('pages', 0) for f in class_data.get('knowledge_files', []))
        
        # If no more files, mark as no knowledge
        if class_data['file_count'] == 0 and len(class_data.get('youtube_links', [])) == 0:
            class_data['has_knowledge'] = False
        
        update_class_data(class_data)
        
        st.success(f"🗑️ Removed {removed_file['name']}")
        st.rerun()

def remove_youtube_video(index):
    """Remove a specific YouTube video"""
    
    class_data = get_current_class_data()
    
    if 'youtube_links' in class_data and index < len(class_data['youtube_links']):
        removed_video = class_data['youtube_links'].pop(index)
        
        # If no more content, mark as no knowledge
        if len(class_data.get('knowledge_files', [])) == 0 and len(class_data.get('youtube_links', [])) == 0:
            class_data['has_knowledge'] = False
        
        update_class_data(class_data)
        
        st.success(f"🗑️ Removed video {removed_video.get('title', 'YouTube Video')}")
        st.rerun()