# Signup/Login Form Fixes - TODO List

## Completed Tasks
- [x] Create custom UserCreationForm with email validation
- [x] Update signup view to use custom form
- [x] Update signup.html to display form errors using Django form rendering
- [x] Update login.html to display error messages
- [x] Fix signup link in login.html
- [x] Add CSS styles for form error display
- [x] Fix login function naming conflict (renamed to login_view)

## Summary of Changes
1. **main/forms.py**: Created CustomUserCreationForm with email field and uniqueness validation
2. **main/views.py**: Updated signup view to use CustomUserCreationForm, renamed login function to login_view to avoid naming conflict
3. **main/urls.py**: Updated URL pattern to use login_view instead of login
4. **main/templates/signup.html**: Replaced manual HTML inputs with Django form rendering to show validation errors
5. **main/templates/login.html**: Added error message display and fixed signup link
6. **main/static/css/style.css**: Added styles for form errors and field-specific errors

## Testing Required
- Test signup with valid data
- Test signup with invalid data (duplicate email, password mismatch, etc.)
- Test login with valid/invalid credentials
- Verify error messages are displayed correctly
