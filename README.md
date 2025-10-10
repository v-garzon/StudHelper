# Class Management System - Setup Instructions

## Database Migration

1. **Run Alembic Migration**
```bash
cd Backend
alembic upgrade head
```

This will add:
- `description` column to `classes` table
- `description` column to `documents` table
- `url` column to `documents` table
- Indexes for better query performance

## Backend Setup

1. **No configuration changes needed** - The migration handles all database changes

2. **Restart the backend server**
```bash
cd Backend
uvicorn app.main:app --reload
```

## Frontend Setup

1. **No npm package installation needed** - All dependencies already exist

2. **File Structure Changes**

The following files need to be created/moved:

**NEW FILES CREATED:**
```
Vue-Frontend/src/
├── services/classService.js
├── components/features/class-management/
│   ├── modals/ClassModal.vue
│   ├── forms/
│   │   ├── ClassInfoForm.vue
│   │   └── KnowledgeManager.vue
│   ├── components/
│   │   ├── FileUploadZone.vue
│   │   ├── FileTable.vue
│   │   ├── YouTubeInput.vue
│   │   └── DeleteClassSection.vue
│   └── views/
│       ├── ClassWelcome.vue
│       └── ClassGrid.vue
```

**MODIFIED FILES:**
```
Vue-Frontend/src/
├── stores/classes.js
├── components/features/dashboard/
│   └── Sidebar.vue
├── components/ui/ModalManager.vue
└── views/DashboardView.vue
```

**FILES TO DELETE:**
```
Vue-Frontend/src/components/features/
├── class-management/modals/CreateClassWizard/index.vue
└── dashboard/WelcomeScreen.vue
```

3. **Restart the frontend server**
```bash
cd Vue-Frontend
npm run dev
```

## Environment Variables

**No changes needed** - All existing environment variables remain the same.

## Testing the Implementation

1. **Create a Class**
   - Click the "+" button in the sidebar
   - Fill in class name and description
   - Upload files (PDF, DOCX, etc.) or add YouTube videos
   - Click "Create Class"

2. **View Class Grid**
   - If you have classes but none selected, you'll see a 2x2 grid
   - Click any class card to select it

3. **Edit a Class**
   - Click the info (ℹ️) button next to a class in the sidebar
   - Modify class info, add/remove files, or delete the class

4. **File Management**
   - New files show with green background
   - Deleted files show with red background
   - Modified descriptions show with orange background

## Known Limitations (Phase 2)

1. **Document Processing**: Files are uploaded but not processed yet (coming in Phase 3)
2. **Chat Sessions**: Button is disabled - implementation coming in Phase 4
3. **File Size**: 10MB limit is set but not enforced on upload progress

## API Endpoints Added

```
POST   /api/v1/classes                          # Create class
GET    /api/v1/classes                          # List classes
GET    /api/v1/classes/{id}                     # Get class details
PUT    /api/v1/classes/{id}                     # Update class
DELETE /api/v1/classes/{id}                     # Delete class

POST   /api/v1/documents/classes/{id}/upload         # Upload file
POST   /api/v1/documents/classes/{id}/upload-youtube # Add YouTube video
GET    /api/v1/documents/classes/{id}                # List documents
PUT    /api/v1/documents/{id}                        # Update description
DELETE /api/v1/documents/{id}                        # Delete document
```

## Troubleshooting


1. **Migration fails**: Check your database connection in `.env`
2. **Import errors**: Make sure all new schema files are created
3. **404 errors**: Verify routes are imported in `main.py`


1. **Component not found**: Check file paths and imports
2. **Modal doesn't open**: Verify `ModalManager.vue` has `ClassModal` registered
3. **Classes don't load**: Check browser console for API errors


**"Class code already exists"**
- The system will retry generating a unique code automatically

**"Not a member of this class"**
- User must be added to class via ClassMembership (automatic for owner)

**"File size exceeds limit"**
- Files must be under 10MB

## Next Steps

After verifying everything works:

1. **Phase 3**: Implement document processing (text extraction, embeddings)
2. **Phase 4**: Implement chat interface and AI integration
3. **Phase 5**: Add permission management and usage tracking

## Support

If you encounter issues:
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify all files are in correct locations
4. Ensure database migration completed successfully
