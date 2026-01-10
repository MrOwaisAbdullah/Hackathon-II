'use client'

/**
 * useVoiceInput Hook (T077, T078, T081)
 *
 * Provides voice input functionality using Web Speech API (SpeechRecognition).
 * Supports English (en-US) and Urdu (ur-PK) transcription.
 * Includes browser compatibility check.
 *
 * Features:
 * - startRecording(): Begin voice capture
 * - stopRecording(): Stop and finalize transcript
 * - isSupported: Browser compatibility flag
 * - transcript: Real-time transcription
 * - isRecording: Recording state
 *
 * Browser Support: Chrome, Edge (Chromium-based)
 */

import { useState, useCallback, useEffect, useRef } from 'react'

export type VoiceLanguage = 'en-US' | 'ur-PK'

interface UseVoiceInputOptions {
  language?: VoiceLanguage
  onTranscript?: (transcript: string) => void
  onError?: (error: string) => void
}

interface UseVoiceInputResult {
  transcript: string
  isRecording: boolean
  isSupported: boolean
  startRecording: () => void
  stopRecording: () => void
  resetTranscript: () => void
}

// Extend Window interface for Speech Recognition
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition
    webkitSpeechRecognition: typeof SpeechRecognition
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onresult: (event: SpeechRecognitionEvent) => void
  onerror: (event: SpeechRecognitionErrorEvent) => void
  onend: () => void
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionResultList {
  readonly length: number
  item(index: number): SpeechRecognitionResult
  [index: number]: SpeechRecognitionResult
}

interface SpeechRecognitionResult {
  readonly length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
  isFinal: boolean
}

