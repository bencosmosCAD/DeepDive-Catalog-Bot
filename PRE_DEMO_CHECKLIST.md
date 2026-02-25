# DeepDive Intelligence - Pre-Demo Verification Checklist

Before presenting to the client, perform the following checks to ensure 100% reliability.

## 1. Automated System Check
Run the verification script in the terminal:
```powershell
python verify_deployment.py
```
- [ ] Confirm output says: `[SUCCESS] SYSTEM HEALTHY: READINESS CONFIRMED`

## 2. Visual & Config Check
Open the app (`streamlit run app_v2.py`).
- [ ] **Sidebar Status**: Check the "🛠️ System Status" expander in the sidebar.
    - API Key: Green/Active
    - Index: Green (> 0 Brands)
- [ ] **Theme**: Ensure the app is in Dark Mode (Dark Blue background, White text).

## 3. Functional Walkthrough
Perform a quick test run:
1.  **Search**: Type `Test Suunto` in the main chat.
    - [ ] Confirm results appear.
2.  **Price Tier**: Change "Pricing Level" in sidebar to "Trade".
    - [ ] Confirm app reloads/updates.
3.  **Cart**: Add an item to cart.
    - [ ] Confirm "Shopping Cart" in sidebar validates the item.

## 4. Reset
- [ ] Click the **"🔄 Reset App"** button in the sidebar before the official demo starts.

---
**Troubleshooting:**
- If **API Key** is missing: Check `os.environ` settings in `app_v2.py`.
- If **Index** is 0: Ensure `.pdf` files are in the `data/` folder.
