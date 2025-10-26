'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { SignIn, SignUp, useUser } from '@clerk/nextjs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, Users, CheckCircle2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface InviteDetails {
  project_name: string
  role: string
  inviter_name: string
  project_id: number
  stakeholder_id: number
}

export default function JoinPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { user, isLoaded } = useUser()

  const code = searchParams.get('code')
  const projectId = searchParams.get('project')
  const stakeholderId = searchParams.get('stakeholder')

  const [inviteDetails, setInviteDetails] = useState<InviteDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activating, setActivating] = useState(false)

  // Fetch invite details
  useEffect(() => {
    if (!code || !projectId || !stakeholderId) {
      setError('Invalid invitation link')
      setLoading(false)
      return
    }

    const fetchInviteDetails = async () => {
      try {
        const response = await fetch(`${API_URL}/api/invites/verify?code=${code}&project=${projectId}&stakeholder=${stakeholderId}`)
        const data = await response.json()

        if (data.success) {
          setInviteDetails(data.data)
        } else {
          setError(data.error || 'Invalid or expired invitation')
        }
      } catch (err) {
        setError('Failed to verify invitation')
      } finally {
        setLoading(false)
      }
    }

    fetchInviteDetails()
  }, [code, projectId, stakeholderId])

  // Auto-activate stakeholder when user is signed in
  useEffect(() => {
    if (isLoaded && user && inviteDetails && !activating) {
      activateStakeholder()
    }
  }, [isLoaded, user, inviteDetails])

  const activateStakeholder = async () => {
    if (!user || !code || !stakeholderId) return

    setActivating(true)

    try {
      const response = await fetch(`${API_URL}/api/invites/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          stakeholder_id: parseInt(stakeholderId!),
          clerk_user_id: user.id,
          email: user.emailAddresses[0]?.emailAddress
        })
      })

      const data = await response.json()

      if (data.success) {
        // Redirect to team page
        setTimeout(() => {
          router.push(`/team/${projectId}`)
        }, 1500)
      } else {
        setError(data.error || 'Failed to activate account')
        setActivating(false)
      }
    } catch (err) {
      setError('Failed to activate account')
      setActivating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-pink-50">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-muted-foreground">Verifying invitation...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-pink-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="h-12 w-12 rounded-full bg-red-100 mx-auto mb-4 flex items-center justify-center">
              <span className="text-2xl">❌</span>
            </div>
            <h2 className="text-xl font-bold mb-2">Invalid Invitation</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Go to Home
            </button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (activating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-pink-50">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Welcome to the team!</h2>
            <p className="text-muted-foreground mb-4">
              Activating your account and redirecting to the project...
            </p>
            <Loader2 className="h-8 w-8 animate-spin text-purple-600 mx-auto" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 p-4">
      <div className="container mx-auto py-12">
        <div className="max-w-5xl mx-auto">
          {/* Invite Details Header */}
          <Card className="mb-8">
            <CardContent className="pt-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 mb-4">
                  <Users className="h-8 w-8 text-white" />
                </div>
                <h1 className="text-3xl font-bold mb-2">You've Been Invited!</h1>
                <p className="text-lg text-muted-foreground mb-4">
                  <strong>{inviteDetails?.inviter_name}</strong> invited you to join:
                </p>
                <h2 className="text-2xl font-bold mb-3">{inviteDetails?.project_name}</h2>
                <Badge className="text-base px-4 py-1">
                  {inviteDetails?.role}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Auth Options */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Sign Up */}
            <Card>
              <CardHeader>
                <CardTitle>Create Account</CardTitle>
                <CardDescription>
                  New to OPS-X? Sign up to join the team
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <SignUp 
                  routing="hash"
                  appearance={{
                    elements: {
                      rootBox: "w-full",
                      card: "shadow-none"
                    }
                  }}
                />
              </CardContent>
            </Card>

            {/* Sign In */}
            <Card>
              <CardHeader>
                <CardTitle>Already Have an Account?</CardTitle>
                <CardDescription>
                  Sign in to accept the invitation
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <SignIn 
                  routing="hash"
                  appearance={{
                    elements: {
                      rootBox: "w-full",
                      card: "shadow-none"
                    }
                  }}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

