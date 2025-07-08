const fetch = require('node-fetch');

async function testConnection() {
  try {
    console.log('Testing connection to backend...');
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();
    console.log('Backend health check:', data);
    
    console.log('Testing login endpoint...');
    const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'teacher@schoolsms.com',
        password: 'teacher123'
      })
    });
    
    const loginData = await loginResponse.json();
    console.log('Login response:', loginData);
    
  } catch (error) {
    console.error('Network error:', error);
  }
}

testConnection();
