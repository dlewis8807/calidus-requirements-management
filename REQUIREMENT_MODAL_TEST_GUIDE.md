# Requirement Modal - Complete Testing Guide

## ✅ Issues Fixed

### 1. Backend API Error (500 Internal Server Error)
**Problem**: `AttributeError: 'TraceabilityLink' object has no attribute 'updated_at'`
**Solution**: Set `updated_at=None` for all traceability links in API responses

### 2. Frontend Authentication
**Problem**: Modal only checked for `demo_token`, failed with admin login
**Solution**: Check multiple token locations: `access_token`, `token`, `demo_token`

### 3. Database Empty
**Problem**: No requirements loaded for testing
**Solution**: Generated 16,600 requirements and 28,523 test cases

## 📁 Files Modified

### Backend
- `backend/app/api/requirements.py` - Fixed traceability link responses (4 locations)

### Frontend
- `frontend/components/RequirementModal.tsx` - Fixed token retrieval
- `frontend/app/demo/page.tsx` - Integrated modal
- `frontend/app/dashboard/requirements/page.tsx` - Integrated modal
- `frontend/app/dashboard/requirements/[id]/page.tsx` - Integrated modal
- `frontend/app/dashboard/test-cases/page.tsx` - Integrated modal
- `frontend/app/dashboard/traceability/page.tsx` - Integrated modal

## 🧪 Manual Testing Instructions

### Prerequisites
1. Backend running: http://localhost:8000
2. Frontend running: http://localhost:3000
3. Database populated with sample data
4. Admin credentials: `admin` / `demo2024`

---

### TEST 1: Demo Page (Public)
**URL**: http://localhost:3000/demo

**Steps**:
1. Navigate to demo page
2. Click "Connect & Import from ENOVIA"
3. Wait for requirements to load
4. Click on any requirement ID badge (blue buttons like "AHLR-001")

**Expected Result**:
- ✅ Modal opens showing full requirement details
- ✅ No "Authentication required" error
- ✅ Regulatory information displayed
- ✅ Test cases shown (if any)
- ✅ Traceability links displayed
- ✅ Can click traceability links to navigate between requirements

**Failure Indicators**:
- ❌ "Authentication required" error
- ❌ Modal doesn't open
- ❌ 404 or 500 error in browser console

---

### TEST 2: Requirements List Page
**URL**: http://localhost:3000/dashboard/requirements

**Steps**:
1. Login as admin (admin / demo2024)
2. Navigate to Requirements page
3. Scroll through the requirements list
4. Click on any requirement ID in the first column

**Expected Result**:
- ✅ Modal opens immediately
- ✅ Requirement details loaded
- ✅ No console errors
- ✅ Modal displays:
  - Requirement ID, title, description
  - Status and priority badges
  - Regulatory source (if applicable)
  - Test cases count
  - Parent/child requirements

**Failure Indicators**:
- ❌ "Authentication required" error
- ❌ "Failed to fetch requirement" error
- ❌ Modal opens but stays loading forever
- ❌ 500 error in backend logs

---

### TEST 3: Requirement Detail Page (Traceability)
**URL**: http://localhost:3000/dashboard/requirements/[any-id]

**Steps**:
1. From Requirements list, click "View" icon (eye) on any requirement
2. Scroll to "Traceability" section
3. Look for "Parent Requirements" or "Child Requirements"
4. Click on any requirement ID button in the traceability cards

**Expected Result**:
- ✅ Modal opens showing the clicked requirement
- ✅ Can navigate to another requirement from within the modal
- ✅ Closing modal returns to detail page

**Failure Indicators**:
- ❌ Clicking does nothing
- ❌ Page navigates away instead of opening modal
- ❌ Modal doesn't load data

---

### TEST 4: Test Cases Page
**URL**: http://localhost:3000/dashboard/test-cases

**Steps**:
1. Navigate to Test Cases page
2. Find a test case with a linked requirement (look in "Requirement" column)
3. Click on the requirement ID (should be blue clickable text)

**Expected Result**:
- ✅ Modal opens showing the linked requirement
- ✅ Requirement details fully loaded
- ✅ Shows how the test case verifies this requirement

**Failure Indicators**:
- ❌ "No requirement" shown for all test cases
- ❌ Requirement ID not clickable
- ❌ 404 error when clicking

---

### TEST 5: Traceability Page
**URL**: http://localhost:3000/dashboard/traceability

**Steps**:
1. Navigate to Traceability page
2. Scroll to "Traceability Gaps" section
3. Click on any requirement ID in the "Requirement" column

