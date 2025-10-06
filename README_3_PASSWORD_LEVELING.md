### SETUP INSTRUCTIONS

No database migration needed - only frontend and backend logic changes.

## Frontend Changes:

1. RegisterForm.vue - Password confirmation, strength indicator, better errors
2. LoginForm.vue - Better error messages
3. UserMenu.vue - Display user alias/name next to avatar

## Backend Changes:

1. auth_service.py - Password validation function
2. security.py - validate_password_strength() function

## Testing Checklist:

### Registration:

1. ✅ Try weak password (less than 6 chars) - should show red
2. ✅ Add uppercase - should show yellow
3. ✅ Add 3 numbers - should show green
4. ✅ Password confirmation mismatch - should show error
5. ✅ Try existing email - should show detailed error with provider
6. ✅ Valid registration - should succeed

### Login:

1. ✅ Wrong email - should say "No account found"
2. ✅ Wrong password - should say "Incorrect password"
3. ✅ Too many attempts - should show rate limit message
4. ✅ Valid login - should succeed

### Dashboard:

1. ✅ Check top-right - should show alias or "Name Surname"
2. ✅ On mobile - name should be hidden, only avatar visible
3. ✅ Click dropdown - should show full name and email

## Password Requirements Summary:

- Minimum 6 characters
- At least 1 uppercase letter (A-Z)
- At least 3 numbers (0-9)
- Backend validates on registration
- Firebase also validates (keeps its own rules)

## Display Name Logic:

- If alias is set → Show alias
- If alias is null → Show "Name Surname"
- Responsive: Hidden on mobile (<1024px), visible on desktop
