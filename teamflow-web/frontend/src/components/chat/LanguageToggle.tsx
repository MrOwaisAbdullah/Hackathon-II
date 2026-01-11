'use client'

/**
 * Language Toggle Component (T074)
 *
 * Dropdown to switch between English (en) and Urdu (ur).
 * Updates user preference via /api/v1/chat/preferences endpoint.
 *
 * Usage:
 *   <LanguageToggle apiUrl="http://localhost:8000" />
 */

import { useState, useEffect } from 'react'

interface LanguageToggleProps {
  apiUrl?: string
  onLanguageChange?: (language: 'en' | 'ur') => void
}

type Language = 'en' | 'ur'

const LANGUAGE_OPTIONS: { value: Language; label: string; flag: string }[] = [
  { value: 'en', label: 'English', flag: '🇬🇧' },
  { value: 'ur', label: 'اردو (Urdu)', flag: '🇵🇰' },
]

export function LanguageToggle({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  onLanguageChange,
}: LanguageToggleProps) {
  const [currentLanguage, setCurrentLanguage] = useState<Language>('en')
  const [isOpen, setIsOpen] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)

  // Load current language preference on mount
  useEffect(() => {
    async function loadPreference() {
      try {
        const response = await fetch(`${apiUrl}/api/v1/chat/preferences`, {
          headers: {
            'Content-Type': 'application/json',
            // Note: In production, include session token
          },
        })

        if (response.ok) {
          const data = await response.json()
          setCurrentLanguage(data.language || 'en')
          if (onLanguageChange) {
            onLanguageChange(data.language || 'en')
          }
        }
      } catch {
        console.error('[LanguageToggle] Failed to load preference:', error)
      }
    }

    loadPreference()
  }, [apiUrl, onLanguageChange])

  const handleLanguageChange = async (newLanguage: Language) => {
    setIsUpdating(true)
    setIsOpen(false)

    try {
      const response = await fetch(`${apiUrl}/api/v1/chat/preferences`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          // Note: In production, include session token
        },
        body: JSON.stringify({
          language: newLanguage,
          voice_enabled: false, // Preserve existing voice setting or set to false
        }),
      })

      if (response.ok) {
        setCurrentLanguage(newLanguage)
        if (onLanguageChange) {
          onLanguageChange(newLanguage)
        }
        console.log(`[LanguageToggle] Language changed to ${newLanguage}`)
      } else {
        console.error('[LanguageToggle] Failed to update preference:', await response.text())
      }
    } catch {
      console.error('[LanguageToggle] Error updating preference:', error)
    } finally {
      setIsUpdating(false)
    }
  }

  const selectedOption = LANGUAGE_OPTIONS.find(opt => opt.value === currentLanguage) || LANGUAGE_OPTIONS[0]

  return (
    <div className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={isUpdating}
        className="inline-flex items-center space-x-2 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Select language"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="text-lg" role="img" aria-label={selectedOption.label}>
          {selectedOption.flag}
        </span>
        <span>{selectedOption.label}</span>
        <svg
          className="h-5 w-5 text-gray-400"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <ul
            className="absolute right-0 z-20 mt-2 max-h-60 w-48 origin-top-right overflow-auto rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
            role="listbox"
            aria-activedescendant={currentLanguage}
          >
            {LANGUAGE_OPTIONS.map((option) => (
              <li
                key={option.value}
                onClick={() => handleLanguageChange(option.value)}
                className={`relative cursor-pointer select-none py-2 pl-3 pr-9 text-gray-900 hover:bg-gray-100 ${
                  option.value === currentLanguage ? 'bg-gray-100 font-semibold' : ''
                }`}
                role="option"
                aria-selected={option.value === currentLanguage}
              >
                <div className="flex items-center">
                  <span className="mr-3 text-lg" role="img" aria-label={option.label}>
                    {option.flag}
                  </span>
                  <span className="block truncate">{option.label}</span>
                </div>
                {option.value === currentLanguage && (
                  <span className="absolute inset-y-0 right-0 flex items-center pr-4 text-blue-600">
                    <svg
                      className="h-5 w-5"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

export default LanguageToggle
