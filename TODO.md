# eCommerce Size/Product Type Implementation TODO

## Plan Steps

- [x] **Step 1: Update main/models.py** ✅ - Add `is_fashion` to Product, `available_sizes` JSONField, `size`/`price` to NewOrder. (price default=0 for migration)
- [x] **Step 2: Run migrations** ✅ (attempted)
- [x] **Step 3: Update main/admin.py** ✅ - Custom ProductAdmin with conditional size checkboxes.
- [x] **Step 4: Update create_media_records.py** ✅ - Set is_fashion=True for fashion products.
- [ ] **Step 5: Update main/views.py** - Cart session with sizes, checkout validation.
- [ ] **Step 6: Update main/forms.py** - Dynamic CheckoutForm for per-item size/qty.
- [ ] **Step 7: Update templates** - product_detail.html (size dropdown), cart.html (edit size), checkout.html (per-item forms/validation).
- [ ] **Step 8: Update main/backends.py** - Correct Apps Script URL, add size to payload.
- [ ] **Step 9: Test** - Admin create fashion/non-fashion, cart/checkout flow, validation, Sheets.
- [x] **Step 0: Create this TODO.md** ✅

**Next:** Proceed to Step 1 after confirmation.

