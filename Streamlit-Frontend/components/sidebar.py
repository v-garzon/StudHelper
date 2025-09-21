import streamlit as st
from datetime import datetime
import uuid

def render_sidebar():
    """Render the sidebar with class selection and creation"""
    
    with st.sidebar:
        st.markdown("## 📚 Your Classes")
        
        # Class creation section
        st.markdown("### ➕ Create New Class")
        
        with st.form("create_class_form"):
            new_class_name = st.text_input(
                "Class Name",
                placeholder="e.g., Machine Learning, History 101, Spanish Basics",
                help="Give your study class a descriptive name"
            )
            
            new_class_description = st.text_area(
                "Description (Optional)",
                placeholder="Brief description of what you'll study in this class",
                max_chars=200,
                height=80
            )
            
            create_button = st.form_submit_button(
                "🎓 Create Class",
                use_container_width=True,
                type="primary"
            )
            
            if create_button and new_class_name.strip():
                # Create new class
                class_id = str(uuid.uuid4())[:8]
                new_class = {
                    'id': class_id,
                    'name': new_class_name.strip(),
                    'description': new_class_description.strip(),
                    'created_at': datetime.now().isoformat(),
                    'has_knowledge': False,
                    'knowledge_files': [],
                    'youtube_links': [],
                    'chat_history': [],
                    'file_count': 0,
                    'total_pages': 0
                }
                
                # Add to session state
                if 'classes' not in st.session_state:
                    st.session_state.classes = {}
                
                st.session_state.classes[class_id] = new_class
                st.session_state.current_class = class_id
                
                st.success(f"✅ Class '{new_class_name}' created successfully!")
                st.rerun()
            
            elif create_button and not new_class_name.strip():
                st.error("❌ Please enter a class name")
        
        st.divider()
        
        # Existing classes section
        st.markdown("### 📖 Select a Class")
        
        if 'classes' in st.session_state and st.session_state.classes:
            # Display existing classes
            for class_id, class_data in st.session_state.classes.items():
                # Create a container for each class
                class_container = st.container()
                
                with class_container:
                    # Check if this is the current class
                    is_current = st.session_state.get('current_class') == class_id
                    
                    # Class selection button
                    button_type = "primary" if is_current else "secondary"
                    
                    if st.button(
                        f"📚 {class_data['name']}",
                        key=f"select_class_{class_id}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state.current_class = class_id
                        st.rerun()
                    
                    # Show class info if selected
                    if is_current:
                        with st.expander("ℹ️ Class Info", expanded=False):
                            st.write(f"**Created:** {class_data['created_at'][:10]}")
                            if class_data.get('description'):
                                st.write(f"**Description:** {class_data['description']}")
                            
                            # Knowledge status
                            if class_data.get('has_knowledge'):
                                st.write("📄 **Files:** " + str(class_data.get('file_count', 0)))
                                st.write("📰 **Pages:** " + str(class_data.get('total_pages', 0)))
                                if class_data.get('youtube_links'):
                                    st.write("🎥 **YouTube:** " + str(len(class_data['youtube_links'])))
                                st.success("✅ Ready for chat!")
                            else:
                                st.warning("⚠️ No knowledge added yet")
                            
                            # Delete class option
                            if st.button(
                                "🗑️ Delete Class",
                                key=f"delete_class_{class_id}",
                                use_container_width=True,
                                help="This will permanently delete the class and all its data"
                            ):
                                # Confirm deletion
                                if st.button(
                                    "⚠️ Confirm Delete",
                                    key=f"confirm_delete_{class_id}",
                                    type="primary"
                                ):
                                    del st.session_state.classes[class_id]
                                    if st.session_state.get('current_class') == class_id:
                                        st.session_state.current_class = None
                                    st.success(f"🗑️ Class '{class_data['name']}' deleted")
                                    st.rerun()
                    
                    st.markdown("---")
        
        else:
            # No classes yet
            st.info("👆 Create your first class to get started!")
        
        # Footer with stats
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        
        total_classes = len(st.session_state.get('classes', {}))
        classes_with_knowledge = sum(
            1 for class_data in st.session_state.get('classes', {}).values()
            if class_data.get('has_knowledge', False)
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Classes", total_classes)
        with col2:
            st.metric("Active", classes_with_knowledge)
        
        # App info
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            StudHelper v1.0<br>
            🤖 AI-Powered Study Assistant
        </div>
        """, unsafe_allow_html=True)