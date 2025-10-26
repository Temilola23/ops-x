import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher([
  '/workspace(.*)',
  '/team(.*)',
  '/refine(.*)',
  '/profile(.*)',
  '/dashboard(.*)',
])

const isPublicRoute = createRouteMatcher([
  '/',
  '/scaffold',
  '/join(.*)',
])

export default clerkMiddleware(async (auth, req) => {
  // Don't protect public routes
  if (isPublicRoute(req)) {
    return
  }
  
  // Protect workspace and project routes
  if (isProtectedRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}

