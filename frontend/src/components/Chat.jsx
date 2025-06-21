import React from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

function Chat({ currentUser, messages, onAddMessage, connectionStatus }) {
  return (
    <div className="chat">
      <div className="chat-header">
        <div className="chat-info">
          <div className="avatar">{currentUser.charAt(4)}</div>
          <div>
            <h3>Usuario {currentUser.charAt(4)}</h3>
            <span className="status">
              {connectionStatus === 'connected' ? 'Online' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
      
      <MessageList messages={messages} />
      
      <MessageInput 
        currentUser={currentUser}
        onAddMessage={onAddMessage}
        disabled={connectionStatus !== 'connected'}
      />
    </div>
  )
}

export default Chat