# CodeRabbit Integration Setup Guide

## How CodeRabbit Actually Works

CodeRabbit is **NOT webhook-based**. It works via **GitHub App installation**.

### Architecture:
```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Developer creates PR                                   │ │
│  │  2. CodeRabbit GitHub App automatically triggers           │ │
│  │  3. CodeRabbit analyzes code & posts review comments       │ │
│  │  4. Pre-merge checks block PR if configured                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                         ┌─────────────┐
                         │ CodeRabbit  │
                         │  (GitHub    │
                         │    App)     │
                         └─────────────┘
```

**Key Points:**
- CodeRabbit reviews PRs **automatically** when installed
- It posts comments **directly on GitHub PRs**
- It can **block merges** via pre-merge checks
- **NO webhooks are sent to external systems**

---

## Setup Instructions

### Step 1: Install CodeRabbit GitHub App

1. Go to: https://github.com/apps/coderabbitai
2. Click **Install**
3. Select your GitHub account or organization
4. Choose repositories:
   - **All repositories** (recommended for OPS-X)
   - OR select specific repos
5. Grant permissions and complete installation

### Step 2: Configure API Key (Optional)

If you want to use CodeRabbit's API for programmatic access:

1. Go to https://coderabbit.ai/settings
2. Generate an API key
3. Add to OPS-X `.env`:
   ```bash
   CODERABBIT_API_KEY=your_api_key_here
   ```

**Note:** OPS-X has already saved your API key: `cr-0c02bf...c1`

### Step 3: .coderabbit.yaml Configuration

OPS-X automatically pushes `.coderabbit.yaml` to every generated repo with:

- **Built-in checks**: Title, description, docstrings (70% threshold)
- **Custom checks**:
  - Breaking Changes Documentation (error mode)
  - Security Review (error mode)
  - Code Quality Standards (warning mode)
  - Test Coverage (warning mode)
  - OPS-X Best Practices (warning mode)

**Location:** `/deployment/coderabbit.yaml` in OPS-X repo

**Auto-deployment:** When you push to GitHub via OPS-X, this config is automatically included.

---

## How to Use with OPS-X

### For Initial Project Creation (Scaffold):
1. Generate your MVP on OPS-X homepage
2. Click "Push to GitHub"
3. OPS-X automatically:
   - Creates GitHub repo
   - Pushes your code
   - **Adds .coderabbit.yaml**
4. CodeRabbit is now active on that repo!

### For Refinements (Create PR):
1. Go to `/refine/{projectId}`
2. Request a refinement
3. Click "Create PR"
4. **CodeRabbit automatically reviews the PR**
5. CodeRabbit posts comments on GitHub with:
   - Code quality issues
   - Security vulnerabilities
   - Pre-merge check results
6. If errors are found (and `request_changes_workflow: true`):
   - PR is **blocked from merging**
   - Developer must fix issues or click "Ignore failed checks"

---

## Pre-Merge Checks Explained

### Enforcement Modes:
- **`off`**: Check disabled
- **`warning`**: Shows warnings but doesn't block merge
- **`error`**: Blocks merge if check fails (requires `request_changes_workflow: true`)

### OPS-X Default Checks:

| Check                             | Mode    | Blocks Merge? |
|-----------------------------------|---------|---------------|
| **Title**                         | warning | No            |
| **Description**                   | warning | No            |
| **Docstrings** (70% threshold)    | warning | No            |
| **Breaking Changes Documentation**| error   | **Yes**       |
| **Security Review**               | error   | **Yes**       |
| **Code Quality Standards**        | warning | No            |
| **Test Coverage**                 | warning | No            |
| **OPS-X Best Practices**          | warning | No            |

### Example: Security Review Check Blocks PR

1. Developer creates PR that hardcodes an API key
2. CodeRabbit reviews and finds: `hardcoded credential in api.ts`
3. Pre-merge check: **Security Review - FAILED (Error)**
4. GitHub blocks merge (red X on PR)
5. Developer must:
   - Remove hardcoded key
   - Push update
   - CodeRabbit re-reviews
   - Check passes → PR unblocked

