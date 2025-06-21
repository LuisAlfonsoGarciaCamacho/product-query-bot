import React from 'react'
import { Users } from 'lucide-react'

function UserSelector({ currentUser, onUserChange }) {
  const users = ['user1', 'user2', 'user3']

  return (
    <div className="user-selector">
      <Users size={16} />
      <select 
        value={currentUser} 
        onChange={(e) => onUserChange(e.target.value)}
      >
        {users.map(user => (
          <option key={user} value={user}>
            Usuario {user.charAt(4)}
          </option>
        ))}
      </select>
    </div>
  )
}

export default UserSelector