### SETUP INSTRUCTIONS

## Backend Setup:

1. Run database migration:

   ```bash
   cd Backend
   alembic upgrade head
   ```
2. Restart backend:

   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup:

No changes to dependencies needed. Just restart:

```bash
cd Vue-Frontend
npm run dev
```

## Testing:

1. Register new user with email/password:

   - Fill in Name, Surname, Email
   - Optionally add Alias
   - Create password
   - Verify display name in dashboard
2. Test OAuth (Google/Microsoft):

   - OAuth will auto-generate name/surname from display name
   - User will be shown with display name
3. Test display name logic:

   - User with alias → Shows alias
   - User without alias → Shows "Name Surname"
4. Verify JWT token:

   - JWT now uses user.id as subject (not username)
   - Login only accepts email (not username)

## Database Changes Summary:

REMOVED:

- username (unique column)
- full_name (optional column)

ADDED:

- name (required)
- surname (required)
- alias (optional, not unique)

JWT CHANGE:

- Subject changed from username to user.id
- More stable (won't break if name changes)

## Display Name Logic:

Frontend (auth store):

- displayName computed property returns user.display_name
- Falls back to "Name Surname" if display_name not set

Backend (auth service):

- _get_display_name() returns alias if set, otherwise "Name Surname"
- Automatically added to UserResponse
