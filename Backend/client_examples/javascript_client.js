/**
 * JavaScript/Node.js client example for StudHelper Backend API
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class StudHelperClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.token = null;
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000,
        });
        
        // Add request interceptor for authentication
        this.client.interceptors.request.use((config) => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        });
    }
    
    async register(email, username, password, fullName = null) {
        const response = await this.client.post('/api/v1/auth/register', {
            email,
            username,
            password,
            full_name: fullName
        });
        return response.data;
    }
    
    async login(username, password) {
        const response = await this.client.post('/api/v1/auth/login', {
            username,
            password
        });
        
        this.token = response.data.access_token;
        return response.data;
    }
    
    async getProfile() {
        const response = await this.client.get('/api/v1/auth/me');
        return response.data;
    }
    
    async createClass(name, description = null) {
        const response = await this.client.post('/api/v1/classes/', {
            name,
            description
        });
        return response.data;
    }
    
    async joinClass(classCode) {
        const response = await this.client.post('/api/v1/classes/join', {
            class_code: classCode
        });
        return response.data;
    }
    
    async getClasses() {
        const response = await this.client.get('/api/v1/classes/');
        return response.data;
    }
    
    async createChatSession(classId, title) {
        const response = await this.client.post('/api/v1/chat/sessions', {
            class_id: classId,
            title
        });
        return response.data;
    }
    
    async sendMessage(sessionId, content) {
        const response = await this.client.post(`/api/v1/chat/sessions/${sessionId}/messages`, {
            content
        });
        return response.data;
    }
    
    async uploadClassDocument(classId, filePath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        
        const response = await this.client.post(
            `/api/v1/documents/classes/${classId}/upload`,
            form,
            {
                headers: {
                    ...form.getHeaders()
                }
            }
        );
        return response.data;
    }
    
    async getUsageStats() {
        const response = await this.client.get('/api/v1/usage/my-usage');
        return response.data;
    }
}

// Example usage
async function example() {
    const client = new StudHelperClient();
    
    try {
        // Register and login
        try {
            const user = await client.register(
                'test@example.com',
                'testuser',
                'testpass123',
                'Test User'
            );
            console.log('User registered:', user.username);
        } catch (error) {
            console.log('User might already exist, trying to login...');
        }
        
        // Login
        const loginResult = await client.login('testuser', 'testpass123');
        console.log('Logged in as:', loginResult.user.username);
        
        // Create a class
        const newClass = await client.createClass('Test Class', 'A test class for the API');
        console.log('Created class:', newClass.name, 'Code:', newClass.class_code);
        
        // Create chat session
        const session = await client.createChatSession(newClass.id, 'Test Chat');
        console.log('Created chat session:', session.title);
        
        // Send a message
        const chatResponse = await client.sendMessage(session.id, 'Hello, can you help me with physics?');
        console.log('AI Response:', chatResponse.ai_response.content);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

module.exports = StudHelperClient;

// Run example if this file is executed directly
if (require.main === module) {
    example();
}

