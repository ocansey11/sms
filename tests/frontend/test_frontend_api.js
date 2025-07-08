const axios = require('axios');

async function testLogin() {
  try {
    const response = await axios.post('http://localhost:8000/api/auth/login', {
      email: 'teacher@schoolsms.com',
      password: 'teacher123'
    });
    console.log('Login successful:', response.data);
  } catch (error) {
    console.error('Login failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
  }
}

testLogin();