---

## Testing CodeRabbit

### Test 1: Create a Simple PR
```bash
# On an OPS-X generated repo
git checkout -b test-coderabbit
echo "console.log('test')" >> app/page.tsx
git commit -am "Test: Add console.log"
git push origin test-coderabbit
```

**Expected:**
- CodeRabbit automatically reviews
- Posts comment: "Remove console.log in production code"
- Pre-merge check: **Code Quality Standards - WARNING**

### Test 2: Trigger Security Block
```bash
git checkout -b security-test
echo "const API_KEY = 'sk-1234567890abcdef'" >> app/api/route.ts
git commit -am "Test: Add API key"
git push origin security-test
```

**Expected:**
- CodeRabbit reviews
- Posts comment: "Hardcoded credential detected"
- Pre-merge check: **Security Review - ERROR**
- **PR merge is BLOCKED**

---

## CodeRabbit Commands

Use these in PR comments to control CodeRabbit:

### Request Review:
```
@coderabbitai review
```

### Ignore Failed Checks (Unblock PR):
```
@coderabbitai ignore pre-merge checks
```

### Re-run Pre-Merge Checks:
```
@coderabbitai run pre-merge checks
```

### Test Custom Check:
```
@coderabbitai evaluate custom pre-merge check --name "Security Review" --instructions "Check for hardcoded secrets" --mode error
```

### Generate Summary:
```
@coderabbitai summary
```

### Pause Auto-Reviews:
```
@coderabbitai pause
```

### Resume Auto-Reviews:
```
@coderabbitai resume
```

---

## Integration with OPS-X Backend

### What OPS-X Does:
1. **Automatic Config Deployment**: Pushes `.coderabbit.yaml` to every repo
2. **GitHub Webhook Monitoring** (optional): Track PR lifecycle events
3. **Refinement Status Sync**: Update database when PRs are merged/closed

### What CodeRabbit Does:
1. **Automatic PR Reviews**: Every PR is reviewed within seconds
2. **Block Bad Code**: Pre-merge checks prevent issues from landing
3. **Learning**: Adapts to your team's patterns over time

### No Custom Integration Needed:
- CodeRabbit works **out of the box** once installed
- No API calls from OPS-X to CodeRabbit
- No webhooks from CodeRabbit to OPS-X
- Everything happens natively on GitHub

---

## Pricing

- **Free Tier**: Public repos (unlimited)
- **Pro Tier**: $15/user/month
  - Private repos
  - Agentic pre-merge checks (up to 5 custom checks during preview)
  - MCP integrations
  - Priority support

**For OPS-X Hackathon**: Use free tier for public repos or Pro trial for private repos.

---

## Troubleshooting

### CodeRabbit Not Reviewing PRs:
1. Check if CodeRabbit GitHub App is installed on the repo
2. Verify repo is not in `.coderabbitignore`
3. Check PR description for `@coderabbitai ignore`
4. Re-trigger: Comment `@coderabbitai review`

### Pre-Merge Checks Not Blocking:
1. Ensure `request_changes_workflow: true` in `.coderabbit.yaml`
2. Check enforcement mode is `error` not `warning`
3. Verify GitHub branch protection settings allow CodeRabbit to block

### Want to Disable for a PR:
Add to PR description:
```
@coderabbitai ignore
```

### Want to Change Check Severity:
Edit `.coderabbit.yaml` in repo:
```yaml
reviews:
  pre_merge_checks:
    custom_checks:
      - name: "Security Review"
        mode: "warning"  # Changed from "error"
```

---

## Next Steps

1. ✅ **Install CodeRabbit** on your GitHub account
2. ✅ **Generate a project** on OPS-X (it will auto-add .coderabbit.yaml)
3. ✅ **Create a test PR** to see CodeRabbit in action
4. ✅ **Customize checks** in `.coderabbit.yaml` if needed
5. ✅ **Iterate** on refinements with automatic PR reviews

**That's it!** CodeRabbit now protects all your OPS-X projects. 🎉

