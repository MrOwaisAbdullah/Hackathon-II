'use client'

/**
 * VoiceInput Component (T079, T080, T082)
 *
 * Provides voice input functionality with microphone button,
 * real-time transcript display, and edit-before-send flow.
 *
 * Features:
 * - Microphone button with visual feedback (pulsing red while recording)
 * - Keyboard shortcut: Ctrl+Shift+V
 * - Real-time transcript display below input field
 * - Edit transcript before sending
 *
 * Usage:
 *   <VoiceInput
 *     onTranscriptReady={(transcript) => sendMessage(transcript)}
 *     language="en-US"
 *   />
 */

import { useState, useEffect, useCallback } from 'react'
import { Mic } from 'lucide-react'
import useVoiceInput from '@/hooks/useVoiceInput'
import type { VoiceLanguage } from '@/hooks/useVoiceInput'

interface VoiceInputProps {
  onTranscriptReady: (transcript: string) => void
  language?: VoiceLanguage
  className?: string
  disabled?: boolean
  placeholder?: string
  autoSend?: boolean  // If true, auto-send transcript when recording stops
}

export function VoiceInput({
  onTranscriptReady,
  language = 'en-US',
  className = '',
  disabled = false,
  placeholder = 'Click microphone and speak...',
  autoSend = false,  // Default to false for backward compatibility
}: VoiceInputProps) {
  const [transcript, setTranscript] = useState('')
  const [isEditing, setIsEditing] = useState(false)

  const {
    transcript: liveTranscript,
    isRecording,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  } = useVoiceInput({
    language,
    onTranscript: (newTranscript) => {
      setTranscript(newTranscript)
    },
    onError: (error) => {
      console.error('[VoiceInput] Error:', error)
      alert(error) // Simple error feedback
    },
  })

  // Keyboard shortcut: Ctrl+Shift+V
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.shiftKey && event.key === 'V') {
        event.preventDefault()
        if (!disabled && isSupported) {
          if (isRecording) {
            stopRecording()
          } else {
            startRecording()
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isRecording, isSupported, startRecording, stopRecording, disabled])

  // Update local transcript when recording stops
  useEffect(() => {
    if (!isRecording && liveTranscript) {
      setTranscript(liveTranscript.trim())

      // Auto-send if enabled and there's a transcript
      if (autoSend && liveTranscript.trim()) {
        onTranscriptReady(liveTranscript.trim())
        // Clear after sending
        setTranscript('')
        setIsEditing(false)
        resetTranscript()
      }
    }
  }, [isRecording, liveTranscript, autoSend, onTranscriptReady, resetTranscript])

  const handleMicClick = useCallback(() => {
    if (!isSupported || disabled) return

    if (isRecording) {
      stopRecording()
    } else {
      // Clear previous transcript and start new recording
      setTranscript('')
      resetTranscript()
      setIsEditing(false)
      startRecording()
    }
  }, [isRecording, isSupported, startRecording, stopRecording, resetTranscript, disabled])

  const handleSend = useCallback(() => {
    if (transcript.trim()) {
      onTranscriptReady(transcript.trim())
      setTranscript('')
      setIsEditing(false)
      resetTranscript()
    }
  }, [transcript, onTranscriptReady, resetTranscript])

  const handleEdit = useCallback((value: string) => {
    setTranscript(value)
    setIsEditing(true)
  }, [])

  // Show message when not supported instead of returning null
  if (!isSupported) {
    return (
      <div className={`voice-input-container ${className}`}>
        <p className="text-xs text-orange-600 bg-orange-50 px-3 py-2 rounded-lg border border-orange-200">
          ⚠️ Voice input requires Chrome or Edge browser. Speech Recognition API not supported in this browser.
        </p>
      </div>
    )
  }

  return (
    <div className={`voice-input-container ${className}`}>
      {/* Transcript Display (T080) */}
      {(transcript || isRecording) && (
        <div className="relative mb-2 rounded-lg border border-gray-300 bg-gray-50 p-3">
          {/* Visual indicator for recording */}
          {isRecording && (
            <div className="absolute left-2 top-2 flex h-2 w-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500"></span>
              </span>
            </div>
          )}

          {/* Editable transcript area (T082) */}
          <textarea
            value={transcript}
            onChange={(e) => handleEdit(e.target.value)}
            placeholder={placeholder}
            className="w-full resize-none rounded border-none bg-transparent p-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            disabled={isRecording}
            readOnly={!isEditing && !isRecording}
          />

          {/* Action buttons */}
          <div className="mt-2 flex items-center justify-between">
            {/* Recording status */}
            {isRecording && (
              <span className="text-xs text-red-600">
                🔴 Recording... Press Ctrl+Shift+V to stop
              </span>
            )}

            {/* Edit/Send buttons */}
            <div className="ml-auto flex space-x-2">
              {transcript && !isRecording && (
                <>
                  <button
                    onClick={() => {
                      setTranscript('')
                      resetTranscript()
                      setIsEditing(false)
                    }}
                    className="rounded-md px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-200"
                  >
                    Clear
                  </button>
                  <button
                    onClick={handleSend}
                    className="rounded-md bg-blue-600 px-3 py-1 text-xs font-medium text-white hover:bg-blue-700"
                  >
                    Send
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Microphone Button (T079) */}
      <button
        onClick={handleMicClick}
        disabled={disabled || !isSupported}
        className={`
          inline-flex items-center justify-center rounded-full p-3
          transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse hover:bg-red-600'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
        title={`Voice input (Ctrl+Shift+V) - ${isRecording ? 'Click to stop' : 'Click to start'}`}
      >
        <Mic className="h-6 w-6" strokeWidth={1.5} />
      </button>

      {/* Help text */}
      {!transcript && !isRecording && (
        <p className="mt-2 text-xs text-gray-500">
          Press Ctrl+Shift+V or click microphone to start voice input
        </p>
      )}
    </div>
  )
}

export default VoiceInput
