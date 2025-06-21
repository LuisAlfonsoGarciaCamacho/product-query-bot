import express from 'express'
import cors from 'cors'

const app = express()
const PORT = process.env.WEBHOOK_PORT || 3001

app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type']
}))

app.use(express.json())

const responses = new Map()

setInterval(() => {
  const now = Date.now()
  for (const [userId, data] of responses.entries()) {
    if (now - data.received_at > 60000) {
      responses.delete(userId)
      console.log(`🗑️ Auto-cleaned old response for ${userId}`)
    }
  }
}, 30000)

app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    stored_responses: responses.size
  })
})

app.post('/webhook', (req, res) => {
  const { user_id, answer, timestamp } = req.body
  
  console.log(`📨 Webhook received for ${user_id}:`, {
    answer_length: answer?.length || 0,
    timestamp
  })
  
  if (!user_id || !answer) {
    console.log(`⚠️ Invalid webhook data`)
    return res.status(400).json({ 
      error: 'Missing required fields: user_id, answer'
    })
  }
  
  responses.set(user_id, {
    user_id,
    answer,
    timestamp: timestamp || new Date().toISOString(),
    received_at: Date.now()
  })
  
  console.log(`💾 Stored response for ${user_id}. Total stored: ${responses.size}`)
  
  res.json({ status: 'received', timestamp: new Date().toISOString() })
})

app.get('/poll/:userId', (req, res) => {
  const userId = req.params.userId
  const response = responses.get(userId)
  
  if (response) {
    console.log(`📤 Delivering response to ${userId}`)
    responses.delete(userId)
    res.json(response)
  } else {
    res.json({ status: 'no_messages' })
  }
})

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🎣 Webhook server running on http://localhost:${PORT}`)
  console.log(`📡 Webhook URL: http://localhost:${PORT}/webhook`)
})