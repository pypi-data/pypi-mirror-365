/**
 * om Mental Health Platform API Client (JavaScript/Node.js)
 * Client library for interacting with om API from web applications
 */

class OMAPIClient {
    constructor(baseUrl = 'http://localhost:5000', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
        
        // Check if we're in Node.js or browser environment
        this.isNode = typeof window === 'undefined';
        
        if (this.isNode) {
            // Node.js environment
            try {
                this.fetch = require('node-fetch');
            } catch (e) {
                console.warn('⚠️  node-fetch not available. Install with: npm install node-fetch');
                this.fetch = null;
            }
        } else {
            // Browser environment
            this.fetch = window.fetch.bind(window);
        }
    }

    /**
     * Make HTTP request to API
     */
    async _makeRequest(method, endpoint, data = null, params = null) {
        if (!this.fetch) {
            throw new Error('Fetch not available. Install node-fetch for Node.js');
        }

        let url = `${this.baseUrl}${endpoint}`;
        
        // Add query parameters
        if (params) {
            const searchParams = new URLSearchParams(params);
            url += `?${searchParams}`;
        }

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Add API key
        if (this.apiKey) {
            options.headers['X-API-Key'] = this.apiKey;
        }

        // Add body for POST/PUT requests
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await this.fetch(url, options);
            
            let responseData;
            try {
                responseData = await response.json();
            } catch (e) {
                responseData = {
                    success: false,
                    error: 'Invalid JSON response'
                };
            }

            return {
                success: responseData.success || false,
                data: responseData.data || null,
                message: responseData.message || '',
                error: responseData.error || '',
                timestamp: responseData.timestamp || '',
                statusCode: response.status
            };

        } catch (error) {
            return {
                success: false,
                error: `Request failed: ${error.message}`,
                statusCode: 500
            };
        }
    }

    /**
     * Health check
     */
    async healthCheck() {
        return await this._makeRequest('GET', '/health');
    }

    /**
     * Get API information
     */
    async getApiInfo() {
        return await this._makeRequest('GET', '/api/info');
    }

    // Mood API methods
    
    /**
     * Get mood entries
     */
    async getMoods(limit = 50, days = null) {
        const params = { limit };
        if (days) params.days = days;
        return await this._makeRequest('GET', '/api/mood', null, params);
    }

    /**
     * Add mood entry
     */
    async addMood(mood, options = {}) {
        const data = { mood };
        if (options.notes) data.notes = options.notes;
        if (options.intensity) data.intensity = options.intensity;
        if (options.triggers) data.triggers = options.triggers;
        if (options.location) data.location = options.location;
        
        return await this._makeRequest('POST', '/api/mood', data);
    }

    /**
     * Get mood analytics
     */
    async getMoodAnalytics() {
        return await this._makeRequest('GET', '/api/mood/analytics');
    }

    /**
     * Get mood suggestions
     */
    async getMoodSuggestions(count = 5) {
        return await this._makeRequest('GET', '/api/mood/suggestions', null, { count });
    }

    // Check-in API methods

    /**
     * Get check-in entries
     */
    async getCheckins(limit = 50, days = null) {
        const params = { limit };
        if (days) params.days = days;
        return await this._makeRequest('GET', '/api/checkin', null, params);
    }

    /**
     * Add check-in entry
     */
    async addCheckin(checkinData) {
        return await this._makeRequest('POST', '/api/checkin', checkinData);
    }

    // Dashboard API methods

    /**
     * Get full dashboard data
     */
    async getDashboard() {
        return await this._makeRequest('GET', '/api/dashboard');
    }

    /**
     * Get dashboard summary
     */
    async getDashboardSummary() {
        return await this._makeRequest('GET', '/api/dashboard/summary');
    }

    // Quick actions API methods

    /**
     * Quick mood logging
     */
    async quickMood(mood = null) {
        const data = {};
        if (mood) data.mood = mood;
        return await this._makeRequest('POST', '/api/quick/mood', data);
    }

    /**
     * Quick gratitude entry
     */
    async quickGratitude(content) {
        return await this._makeRequest('POST', '/api/quick/gratitude', { content });
    }

    // Backup API methods

    /**
     * Create backup
     */
    async createBackup(name = null) {
        const data = {};
        if (name) data.name = name;
        return await this._makeRequest('POST', '/api/backup', data);
    }

    /**
     * List available backups
     */
    async listBackups() {
        return await this._makeRequest('GET', '/api/backup/list');
    }
}

/**
 * Helper class with convenience methods
 */
class OMAPIHelper {
    constructor(client) {
        this.client = client;
    }

    /**
     * Log daily mood with error handling
     */
    async logDailyMood(mood, notes = null) {
        try {
            const response = await this.client.addMood(mood, { notes });
            if (response.success) {
                console.log(`✅ Mood logged: ${mood}`);
                return true;
            } else {
                console.error(`❌ Failed to log mood: ${response.error}`);
                return false;
            }
        } catch (error) {
            console.error(`❌ Error logging mood: ${error.message}`);
            return false;
        }
    }

