# Separate Admin/User Authentication Sessions - Manual Session Keys Approach (Simpler, no custom backends)

## Steps to Complete:

### 1. [x] Initial TODO created (updated to manual approach)

### 2. [ ] Update main/views.py
   - Add manual session auth for login_view (user_auth_id/hash)
   - admin_login_view (admin_auth_id/hash)
   - Social callbacks: user_auth
   - Add logout_user_view, logout_admin_view
   - Update decorators: manual get_session_user(), get_session_admin_user()

### 3. [ ] Update main/context_processors.py
   - Add get_current_user(request), get_current_admin_user(request) -> {'user': ..., 'admin_user': ...}

### 4. [ ] Update main/urls.py
   - Add 'logout-user/', 'logout-admin/'

### 5. [ ] Update templates
   - base.html: nav use {{ user.is_authenticated }}
   - admin/base_admin.html: {{ admin_user.is_authenticated }}, admin logout link

### 6. [ ] Test
   - Login user, check /admin-login requires login, session separate
   - Login admin, check profile requires user login
   - Clear one doesn't affect other

**Current Step: 2/6**

### 3. [ ] Update main/context_processors.py
   - Add dual user context processor for templates

### 4. [ ] Update templates
   - main/templates/base.html: Use {{ user }} for user panel nav
   - main/templates/admin/base_admin.html: Use {{ admin_user }}, separate logout

### 5. [ ] Update main/urls.py
   - Add logout-user/ and logout-admin/ paths

### 6. [ ] Update main/views.py
   - Specify backends in login/authenticate/login calls
   - Add logout_user and logout_admin views
   - Update decorators to check correct backend users
   - Ensure social uses UserBackend

### 7. [ ] Test
   - Runserver
   - Test user login doesn't affect admin, vice versa
   - Check decorators protect correctly
   - Verify social logins user-only
   - No cross-session interference

**Current Step: 1/7**

