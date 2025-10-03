## Backend Setup:

1. Install new dependency:

   ```bash
   cd Backend
   pip install firebase-admin==6.5.0
   ```
2. Update .env file with Firebase credentials:

   ```
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   ```
3. Download Firebase service account JSON:

   - Go to Firebase Console > Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save as firebase-credentials.json in Backend folder
4. Run database migration:

   ```bash
   alembic revision --autogenerate -m "add firebase auth fields"
   alembic upgrade head
   ```
5. Start backend:

   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup:

1. Install new dependency:

   ```bash
   cd Vue-Frontend
   npm install firebase
   ```
2. Update .env file with Firebase web config:

   ```
   VITE_FIREBASE_API_KEY=AIza...
   VITE_FIREBASE_AUTH_DOMAIN=studhelper-xxxxx.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=studhelper-xxxxx
   VITE_FIREBASE_STORAGE_BUCKET=studhelper-xxxxx.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
   VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
   ```
3. Start frontend:

   ```bash
   npm run dev
   ```

## Firebase Console Setup:

1. Create Firebase project at https://console.firebase.google.com/
2. Enable Authentication:

   - Go to Build > Authentication
   - Click "Get started"
   - Enable "Email/Password" provider
   - Enable "Google" provider
   - Enable "Microsoft" provider (requires Azure AD setup)
3. Get Web Config:

   - Go to Project Settings > General
   - Scroll to "Your apps"
   - Click web icon (</>)
   - Register app and copy firebaseConfig values to .env
4. Get Service Account:

   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save JSON file as firebase-credentials.json in Backend folder

## Testing:

1. Test email/password registration:

   - Register with email - should create Firebase account
   - Check email for verification link
   - Login with same credentials
2. Test Google OAuth:

   - Click "Continue with Google"
   - Select Google account
   - Should auto-login
3. Test Microsoft OAuth:

   - Click "Continue with Microsoft"
   - Enter Microsoft credentials
   - Should auto-login

## Important Notes:

- Firebase API keys in frontend are MEANT to be public
- Security comes from Firebase Auth rules and backend JWT verification
- All passwords are handled by Firebase (never stored in your DB)
- OAuth users have no password in your database
- Email verification is handled automatically by Firebase
- Password reset is handled by Firebase (sendPasswordResetEmail)
