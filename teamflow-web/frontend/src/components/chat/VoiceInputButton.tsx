'use client'

/**
 * VoiceInputButton - Compact microphone button for voice input
 *
 * A minimal voice input button that:
 * - Shows only the microphone icon (no separate textarea)
 * - Auto-sends transcript when recording stops
 * - Shows recording status with visual feedback
 * - Positioned to overlay near chat input area
 */

import { useState } from 'react'
import { Mic } from 'lucide-react'
import useVoiceInput from '@/hooks/useVoiceInput'
import type { VoiceLanguage } from '@/hooks/useVoiceInput'

interface VoiceInputButtonProps {
  onTranscriptReady: (transcript: string) => void
  language?: VoiceLanguage
  disabled?: boolean
}

export function VoiceInputButton({
  onTranscriptReady,
  language = 'en-US',
  disabled = false,
}: VoiceInputButtonProps) {
  const [showError, setShowError] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const {
    transcript,
    isRecording,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  } = useVoiceInput({
    language,
    onTranscript: (newTranscript) => {
      // Auto-send when we get a transcript
      if (newTranscript.trim()) {
        onTranscriptReady(newTranscript.trim())
      }
    },
    onError: (error) => {
      console.error('[VoiceInputButton] Error:', error)
      setErrorMessage(error)
      setShowError(true)
      setTimeout(() => setShowError(false), 3000)
    },
  })

  const handleClick = () => {
    if (!isSupported || disabled) return

    if (isRecording) {
      stopRecording()
    } else {
      resetTranscript()
      startRecording()
    }
  }

  // Don't render if not supported (silent fail)
  if (!isSupported) {
    return null
  }

  return (
    <>
      {/* Compact microphone button */}
      <button
        onClick={handleClick}
        disabled={disabled}
        className={`
          flex items-center justify-center rounded-full transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse hover:bg-red-600 w-10 h-10'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 w-9 h-9'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
        title={isRecording ? 'Click to stop recording' : 'Click to start voice input (Ctrl+Shift+V)'}
      >
        <Mic className="h-5 w-5" strokeWidth={1.5} />
      </button>

      {/* Recording indicator - small popup */}
      {isRecording && (
        <div className="fixed bottom-28 right-8 z-[10001] bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm flex items-center space-x-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500"></span>
          </span>
          <span>Recording... Speak now</span>
        </div>
      )}

      {/* Error toast */}
      {showError && (
        <div className="fixed bottom-28 right-8 z-[10002] bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm max-w-xs">
          {errorMessage}
        </div>
      )}

      {/* Transcript preview (hidden - auto-sends) */}
      {transcript && (
        <div className="sr-only">
          Transcript: {transcript}
        </div>
      )}
    </>
  )
}

export default VoiceInputButton
