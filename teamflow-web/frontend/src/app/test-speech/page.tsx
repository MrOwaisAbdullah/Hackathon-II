'use client';

/**
 * Simple Speech Recognition Test Page
 * Tests if Web Speech API works without any other dependencies
 */

import { useState } from 'react';

export default function TestSpeechPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
    console.log('[TestSpeech]', message);
  };

  const startRecording = () => {
    setError('');
    setTranscript('');
    setLogs([]);

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      const errorMsg = 'Speech Recognition not supported in this browser';
      setError(errorMsg);
      addLog(`ERROR: ${errorMsg}`);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      addLog('✅ Recognition started');
      setIsRecording(true);
    };

    recognition.onresult = (event: any) => {
      addLog(`✅ Result received: ${event.results.length} results`);
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        addLog(`   Result ${i}: &quot;${transcript}&quot; (isFinal: ${result.isFinal})`);

        if (result.isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      setTranscript(finalTranscript || interimTranscript);
    };

    recognition.onerror = (event: any) => {
      addLog(`❌ Error: ${event.error} - ${event.message || 'No message'}`);
      setError(`Error: ${event.error} - ${event.message || 'See browser console'}`);
      setIsRecording(false);
    };

    recognition.onend = () => {
      addLog('🏁 Recognition ended');
      setIsRecording(false);
    };

    addLog('🎤 Starting recognition...');
    recognition.start();
  };

  return (
    <div className=&quot;min-h-screen bg-gray-50 p-8&quot;>
      <div className=&quot;max-w-2xl mx-auto&quot;>
        <h1 className=&quot;text-3xl font-bold mb-4&quot;>Web Speech API Test</h1>
        <p className=&quot;text-gray-600 mb-6&quot;>
          This page tests if the Web Speech API works in your browser.
        </p>

        {/* Test Button */}
        <button
          onClick={startRecording}
          disabled={isRecording}
          className={`px-6 py-3 rounded-lg font-medium ${
            isRecording
              ? 'bg-red-500 text-white animate-pulse'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {isRecording ? '🔴 Recording... Click to stop' : '🎤 Start Recording'}
        </button>

        {/* Transcript Display */}
        {transcript && (
          <div className=&quot;mt-6 p-4 bg-white rounded-lg border border-gray-200&quot;>
            <h2 className=&quot;font-semibold mb-2&quot;>Transcript:</h2>
            <p className=&quot;text-lg&quot;>{transcript}</p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className=&quot;mt-6 p-4 bg-red-50 rounded-lg border border-red-200&quot;>
            <h2 className=&quot;font-semibold text-red-800 mb-2&quot;>Error:</h2>
            <p className=&quot;text-red-700&quot;>{error}</p>
          </div>
        )}

        {/* Logs */}
        {logs.length > 0 && (
          <div className=&quot;mt-6 p-4 bg-white rounded-lg border border-gray-200&quot;>
            <h2 className=&quot;font-semibold mb-2&quot;>Event Log:</h2>
            <div className=&quot;font-mono text-sm space-y-1 max-h-64 overflow-y-auto&quot;>
              {logs.map((log, i) => (
                <div key={i} className={log.includes('❌') ? 'text-red-600' : log.includes('✅') ? 'text-green-600' : 'text-gray-700'}>
                  {log}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className=&quot;mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200&quot;>
          <h2 className=&quot;font-semibold text-blue-900 mb-2&quot;>If you get a &quot;network&quot; error:</h2>
          <ul className=&quot;list-disc list-inside text-blue-800 space-y-1 text-sm&quot;>
            <li>Check your internet connection</li>
            <li>Try opening chrome://flags/#enable-speech-api and enable it</li>
            <li>Try in Incognito mode (Ctrl+Shift+N)</li>
            <li>Disable VPN or proxy if enabled</li>
            <li>Make sure firewall allows Chrome to access Google servers</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
