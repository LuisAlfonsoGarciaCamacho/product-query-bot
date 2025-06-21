const WEBHOOK_BASE_URL = `http://localhost:${import.meta.env.VITE_WEBHOOK_PORT || 3001}`

export const setupWebhook = (onMessage) => {
  let pollCount = 0
  
  const pollInterval = setInterval(async () => {
    try {
      const users = ['user1', 'user2', 'user3']
      
      for (const userId of users) {
        const response = await fetch(`${WEBHOOK_BASE_URL}/poll/${userId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(5000)
        })
        
        if (!response.ok) {
          console.error(`❌ Poll failed for ${userId}: ${response.status}`)
          continue
        }
        
        const data = await response.json()
        
        if (data.status !== 'no_messages' && data.answer) {
          console.log(`✅ Got message for ${userId}`)
          onMessage({
            user_id: data.user_id,
            answer: data.answer,
            timestamp: data.timestamp
          })
        }
      }
      
      pollCount++
      
    } catch (error) {
      console.error('❌ Polling error:', error)
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        console.log('⏰ Poll timeout, continuing...')
      }
    }
  }, 2000)

  return () => {
    console.log('🛑 Stopping webhook polling')
    clearInterval(pollInterval)
  }
}