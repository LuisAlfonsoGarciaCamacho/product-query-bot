import React, { useState, useEffect } from 'react'
import Chat from './components/Chat'
import UserSelector from './components/UserSelector'
import { setupWebhook } from './services/webhook'
import { getHealth } from './services/api'
import './App.css'

function App() {
  const [currentUser, setCurrentUser] = useState('user1')
  const [conversations, setConversations] = useState({
    user1: [],
    user2: [],
    user3: []
  })
  const [connectionStatus, setConnectionStatus] = useState('connecting')

  useEffect(() => {
    const checkConnection = async () => {
      try {
        await getHealth()
        setConnectionStatus('connected')
      } catch (error) {
        console.error('Connection failed:', error)
        setConnectionStatus('error')
      }
    }

    checkConnection()

    const cleanup = setupWebhook((response) => {
      console.log('📥 Received webhook response:', response)
      
      const { user_id, answer } = response
      if (user_id && answer) {
        setConversations(prev => ({
          ...prev,
          [user_id]: [
            ...prev[user_id],
            {
              id: Date.now(),
              text: answer,
              sender: 'bot',
              timestamp: new Date()
            }
          ]
        }))
      }
    })

    return cleanup
  }, [])

  const addMessage = (message) => {
    setConversations(prev => ({
      ...prev,
      [currentUser]: [...prev[currentUser], message]
    }))
  }

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#25d366'
      case 'connecting': return '#ffa500'
      case 'error': return '#ff4444'
      default: return '#999'
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected'
      case 'connecting': return 'Connecting...'
      case 'error': return 'Connection error'
      default: return 'Desconocido'
    }
  }

  return (
    <div className="app">
      <div className="app-container">
        <div className="header">
          <div className="header-left">
            <h1>🤖 RAG Chatbot</h1>
            <div className="connection-status">
              <div 
                className="status-indicator"
                style={{ backgroundColor: getStatusColor() }}
              ></div>
              <span className="status-text">{getStatusText()}</span>
            </div>
          </div>
          <UserSelector 
            currentUser={currentUser}
            onUserChange={setCurrentUser}
          />
        </div>
        
        <Chat 
          currentUser={currentUser}
          messages={conversations[currentUser]}
          onAddMessage={addMessage}
          connectionStatus={connectionStatus}
        />
      </div>
    </div>
  )
}

export default App