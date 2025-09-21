

import streamlit as st
from datetime import datetime
from typing import Dict, Optional, Any

def initialize_session_state():
    """Initialize session state variables"""
    
    # Core app state
    if 'classes' not in st.session_state:
        st.session_state.classes = {}
    
    if 'current_class' not in st.session_state:
        st.session_state.current_class = None
    
    # App metadata
    if 'app_version' not in st.session_state:
        st.session_state.app_version = "1.0.0"
    
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    # Current time for timestamps
    st.session_state.current_time = datetime.now().isoformat()
    
    # UI state
    if 'show_debug' not in st.session_state:
        st.session_state.show_debug = False
    
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}

def get_current_class_data() -> Optional[Dict[str, Any]]:
    """Get the data for the currently selected class"""
    
    current_class = st.session_state.get('current_class')
    
    if not current_class:
        return None
    
    classes = st.session_state.get('classes', {})
    return classes.get(current_class)

def update_class_data(class_data: Dict[str, Any]):
    """Update the data for the currently selected class"""
    
    current_class = st.session_state.get('current_class')
    
    if not current_class:
        return False
    
    if 'classes' not in st.session_state:
        st.session_state.classes = {}
    
    # Add/update timestamp
    class_data['updated_at'] = datetime.now().isoformat()
    
    st.session_state.classes[current_class] = class_data
    return True

def get_all_classes() -> Dict[str, Dict[str, Any]]:
    """Get all classes"""
    
    return st.session_state.get('classes', {})

def delete_class(class_id: str) -> bool:
    """Delete a class and its data"""
    
    if 'classes' not in st.session_state:
        return False
    
    if class_id in st.session_state.classes:
        del st.session_state.classes[class_id]
        
        # If this was the current class, unselect it
        if st.session_state.get('current_class') == class_id:
            st.session_state.current_class = None
        
        return True
    
    return False

def create_new_class(name: str, description: str = "") -> str:
    """Create a new class and return its ID"""
    
    import uuid
    
    class_id = str(uuid.uuid4())[:8]
    
    new_class = {
        'id': class_id,
        'name': name.strip(),
        'description': description.strip(),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'has_knowledge': False,
        'knowledge_files': [],
        'youtube_links': [],
        'chat_history': [],
        'file_count': 0,
        'total_pages': 0,
        'processing_status': 'idle',
        'settings': {
            'auto_process': True,
            'chunk_size': 1000,
            'chunk_overlap': 200
        }
    }
    
    if 'classes' not in st.session_state:
        st.session_state.classes = {}
    
    st.session_state.classes[class_id] = new_class
    
    return class_id

def get_class_statistics() -> Dict[str, Any]:
    """Get overall statistics about all classes"""
    
    classes = get_all_classes()
    
    total_classes = len(classes)
    active_classes = sum(1 for c in classes.values() if c.get('has_knowledge', False))
    total_files = sum(len(c.get('knowledge_files', [])) for c in classes.values())
    total_pages = sum(c.get('total_pages', 0) for c in classes.values())
    total_videos = sum(len(c.get('youtube_links', [])) for c in classes.values())
    total_messages = sum(len(c.get('chat_history', [])) for c in classes.values())
    
    return {
        'total_classes': total_classes,
        'active_classes': active_classes,
        'total_files': total_files,
        'total_pages': total_pages,
        'total_videos': total_videos,
        'total_messages': total_messages
    }

def set_processing_status(status: str, message: str = ""):
    """Set processing status for the current class"""
    
    current_class = st.session_state.get('current_class')
    
    if current_class:
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = {}
        
        st.session_state.processing_status[current_class] = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

def get_processing_status() -> Optional[Dict[str, Any]]:
    """Get processing status for the current class"""
    
    current_class = st.session_state.get('current_class')
    
    if not current_class:
        return None
    
    return st.session_state.get('processing_status', {}).get(current_class)

def clear_processing_status():
    """Clear processing status for the current class"""
    
    current_class = st.session_state.get('current_class')
    
    if current_class and 'processing_status' in st.session_state:
        if current_class in st.session_state.processing_status:
            del st.session_state.processing_status[current_class]

def reset_all_data():
    """Reset all application data (useful for debugging)"""
    
    st.session_state.classes = {}
    st.session_state.current_class = None
    st.session_state.processing_status = {}
    
    # Reinitialize
    initialize_session_state()

def export_session_data() -> Dict[str, Any]:
    """Export all session data for backup/debugging"""
    
    return {
        'classes': st.session_state.get('classes', {}),
        'current_class': st.session_state.get('current_class'),
        'session_id': st.session_state.get('session_id'),
        'app_version': st.session_state.get('app_version'),
        'statistics': get_class_statistics(),
        'export_timestamp': datetime.now().isoformat()
    }

def import_session_data(data: Dict[str, Any]) -> bool:
    """Import session data from backup"""
    
    try:
        if 'classes' in data:
            st.session_state.classes = data['classes']
        
        if 'current_class' in data:
            st.session_state.current_class = data['current_class']
        
        return True
    
    except Exception as e:
        st.error(f"Error importing data: {str(e)}")
        return False

def debug_session_state():
    """Display debug information about session state"""
    
    if st.session_state.get('show_debug', False):
        with st.expander("🐛 Debug Info", expanded=False):
            st.json({
                'session_id': st.session_state.get('session_id'),
                'current_class': st.session_state.get('current_class'),
                'total_classes': len(st.session_state.get('classes', {})),
                'processing_status': st.session_state.get('processing_status', {}),
                'statistics': get_class_statistics()
            })

# Validation functions
def validate_class_data(class_data: Dict[str, Any]) -> bool:
    """Validate class data structure"""
    
    required_fields = ['id', 'name', 'created_at']
    
    for field in required_fields:
        if field not in class_data:
            return False
    
    return True

def sanitize_class_name(name: str) -> str:
    """Sanitize class name for safe storage"""
    
    import re
    
    # Remove any potentially problematic characters
    sanitized = re.sub(r'[^\w\s-]', '', name.strip())
    
    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50].strip()
    
    return sanitized

