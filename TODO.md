# Security Fixes & Code Cleanup - Approved Plan
Status: Major Fixes Complete

## Breakdown Steps

### Phase 1: Create .env.example & Settings Fixes
- [x] 1.1 Create `.env.example` with all secrets template
- [x] 1.2 Edit `R_dot/settings.py`: DEBUG=os.getenv, no SECRET_KEY fallback, add APPS_SCRIPT_URL, security headers

### Phase 2: Cleanup main/views.py (Multi-edits)
- [x] 2.1 Remove hardcoded OAuth secrets (FACEBOOK/GOOGLE)
- [x] 2.2 Remove entire duplicate unreachable checkout() block
- [ ] 2.3 Replace custom session auth with Django login()/logout()
- [ ] 2.4 Fix admin_dashboard revenue: use real `sum(order.price * order.quantity)`
- [ ] 2.5 Optimize category_detail(): prefetch_related, remove N+1 loop
- [ ] 2.6 Fix cart add_to_cart(): increment qty if product exists
- [ ] 2.7 Fix google_callback last_name split logic

### Phase 3: Other Fixes
- [x] 3.1 Edit `main/backends.py`: use settings.APPS_SCRIPT_URL
- [x] 3.2 Edit `requirements.txt`: remove duplicates/unused pkgs (dotenv dupe, mptt/js-asset/fake-bpy)

### Phase 4: Test & Deploy Prep
- [x] 4.1 Run `pip install -r requirements.txt`
- [ ] 4.2 `python manage.py check --deploy && makemigrations && migrate`
- [ ] 4.3 Manual tests: auth, checkout, admin dashboard, category pages
- [ ] 4.4 Create git branch `blackboxai/security-fixes` and commit

**Next: 4.2** Django checks/migrations.