interface SpeechRecognitionAlternative {
  transcript: string
  confidence: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

// Helper to get SpeechRecognition constructor safely (SSR-compatible)
const getSpeechRecognitionConstructor = () => {
  if (typeof window === 'undefined') return null
  return (window.SpeechRecognition || window.webkitSpeechRecognition) as {
    new (): SpeechRecognition
  } | null
}

export function useVoiceInput({
  language = 'en-US',
  onTranscript,
  onError,
}: UseVoiceInputOptions = {}): UseVoiceInputResult {
  const [transcript, setTranscript] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  // Store callbacks in refs to avoid recreation
  const onTranscriptRef = useRef(onTranscript)
  const onErrorRef = useRef(onError)

  // Keep refs in sync with props
  useEffect(() => {
    onTranscriptRef.current = onTranscript
  }, [onTranscript])

  useEffect(() => {
    onErrorRef.current = onError
  }, [onError])

  // Check browser support on mount
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return

    const supported = !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    setIsSupported(supported)

    if (!supported) {
      console.warn('[useVoiceInput] Speech Recognition API not supported in this browser')
    }
  }, [])

  // Initialize recognition instance
  useEffect(() => {
    if (!isSupported) return

    const SpeechRecognition = getSpeechRecognitionConstructor()
    if (!SpeechRecognition) return

    console.log('[useVoiceInput] >>> INIT: Initializing Speech Recognition with language:', language)

    const recognition = new SpeechRecognition()
    recognition.continuous = true  // Keep true for continuous listening
    recognition.interimResults = true
    recognition.lang = language

    // Add more event listeners for debugging
    recognition.onaudiostart = () => {
      console.log('[useVoiceInput] >>> AUDIO START: Audio capturing started')
    }
    recognition.onaudioend = () => {
      console.log('[useVoiceInput] >>> AUDIO END: Audio capturing ended')
    }
    recognition.onspeechstart = () => {
      console.log('[useVoiceInput] >>> SPEECH START: Speech detected')
    }
    recognition.onspeechend = () => {
      console.log('[useVoiceInput] >>> SPEECH END: Speech ended')
    }
    recognition.onstart = () => {
      console.log('[useVoiceInput] >>> START: Recognition started')
    }

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      console.log('[useVoiceInput] >>> RESULT: onresult fired - resultIndex:', event.resultIndex, 'results length:', event.results.length)

      let interimTranscript = ''
      let finalTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const transcript = result[0].transcript

        console.log('[useVoiceInput] Result:', i, 'isFinal:', result.isFinal, 'transcript:', transcript, 'confidence:', result[0].confidence)

        if (result.isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }

      // Update with final transcript, append interim for visual feedback
      setTranscript(prev => {
        const newTranscript = prev + finalTranscript
        // Call callback with full transcript including interim
        const fullTranscript = newTranscript + interimTranscript
        console.log('[useVoiceInput] Full transcript:', fullTranscript)

        if (onTranscriptRef.current) {
          onTranscriptRef.current(fullTranscript.trim())
        }
        // Only show interim in UI temporarily
        return newTranscript + interimTranscript
      })
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('[useVoiceInput] >>> ERROR:', event.error, event.message)

      // Handle "aborted" as normal stop (user clicked stop or recording ended)
      if (event.error === 'aborted') {
        console.log('[useVoiceInput] Recording stopped normally (aborted)')
        setIsRecording(false)
        return
      }

      // Handle "no-speech" - this is expected if user doesn't speak
      if (event.error === 'no-speech') {
        console.log('[useVoiceInput] No speech detected - user may not have spoken')
        const errorMessage = 'No speech detected. Please try again.'
        if (onErrorRef.current) {
          onErrorRef.current(errorMessage)
        }
        setIsRecording(false)
        return
      }

      let errorMessage = 'Voice input error'
      switch (event.error) {
        case 'audio-capture':
          errorMessage = 'Microphone not found or not allowed.'
          break
        case 'not-allowed':
          errorMessage = 'Microphone permission denied.'
          break
        case 'network':
          errorMessage = 'Network error. Please check your connection.'
          break
        default:
          errorMessage = `Error: ${event.error}`
      }

      if (onErrorRef.current) {
        onErrorRef.current(errorMessage)
      }

      setIsRecording(false)
    }

    recognition.onend = () => {
      console.log('[useVoiceInput] >>> END: Recognition ended, isRecording was:', isRecording)
      setIsRecording(false)
    }

    recognitionRef.current = recognition

    return () => {
      console.log('[useVoiceInput] >>> CLEANUP: Aborting recognition')
      if (recognitionRef.current) {
        recognitionRef.current.abort()
        recognitionRef.current = null
      }
    }
  }, [isSupported, language]) // Removed onTranscript and onError from deps

  const startRecording = useCallback(() => {
    console.log('[useVoiceInput] >>> CLICK: startRecording called')
    console.log('[useVoiceInput] State check - isSupported:', isSupported, 'isRecording:', isRecording)

    if (!isSupported) {
      const error = 'Speech Recognition is not supported in this browser. Please use Chrome or Edge.'
      console.error('[useVoiceInput]', error)
      if (onErrorRef.current) {
        onErrorRef.current(error)
      }
      return
    }

    if (isRecording) {
      console.warn('[useVoiceInput] Already recording, ignoring start request')
      return
    }

    const recognition = recognitionRef.current
    console.log('[useVoiceInput] Recognition instance:', recognition ? 'EXISTS' : 'NULL')

    if (recognition) {
      try {
        console.log('[useVoiceInput] Starting recording process...')
        // Request microphone access explicitly
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then((stream) => {
            console.log('[useVoiceInput] >>> SUCCESS: Microphone access granted, stream tracks:', stream.getTracks().length)
            // Stop the media stream immediately - we just needed permission
            stream.getTracks().forEach(track => track.stop())

            recognition.start()
            setIsRecording(true)
            console.log('[useVoiceInput] >>> start() called, language:', language)
          })
          .catch((err) => {
            console.error('[useVoiceInput] >>> FAIL: Microphone access denied:', err.name, err.message)
            const errorMsg = 'Microphone permission denied. Please allow microphone access in your browser.'
            if (onErrorRef.current) {
              onErrorRef.current(errorMsg)
            }
          })
      } catch (error) {
        console.error('[useVoiceInput] >>> FAIL: Failed to start recording:', error)
        if (onErrorRef.current) {
          onErrorRef.current('Failed to start recording. Please try again.')
        }
      }
    } else {
      console.error('[useVoiceInput] >>> FAIL: Recognition instance is null - this should never happen!')
      if (onErrorRef.current) {
        onErrorRef.current('Speech recognition not initialized. Please refresh the page.')
      }
    }
  }, [isSupported, isRecording, language])

  const stopRecording = useCallback(() => {
    console.log('[useVoiceInput] >>> STOP CLICK: stopRecording called, isRecording:', isRecording)
    const recognition = recognitionRef.current
    console.log('[useVoiceInput] Recognition instance:', recognition ? 'EXISTS' : 'NULL')

    if (recognition && isRecording) {
      try {
        console.log('[useVoiceInput] >>> Calling recognition.stop()')
        recognition.stop()
        setIsRecording(false)
        console.log('[useVoiceInput] >>> stop() completed')
      } catch (error) {
        console.error('[useVoiceInput] >>> ERROR stopping recognition:', error)
        setIsRecording(false)
      }
    } else {
      console.log('[useVoiceInput] >>> STOP ignored - not recording or recognition is null')
      setIsRecording(false)
    }
  }, [isRecording])

  const resetTranscript = useCallback(() => {
    setTranscript('')
  }, [])

  return {
    transcript,
    isRecording,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  }
}

export default useVoiceInput