**Expected Result**:
- ✅ Modal opens showing requirement details
- ✅ Shows why this requirement has a traceability gap
- ✅ Can navigate to related requirements

**Failure Indicators**:
- ❌ Clicking navigates to detail page instead
- ❌ Modal doesn't open
- ❌ Error loading requirement

---

### TEST 6: Cross-Page Navigation
**Steps**:
1. Open Requirements page
2. Click a requirement ID to open modal
3. In the modal, click a parent/child requirement ID
4. From that requirement, click another traceability link
5. Repeat 2-3 times

**Expected Result**:
- ✅ Can navigate through multiple requirements without closing modal
- ✅ Each click loads new requirement data
- ✅ No memory leaks or slowdown
- ✅ Back button on modal still works

**Failure Indicators**:
- ❌ Modal closes when clicking requirement links
- ❌ Modal gets stuck loading
- ❌ Browser becomes slow/unresponsive

---

## 🔍 Browser Console Checks

### Open Developer Tools (F12)
Check for these in the Console tab:

**Good Signs** ✅:
```
GET http://localhost:8000/api/requirements/by-req-id/AHLR-001 200 OK
```

**Bad Signs** ❌:
```
GET http://localhost:8000/api/requirements/by-req-id/AHLR-001 500 Internal Server Error
Authentication required
Failed to fetch requirement: Unauthorized
```

### Network Tab
Filter by "by-req-id" and check:
- ✅ Status: 200 OK
- ✅ Response includes: `requirement_id`, `title`, `test_cases`, `parent_traces`, `child_traces`
- ❌ Status: 401, 404, or 500
- ❌ Response: `{"detail": "error message"}`

---

## 🐛 Troubleshooting

### Problem: "Authentication required" in modal
**Solution**:
1. Check localStorage in browser dev tools
2. Should have one of: `access_token`, `token`, or `demo_token`
3. If missing, log out and log back in
4. Verify token in localStorage after login

### Problem: 404 Not Found
**Cause**: Requirement doesn't exist in database
**Solution**:
1. Check requirement ID is valid (e.g., "AHLR-001" not "AHLR001")
2. Verify database has requirements:
   ```bash
   docker compose exec backend python -c "from app.database import SessionLocal; from app.models.requirement import Requirement; db = SessionLocal(); print(f'Total requirements: {db.query(Requirement).count()}')"
   ```

### Problem: 500 Internal Server Error
**Check backend logs**:
```bash
docker compose logs backend --tail=50
```

**Common Errors**:
- `AttributeError: 'TraceabilityLink' object has no attribute 'updated_at'`
  - **Fix**: Restart backend after code changes
  - ```bash
    docker compose restart backend
    ```

### Problem: Modal opens but never loads
**Causes**:
1. Backend not running
2. CORS issue
3. Token expired

**Solutions**:
1. Check backend health: http://localhost:8000/health
2. Check browser console for CORS errors
3. Log out and log back in to refresh token

---

## ✅ Success Criteria

All pages should:
1. ✅ Display requirement IDs as clickable elements (blue text/buttons)
2. ✅ Open modal when clicking requirement ID
3. ✅ Load requirement data within 2 seconds
4. ✅ Display complete information (title, description, status, etc.)
5. ✅ Show traceability links (if any)
6. ✅ Show test cases (if any)
7. ✅ Allow navigation between requirements within modal
8. ✅ Close modal when clicking X or outside modal
9. ✅ No console errors
10. ✅ No backend errors in logs

---

## 📊 System Status

**Backend**: http://localhost:8000
- ✅ Running
- ✅ API endpoint: `/api/requirements/by-req-id/{req_id}`
- ✅ 16,600 requirements loaded
- ✅ 28,523 test cases loaded
- ✅ 15,093 traceability links created

**Frontend**: http://localhost:3000
- ✅ Running
- ✅ All pages compiled successfully
- ✅ RequirementModal integrated on 5 pages

**Database**: PostgreSQL
- ✅ Populated with sample data
- ✅ All relationships established

---

## 🎯 Quick Smoke Test (2 minutes)

1. Login: http://localhost:3000/login (admin / demo2024)
2. Requirements: Click any requirement ID → Modal opens ✅
3. Test Cases: Click any requirement link → Modal opens ✅
4. Traceability: Click any requirement ID → Modal opens ✅
5. Demo page: Click "Connect", then click requirement ID → Modal opens ✅

**If all 5 tests pass**: System is working correctly! 🎉
**If any test fails**: See troubleshooting section above
