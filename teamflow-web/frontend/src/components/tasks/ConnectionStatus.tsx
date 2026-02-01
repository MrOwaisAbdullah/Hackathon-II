/**
 * T123: Connection Status Indicator
 *
 * Displays WebSocket connection status with animated indicators.
 */

import { motion, AnimatePresence } from "framer-motion"
import { Wifi, WifiOff, Loader2 } from "lucide-react"
import { ConnectionState } from "@/services/websocket"

interface ConnectionStatusProps {
  state: ConnectionState
  reconnectingIn?: number | null
}

export function ConnectionStatus({ state, reconnectingIn }: ConnectionStatusProps) {
  const getStatusConfig = () => {
    switch (state) {
      case 'connected':
        return {
          icon: Wifi,
          text: 'Live',
          bgColor: 'bg-emerald-500/10 dark:bg-emerald-500/20',
          textColor: 'text-emerald-600 dark:text-emerald-400',
          dotColor: 'bg-emerald-500',
        }
      case 'connecting':
        return {
          icon: Loader2,
          text: 'Connecting...',
          bgColor: 'bg-blue-500/10 dark:bg-blue-500/20',
          textColor: 'text-blue-600 dark:text-blue-400',
          dotColor: 'bg-blue-500',
          animate: true,
        }
      case 'error':
      case 'disconnected':
        return {
          icon: WifiOff,
          text: 'Offline',
          bgColor: 'bg-rose-500/10 dark:bg-rose-500/20',
          textColor: 'text-rose-600 dark:text-rose-400',
          dotColor: 'bg-rose-500',
        }
      default:
        return {
          icon: WifiOff,
          text: 'Unknown',
          bgColor: 'bg-gray-500/10 dark:bg-gray-500/20',
          textColor: 'text-gray-600 dark:text-gray-400',
          dotColor: 'bg-gray-500',
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={state}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.2 }}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor}`}
      >
        <div className="flex items-center gap-1.5">
          <Icon className={`w-3.5 h-3.5 ${config.animate ? 'animate-spin' : ''}`} />
          <span>{config.text}</span>
        </div>
        {state === 'connected' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`w-2 h-2 rounded-full ${config.dotColor}`}
          />
        )}
        {state === 'connecting' && (
          <motion.div
            className={`w-2 h-2 rounded-full ${config.dotColor}`}
            animate={{
              scale: [1, 1.5, 1],
              opacity: [1, 0.5, 1],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
            }}
          />
        )}
        {state === 'disconnected' && reconnectingIn && (
          <span className="text-xs opacity-75">
            Reconnecting in {Math.ceil(reconnectingIn / 1000)}s
          </span>
        )}
      </motion.div>
    </AnimatePresence>
  )
}
