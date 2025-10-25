# v0 Integration Setup Guide

## 🎯 Overview

OPS-X now uses [v0.dev](https://v0.dev) for beautiful, instant MVP generation. This guide will help you get started.

## 📋 Prerequisites

- Node.js 18+
- v0.dev account
- v0 API key

## 🔑 Step 1: Get Your v0 API Key

1. Go to [v0.dev](https://v0.dev)
2. Sign in or create an account
3. Navigate to **Settings** → **API Keys**
4. Generate a new API key
5. Copy the key (you won't see it again!)

## ⚙️ Step 2: Configure Environment

Create `.env.local` in the frontend directory:

```bash
cd frontend
```

Create the file with:

```bash
# v0 API Configuration
V0_API_KEY=your_actual_api_key_here

# Backend API Configuration (if using)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

**⚠️ Important:** Replace `your_actual_api_key_here` with your real v0 API key!

## 🚀 Step 3: Run the Application

```bash
# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 💡 How to Use

### 1. **Initial Build**

- Click "Start Building Your Startup"
- Enter your project name (e.g., "TaskMaster")
- Describe your app in detail:
  ```
  A todo app with categories, due dates, priority levels,
  and dark mode. Include user authentication and a clean,
  modern design with smooth animations.
  ```
- Press **Cmd/Ctrl + Enter** or click "Build MVP"
- Watch as v0 generates your app in real-time!

### 2. **View Preview**

- See your app live in the **Preview** tab
- The iframe shows v0's hosted preview
- Fully interactive and responsive

### 3. **View Code**

- Switch to the **Code** tab
- See all generated files
- Click "Copy" to copy any file
- Files organized by directory

### 4. **Refine Your App**

After the initial build, you can iteratively improve:

Example refinements:

- "Add dark mode support"
- "Make the navbar sticky"
- "Add user authentication"
- "Include a search bar"
- "Add animations to the todo list"
- "Make it mobile-responsive"

Each refinement updates both the preview AND the code instantly!

## 🎨 Features

### Lovable-Style UX

- ✅ **Real-time Preview**: See changes instantly
- ✅ **Code Viewer**: Inspect all generated files
- ✅ **Iterative Refinement**: Improve your app with follow-up prompts
- ✅ **Copy Code**: One-click copy for any file
- ✅ **Loading Animations**: Beautiful fade effects while generating

### Technical Features

- ✅ **Server-Side Security**: API key never exposed to browser
- ✅ **Next.js Server Actions**: Secure, type-safe v0 calls
- ✅ **TypeScript**: Full type safety throughout
- ✅ **shadcn/ui**: Beautiful, accessible components
- ✅ **Responsive Design**: Works on all devices

## 🏗️ Architecture

```
User Input (Prompt)
    ↓
Next.js Server Action (src/app/actions/v0.ts)
    ↓
v0 SDK (Server-side, secure)
    ↓
v0 API (https://api.v0.dev)
    ↓
Returns:
  - chat.id (for follow-ups)
  - chat.demo (preview URL)
  - chat.files (generated code)
    ↓
BuildWithPreview Component
  ├─ Preview Tab (iframe with chat.demo)
  └─ Code Tab (CodeDisplay component)
```

## 🔧 Troubleshooting

### "Failed to create chat with v0"

**Cause:** Invalid or missing API key

**Fix:**

1. Check your `.env.local` file exists
2. Verify `V0_API_KEY=...` has your actual key
3. Restart the dev server: `npm run dev`
4. Check the terminal for any errors

### Preview not loading

**Cause:** v0 is still generating

**Fix:**

- Wait for the loading overlay to fade
- Check the browser console for errors
- Try refreshing the page

### "Command not found: npm"

**Fix:**

```bash
# Install Node.js from nodejs.org
# Then:
npm install
npm run dev
```

### Changes not reflecting

**Fix:**

```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

## 📚 Example Prompts

### Simple Todo App

```
A minimalist todo app with add, complete, and delete
functionality. Use a clean design with smooth animations.
```

### Dashboard App

```
A SaaS dashboard with sidebar navigation, charts showing
user metrics, a data table with pagination, and a dark mode toggle.
```

### Landing Page

```
A startup landing page with a hero section, feature cards,
pricing table, testimonials, and a contact form. Make it
modern and conversion-focused.
```

### E-commerce Product Page

```
A product detail page for an online store with image gallery,
add to cart button, size selector, reviews section, and
recommended products.
```

## 🎯 Best Practices

1. **Be Specific**: More detail = better results

   - ❌ "A todo app"
   - ✅ "A todo app with categories, due dates, priority tags, and dark mode"

2. **Mention Tech Stack**: Guide v0's choices

   - "Use Next.js 14, shadcn/ui, and Tailwind CSS"

3. **Request Features**: Don't assume

   - "Include user authentication"
   - "Add loading states"
   - "Make it responsive"

4. **Iterate Gradually**: Refine step by step

   - First: Get the basic structure
   - Then: Add dark mode
   - Then: Add animations
   - Then: Add authentication

5. **Save Your Work**: Copy code early
   - Click "Copy" on important files
   - v0 chat persists, but be safe!

## 🔗 Resources

- [v0 Documentation](https://v0.dev/docs)
- [v0 Platform API](https://v0.app/docs/api/platform/quickstart)
- [v0 SDK on npm](https://www.npmjs.com/package/v0-sdk)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Next.js Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)

## 🚨 Important Notes

- **API Key Security**: Never commit `.env.local` to git (it's in `.gitignore`)
- **Server Actions**: Only work in Next.js 13.4+ with App Router
- **Preview URLs**: v0 hosts the preview; it's a live URL anyone can access
- **Rate Limits**: v0 has rate limits; check your plan

## 🎉 You're Ready!

Start building beautiful MVPs in seconds. Happy coding! 🚀
