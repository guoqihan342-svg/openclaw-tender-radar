// Vercel Serverless Function - 订阅处理 (JSON存储)
const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '..', 'data', 'subscribers.json');

module.exports = async (req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, name } = req.body;
  
  if (!email) {
    return res.status(400).json({ error: 'Email is required' });
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }

  try {
    // 读取现有数据
    let subscribers = [];
    if (fs.existsSync(DATA_FILE)) {
      const data = fs.readFileSync(DATA_FILE, 'utf8');
      subscribers = JSON.parse(data);
    }
    
    // 检查是否已存在
    const existing = subscribers.find(s => s.email === email);
    if (existing) {
      return res.status(200).json({ 
        success: true, 
        message: 'Already subscribed!',
        email: email
      });
    }
    
    // 添加新订阅
    const newSubscriber = {
      id: Date.now(),
      email,
      name: name || '',
      plan: 'free',
      status: 'trial',
      created_at: new Date().toISOString()
    };
    subscribers.push(newSubscriber);
    
    // 保存
    fs.writeFileSync(DATA_FILE, JSON.stringify(subscribers, null, 2));
    
    return res.status(200).json({ 
      success: true, 
      message: 'Subscription successful!',
      id: newSubscriber.id
    });
    
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
