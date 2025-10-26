# CodeRabbit Quick Start (2 Minutes)

## TL;DR

**CodeRabbit = GitHub App (NOT Webhook)**

1. **Install**: https://github.com/apps/coderabbitai
2. **Done!** OPS-X automatically adds `.coderabbit.yaml` when you push to GitHub
3. CodeRabbit reviews every PR automatically

---

## 3-Step Setup

### 1️⃣ Install CodeRabbit (1 minute)
```
https://github.com/apps/coderabbitai
→ Install
→ Select "All repositories" or specific ones
→ Authorize
```

### 2️⃣ Generate Project on OPS-X (2 minutes)
```
opsx.com → Enter prompt → "Generate My MVP"
→ Preview loads
→ Click "Push to GitHub"
→ .coderabbit.yaml is automatically added ✅
```

### 3️⃣ Create a Test PR (1 minute)
```bash
git checkout -b test
echo "test" >> app/page.tsx
git commit -am "Test"
git push origin test
```

**Result:** CodeRabbit auto-reviews within 10 seconds!

---

## What You Get

✅ **Automatic PR Reviews** - Every PR reviewed in <10 seconds  
✅ **Security Scanning** - Blocks hardcoded secrets, SQL injection, XSS  
✅ **Code Quality** - Flags console.log, missing error handling, poor TypeScript  
✅ **Breaking Changes Guard** - Requires documentation for API changes  
✅ **Smart Blocking** - Bad code can't merge (error-mode checks)  

---

## Control via Comments

```bash
@coderabbitai review           # Re-run review
@coderabbitai ignore pre-merge checks  # Unblock PR
@coderabbitai summary          # Generate PR summary
@coderabbitai pause            # Stop auto-reviews
```

---

## Default Checks (OPS-X)

| Check | Blocks Merge? |
|-------|---------------|
| Security Review | ✅ **YES** |
| Breaking Changes | ✅ **YES** |
| Code Quality | ⚠️ Warning only |
| Test Coverage | ⚠️ Warning only |

---

## Pricing

- **Free**: Public repos (unlimited)
- **$15/month**: Private repos + advanced features

**Hackathon**: Use free tier for public repos!

---

## Example: Security Block

```typescript
// ❌ This would get BLOCKED:
const API_KEY = "sk-1234567890"

// ✅ This would PASS:
const API_KEY = process.env.API_KEY
```

**CodeRabbit detects the hardcoded key and blocks the PR from merging.**

---

## Full Docs

See [`CODERABBIT_SETUP.md`](./CODERABBIT_SETUP.md) for:
- Detailed configuration
- Custom check examples
- Troubleshooting
- Advanced usage

---

## Support

- **Docs**: https://docs.coderabbit.ai
- **API Key**: Already saved in OPS-X `.env`
- **Status**: Check GitHub "Checks" tab on any PR