    /**
     * Quick daily check-in
     */
    async quickCheckin(mood, energy, stress, notes = null) {
        const checkinData = {
            type: 'quick_api_checkin',
            mood: mood,
            energy_level: energy,
            stress_level: stress,
            date: new Date().toISOString()
        };

        if (notes) checkinData.notes = notes;

        try {
            const response = await this.client.addCheckin(checkinData);
            if (response.success) {
                console.log(`✅ Check-in completed: ${mood} (Energy: ${energy}, Stress: ${stress})`);
                return true;
            } else {
                console.error(`❌ Check-in failed: ${response.error}`);
                return false;
            }
        } catch (error) {
            console.error(`❌ Error during check-in: ${error.message}`);
            return false;
        }
    }

    /**
     * Get wellness summary with error handling
     */
    async getWellnessSummary() {
        try {
            const response = await this.client.getDashboardSummary();
            if (response.success) {
                return response.data;
            } else {
                console.error(`❌ Failed to get wellness summary: ${response.error}`);
                return {};
            }
        } catch (error) {
            console.error(`❌ Error getting wellness summary: ${error.message}`);
            return {};
        }
    }

    /**
     * Create backup with timestamp
     */
    async backupData() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
        
        try {
            const response = await this.client.createBackup(`api_backup_${timestamp}`);
            if (response.success) {
                const backupName = response.data?.backup_name || 'Unknown';
                console.log(`✅ Backup created: ${backupName}`);
                return true;
            } else {
                console.error(`❌ Backup failed: ${response.error}`);
                return false;
            }
        } catch (error) {
            console.error(`❌ Error creating backup: ${error.message}`);
            return false;
        }
    }

    /**
     * Get mood trends for visualization
     */
    async getMoodTrends(days = 7) {
        try {
            const response = await this.client.getMoods(100, days);
            if (response.success && response.data.entries) {
                const entries = response.data.entries;
                
                // Process entries for trend analysis
                const trends = entries.map(entry => ({
                    date: entry.date,
                    mood: entry.mood,
                    intensity: entry.intensity || 5
                }));

                return trends.reverse(); // Oldest first for charts
            }
            return [];
        } catch (error) {
            console.error(`❌ Error getting mood trends: ${error.message}`);
            return [];
        }
    }
}

/**
 * React Hook for om API (if using React)
 */
function useOMAPI(apiKey, baseUrl = 'http://localhost:5000') {
    if (typeof React === 'undefined') {
        // Not in React environment
        return null;
    }

    const [client] = React.useState(() => new OMAPIClient(baseUrl, apiKey));
    const [helper] = React.useState(() => new OMAPIHelper(client));
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState(null);

    const makeRequest = React.useCallback(async (requestFn) => {
        setIsLoading(true);
        setError(null);
        
        try {
            const result = await requestFn();
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    return {
        client,
        helper,
        isLoading,
        error,
        makeRequest
    };
}

// Example usage
async function exampleUsage() {
    console.log('🧘‍♀️ om API Client Example (JavaScript)');
    console.log('='.repeat(40));

    // Initialize client (replace with your actual API key)
    const apiKey = 'your_api_key_here';
    const client = new OMAPIClient('http://localhost:5000', apiKey);
    const helper = new OMAPIHelper(client);

    try {
        // Health check
        console.log('1. Health check...');
        const health = await client.healthCheck();
        if (health.success) {
            console.log(`   ✅ API server is healthy: ${health.data?.status}`);
        } else {
            console.log(`   ❌ Health check failed: ${health.error}`);
            return;
        }

        // Log mood
        console.log('\n2. Logging mood...');
        await helper.logDailyMood('happy', 'Feeling good today!');

        // Quick check-in
        console.log('\n3. Quick check-in...');
        await helper.quickCheckin('content', 7, 3, 'Good day overall');

        // Get mood analytics
        console.log('\n4. Getting mood analytics...');
        const analytics = await client.getMoodAnalytics();
        if (analytics.success) {
            const totalEntries = analytics.data?.total_entries || 0;
            console.log(`   📊 Total mood entries: ${totalEntries}`);
        }

        // Get wellness summary
        console.log('\n5. Getting wellness summary...');
        const summary = await helper.getWellnessSummary();
        if (summary.overall_wellness) {
            const wellnessScore = summary.overall_wellness.score || 'Unknown';
            console.log(`   🌟 Wellness score: ${wellnessScore}`);
        }

        // Create backup
        console.log('\n6. Creating backup...');
        await helper.backupData();

        console.log('\n✅ Example completed!');

    } catch (error) {
        console.error(`❌ Example failed: ${error.message}`);
    }
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    // Node.js
    module.exports = {
        OMAPIClient,
        OMAPIHelper,
        exampleUsage
    };
} else if (typeof window !== 'undefined') {
    // Browser
    window.OMAPIClient = OMAPIClient;
    window.OMAPIHelper = OMAPIHelper;
    window.useOMAPI = useOMAPI;
}

// Run example if this file is executed directly in Node.js
if (typeof require !== 'undefined' && require.main === module) {
    exampleUsage();
}
