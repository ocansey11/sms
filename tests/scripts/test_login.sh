#!/bin/bash
curl -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/json" -d '{"email": "teacher@schoolsms.com", "password": "teacher123"}'
