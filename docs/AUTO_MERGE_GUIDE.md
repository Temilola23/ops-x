# Auto-Merge Setup Guide

## Overview
OPS-X now includes **automatic PR merging** powered by GitHub Actions and CodeRabbit reviews.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Your PR Workflow                          │
└─────────────────────────────────────────────────────────────┘

1. Developer creates PR from /refine page
   └─> Backend creates branch + PR on GitHub

2. CodeRabbit reviews PR automatically
   └─> Posts comments, runs pre-merge checks

3. GitHub Action monitors PR status
   └─> Waits for CodeRabbit approval OR human approval

4. All checks pass?
   └─> GitHub Action auto-merges PR
   └─> PR closes, changes go to main ✅

5. If high severity issues found:
   └─> Backend re-refines code automatically
   └─> Creates new PR with fixes
```

---

## What Gets Auto-Deployed

Every new repo created via OPS-X includes:

### 1. **`.coderabbit.yaml`** (Root of repo)
- Configures CodeRabbit pre-merge checks
- 5 custom checks: Security, Breaking Changes, Code Quality, Tests, Best Practices
- Automatically pushed by backend

### 2. **`.github/workflows/auto-merge.yml`** (GitHub Actions)
- Monitors PRs for approvals
- Auto-merges when:
  - CodeRabbit approves OR human approves
  - All CI checks pass
- Automatically pushed by backend

---

## Merge Conditions

A PR will auto-merge if **ANY** of these conditions are met:

### Option 1: Approval + Checks
✅ **CodeRabbit approved** (reviews code, posts approval)  
OR  
✅ **Human approved** (team member manually approves)  
OR  
✅ **GitHub bot approved** (Dependabot, Actions, etc.)  
**AND**  
✅ **All GitHub checks passed** (CI, tests, etc.)

### Option 2: Checks Only
✅ **All GitHub checks passed** (CI, tests, linting, etc.)  
**NO APPROVAL NEEDED!**

This means even if no one reviews the PR, if all automated checks pass, it will auto-merge! Perfect for hackathon speed. 🚀

---

## Testing Auto-Merge

### Test 1: Empty PR (No Changes)
```bash
# This will NOT trigger auto-merge because there are no changes
1. Go to /refine/22
2. Click "Create PR" without changing anything
3. Result: PR created but CodeRabbit has nothing to review
```

### Test 2: Real Change
```bash
# This WILL trigger auto-merge
1. Go to /refine/22
2. Type in textbox: "Change the background color to blue"
3. Click "Create PR"
4. Watch:
   - CodeRabbit reviews within 10 seconds
   - GitHub Action checks approval status
   - PR auto-merges if approved ✅
```

---

## Monitoring Auto-Merge

### Where to See It:
1. **GitHub PR page**: Look for "All checks have passed" badge
2. **Actions tab**: See the "Auto-merge CodeRabbit Approved PRs" workflow running
3. **PR comments**: CodeRabbit will post review, then Action will merge
4. **Backend logs**: Shows PR creation and status updates

### Timeline:

**With CodeRabbit:**
```
PR Created → 10s → CodeRabbit Review → 5s → All Checks Pass → 3s → Auto-Merge ✅
Total: ~18 seconds from PR to merge!
```

**Without CodeRabbit (checks only):**
```
PR Created → All Checks Pass → 2s → Auto-Merge ✅
Total: ~5 seconds from PR to merge! ⚡
```

---

## Manual Override

If you want to **disable auto-merge** for a specific PR:

### Option A: Add `[skip-merge]` to PR title
```
Title: "WIP: Refactor auth [skip-merge]"
```

### Option B: Mark PR as draft
```
# On GitHub, click "Convert to draft"
# Auto-merge workflow skips draft PRs
```

---

## For Old Repos (Created Before This Feature)

If you created a repo before auto-merge was added:

### Manually Add Auto-Merge:
```bash
# 1. Go to your test repo (e.g., car-20251025-174549)
# 2. Create .github/workflows/auto-merge.yml
# 3. Copy content from: /deployment/github-auto-merge.yml
# 4. Commit to main branch
# 5. Done! Auto-merge now works on this repo
```

---

## Troubleshooting

### "PR not auto-merging"
**Checklist:**
1. ✅ Is `.github/workflows/auto-merge.yml` in the repo?
2. ✅ Did CodeRabbit approve the PR?
3. ✅ Are all GitHub checks passing?
4. ✅ Is the PR a draft? (Drafts don't auto-merge)
5. ✅ Does PR have `[skip-merge]` in title?

### "CodeRabbit approved but didn't merge"
- Check GitHub Actions tab for errors
- Make sure repo has "Actions" enabled
- Verify GitHub token has merge permissions

### "Want to test without waiting for CodeRabbit"
- Manually approve the PR as a human reviewer
- Auto-merge will trigger on human approval too

---

## Why Empty PRs Don't Auto-Merge

If you see PRs with "no difference":
- You're pushing the same code twice
- CodeRabbit has nothing to review
- Auto-merge doesn't trigger (no changes = no review)

**Solution:** Make real changes via the `/refine` page before creating PRs.

---

## Next Steps

1. **Test It:** Create a new project via `/scaffold`
2. **Refine It:** Go to `/refine/{project_id}` and request a change
3. **Watch Magic:** Create PR and watch it auto-merge in ~20 seconds
4. **Celebrate:** You now have fully automated code reviews + merging! 🎉

