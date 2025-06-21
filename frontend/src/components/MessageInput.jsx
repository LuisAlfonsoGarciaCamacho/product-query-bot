import React, { useState } from 'react'
import { Send, AlertCircle } from 'lucide-react'
import { sendMessage } from '../services/api'

function MessageInput({ currentUser, onAddMessage, disabled }) {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading || disabled) return

    const message = {
      id: Date.now(),
      text: input.trim(),
      sender: 'user',
      timestamp: new Date()
    }

    onAddMessage(message)
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      await sendMessage(currentUser, message.text)
    } catch (error) {
      console.error('❌ Error sending message:', error)
      setError('Error al enviar mensaje')
      
      onAddMessage({
        id: Date.now() + 1,
        text: 'Error, try again.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="message-input-container">
      {error && (
        <div className="error-banner">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
      <form className="message-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={disabled ? "Connecting..." : "Type your message..."}
          disabled={isLoading || disabled}
        />
        <button 
          type="submit" 
          disabled={!input.trim() || isLoading || disabled}
          className="send-button"
        >
          {isLoading ? (
            <div className="loading-spinner"></div>
          ) : (
            <Send size={20} />
          )}
        </button>
      </form>
    </div>
  )
}

export default MessageInput