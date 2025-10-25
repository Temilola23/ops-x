'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { signUp, verifyOTP, type User } from '@/lib/auth'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: (user: User) => void
}

export function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [step, setStep] = useState<'email' | 'otp'>('email')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const handleSignup = async () => {
    if (!email || !name) {
      setError('Please fill in all fields')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')
    
    const result = await signUp(email, name)
    
    if (result.success) {
      setMessage(result.message)
      setStep('otp')
    } else {
      setError(result.message)
    }
    
    setLoading(false)
  }

  const handleVerifyOtp = async () => {
    if (otp.length !== 6) {
      setError('Please enter a 6-digit OTP')
      return
    }

    setLoading(true)
    setError('')
    
    const result = await verifyOTP(email, otp)
    
    if (result.success && result.user) {
      setMessage('Login successful!')
      onSuccess?.(result.user)
      
      // Close modal after short delay
      setTimeout(() => {
        onClose()
        // Reset form
        setStep('email')
        setEmail('')
        setName('')
        setOtp('')
        setError('')
        setMessage('')
      }, 1000)
    } else {
      setError(result.message || 'Invalid OTP. Please try again.')
    }
    
    setLoading(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent, action: () => void) => {
    if (e.key === 'Enter') {
      action()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            {step === 'email' ? 'Welcome to OPS-X' : 'Verify Your Email'}
          </DialogTitle>
          <DialogDescription>
            {step === 'email' 
              ? 'Enter your details to get started' 
              : `We sent a code to ${email}`
            }
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {step === 'email' ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, handleSignup)}
                  placeholder="Your name"
                  disabled={loading}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, handleSignup)}
                  placeholder="you@example.com"
                  disabled={loading}
                />
              </div>

              {message && (
                <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                  {message}
                </div>
              )}

              {error && (
                <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                  {error}
                </div>
              )}

              <Button
                onClick={handleSignup}
                disabled={!email || !name || loading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {loading ? 'Sending...' : 'Continue'}
              </Button>
            </>
          ) : (
            <>
              <div className="space-y-2">
                <Label htmlFor="otp">Enter 6-Digit Code</Label>
                <Input
                  id="otp"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  onKeyPress={(e) => handleKeyPress(e, handleVerifyOtp)}
                  placeholder="000000"
                  maxLength={6}
                  disabled={loading}
                  className="text-center text-2xl tracking-widest font-bold"
                />
                <p className="text-xs text-muted-foreground text-center">
                  Check your email inbox for the verification code
                </p>
              </div>

              {message && (
                <div className="text-sm text-green-600 bg-green-50 p-3 rounded-lg">
                  {message}
                </div>
              )}

              {error && (
                <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Button
                  onClick={handleVerifyOtp}
                  disabled={otp.length !== 6 || loading}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  {loading ? 'Verifying...' : 'Verify & Login'}
                </Button>

                <Button
                  variant="ghost"
                  onClick={() => {
                    setStep('email')
                    setOtp('')
                    setError('')
                    setMessage('')
                  }}
                  className="w-full"
                  disabled={loading}
                >
                  Back
                </Button>
              </div>

              <div className="text-center text-sm text-muted-foreground">
                Didn't receive the code?{' '}
                <button
                  onClick={handleSignup}
                  disabled={loading}
                  className="text-purple-600 hover:underline font-medium"
                >
                  Resend
                </button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

