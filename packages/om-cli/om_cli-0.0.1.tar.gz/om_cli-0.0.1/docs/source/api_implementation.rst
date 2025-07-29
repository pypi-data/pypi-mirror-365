API Implementation
==================

Comprehensive REST API implementation for the om mental health platform, enabling external integrations, mobile apps, web interfaces, and third-party applications while maintaining privacy and security.

🏗️ Architecture
---------------

Core Components
~~~~~~~~~~~~~~

1. **API Server** (``api/server.py``) - Flask-based REST API server
2. **Python Client** (``api/client.py``) - Python client library
3. **JavaScript Client** (``api/client.js``) - Web/Node.js client library
4. **Web Dashboard** (``api/web_dashboard.html``) - Example web interface
5. **CLI Integration** (``modules/api_server.py``) - om CLI integration

Security Model
~~~~~~~~~~~~~

- **API Key Authentication** - Secure key-based access control
- **Permission System** - Read/write permissions per key
- **Rate Limiting** - Configurable request limits
- **Local Data Only** - No external data transmission
- **CORS Support** - Configurable for web applications

📡 API Endpoints
---------------

System Endpoints
~~~~~~~~~~~~~~~

Health Check
^^^^^^^^^^^^

.. code-block:: http

   GET /health
   
   Response:
   {
     "status": "healthy",
     "version": "0.0.1",
     "uptime": 3600
   }

API Information
^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/info
   Authorization: Bearer <api_key>
   
   Response:
   {
     "version": "0.0.1",
     "endpoints": [...],
     "capabilities": ["mood_tracking", "wellness_dashboard", "ai_coaching"],
     "rate_limits": {
       "requests_per_minute": 60,
       "requests_per_hour": 1000
     }
   }

Mood Tracking Endpoints
~~~~~~~~~~~~~~~~~~~~~~

Retrieve Mood Entries
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/mood?limit=10&offset=0&start_date=2025-01-01&end_date=2025-01-31
   Authorization: Bearer <api_key>
   
   Response:
   {
     "entries": [
       {
         "id": "mood_123",
         "mood": "happy",
         "intensity": 8,
         "date": "2025-01-15",
         "notes": "Great day at work",
         "energy_level": 7,
         "stress_level": 3,
         "created_at": "2025-01-15T10:30:00Z"
       }
     ],
     "total": 45,
     "has_more": true
   }

Add Mood Entry
^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/mood
   Authorization: Bearer <api_key>
   Content-Type: application/json
   
   {
     "mood": "calm",
     "intensity": 7,
     "notes": "Meditation helped today",
     "energy_level": 6,
     "stress_level": 4,
     "triggers": ["work", "traffic"]
   }
   
   Response:
   {
     "id": "mood_124",
     "status": "created",
     "message": "Mood entry added successfully"
   }

Mood Analytics
^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/mood/analytics?period=30d&group_by=day
   Authorization: Bearer <api_key>
   
   Response:
   {
     "period": "30d",
     "summary": {
       "avg_mood": 6.8,
       "avg_energy": 6.2,
       "avg_stress": 4.1,
       "total_entries": 28
     },
     "trends": [
       {
         "date": "2025-01-01",
         "avg_mood": 7.0,
         "avg_energy": 6.5,
         "avg_stress": 3.8
       }
     ],
     "patterns": {
       "best_day": "Sunday",
       "worst_day": "Monday",
       "common_triggers": ["work", "sleep", "weather"]
     }
   }

Mood Suggestions
^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/mood/suggestions?current_mood=anxious&intensity=7
   Authorization: Bearer <api_key>
   
   Response:
   {
     "suggestions": [
       {
         "type": "breathing",
         "title": "4-7-8 Breathing Exercise",
         "description": "Calm anxiety with controlled breathing",
         "duration": 5,
         "effectiveness": 8.2
       },
       {
         "type": "grounding",
         "title": "5-4-3-2-1 Technique",
         "description": "Ground yourself in the present moment",
         "duration": 3,
         "effectiveness": 7.8
       }
     ]
   }

Daily Check-in Endpoints
~~~~~~~~~~~~~~~~~~~~~~~

Retrieve Check-ins
^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/checkin?limit=7
   Authorization: Bearer <api_key>
   
   Response:
   {
     "checkins": [
       {
         "id": "checkin_456",
         "date": "2025-01-15",
         "type": "daily",
         "mood": "good",
         "energy_level": 7,
         "sleep_quality": "good",
         "sleep_hours": 7.5,
         "going_well": "Work project progress",
         "challenges": "Time management",
         "gratitude": "Supportive team",
         "created_at": "2025-01-15T09:00:00Z"
       }
     ]
   }

Add Check-in Entry
^^^^^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/checkin
   Authorization: Bearer <api_key>
   Content-Type: application/json
   
   {
     "type": "morning",
     "mood": "optimistic",
     "energy_level": 8,
     "sleep_quality": "excellent",
     "sleep_hours": 8.0,
     "goals": "Complete project milestone",
     "gratitude": "Beautiful sunrise"
   }
   
   Response:
   {
     "id": "checkin_457",
     "status": "created",
     "message": "Check-in recorded successfully"
   }

Wellness Dashboard Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Full Dashboard Data
^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/dashboard?period=7d
   Authorization: Bearer <api_key>
   
   Response:
   {
     "period": "7d",
     "summary": {
       "wellness_score": 7.2,
       "mood_trend": "improving",
       "activity_count": 15,
       "streak_days": 5
     },
     "metrics": {
       "mood": {
         "average": 6.8,
         "trend": "up",
         "data_points": 7
       },
       "energy": {
         "average": 6.5,
         "trend": "stable",
         "data_points": 7
       },
       "activities": {
         "breathing": 5,
         "meditation": 3,
         "gratitude": 7,
         "physical": 2
       }
     },
     "achievements": {
       "recent": ["7-day-streak", "gratitude-week"],
       "progress": {
         "level": 5,
         "points": 2150,
         "next_level": 2500
       }
     }
   }

Dashboard Summary
^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/dashboard/summary
   Authorization: Bearer <api_key>
   
   Response:
   {
     "wellness_score": 7.2,
     "current_streak": 5,
     "today_activities": 3,
     "mood_status": "good",
     "energy_level": 7,
     "quick_insights": [
       "Your mood has improved 15% this week",
       "Breathing exercises are most effective for you",
       "Consider adding more physical activities"
     ]
   }

Quick Actions Endpoints
~~~~~~~~~~~~~~~~~~~~~~

Quick Mood Logging
^^^^^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/quick/mood
   Authorization: Bearer <api_key>
   Content-Type: application/json
   
   {
     "mood": "happy",
     "intensity": 8,
     "context": "quick_check"
   }
   
   Response:
   {
     "status": "logged",
     "suggestions": [
       "Great mood! Consider sharing gratitude.",
       "Keep up the positive energy with a quick walk."
     ]
   }

Quick Gratitude Entry
^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   POST /api/quick/gratitude
   Authorization: Bearer <api_key>
   Content-Type: application/json
   
   {
     "gratitude": "Sunny weather today",
     "category": "nature"
   }
   
   Response:
   {
     "status": "recorded",
     "streak_updated": true,
     "current_streak": 6
   }

AI Coaching Endpoints
~~~~~~~~~~~~~~~~~~~~

Daily Coaching Insights
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/coach/daily
   Authorization: Bearer <api_key>
   
   Response:
   {
     "insights": [
       {
         "type": "pattern",
         "title": "Mood Pattern Detected",
         "content": "Your mood tends to improve after breathing exercises",
         "priority": "medium",
         "action": "Try a breathing session when feeling low"
       }
     ],
     "recommendations": [
       {
         "activity": "gratitude",
         "reason": "You haven't practiced gratitude in 2 days",
         "expected_benefit": "mood_boost"
       }
     ]
   }

Pattern Analysis
^^^^^^^^^^^^^^^^

.. code-block:: http

   GET /api/coach/analyze?period=30d
   Authorization: Bearer <api_key>
   
   Response:
   {
     "patterns": {
       "mood_triggers": [
         {"trigger": "work_stress", "impact": -1.2, "frequency": 8},
         {"trigger": "exercise", "impact": +1.8, "frequency": 12}
       ],
       "effective_activities": [
         {"activity": "breathing", "effectiveness": 8.2},
         {"activity": "gratitude", "effectiveness": 7.6}
       ],
       "time_patterns": {
         "best_time": "morning",
         "challenging_time": "evening"
       }
     },
     "insights": [
       "Exercise has the strongest positive impact on your mood",
       "Work stress is your most common mood trigger",
       "Morning activities are most effective for you"
     ]
   }

Backup and Data Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~

Create Backup
^^^^^^^^^^^^^

.. code-block:: http

   POST /api/backup
   Authorization: Bearer <api_key>
   Content-Type: application/json
   
   {
     "include_tables": ["mood_entries", "wellness_sessions", "habits"],
     "format": "json",
     "compress": true
   }
   
   Response:
   {
     "backup_id": "backup_789",
     "filename": "om_backup_20250115.json.gz",
     "size_bytes": 15420,
     "created_at": "2025-01-15T14:30:00Z"
   }

List Backups
^^^^^^^^^^^^

.. code-block:: http

   GET /api/backup/list
   Authorization: Bearer <api_key>
   
   Response:
   {
     "backups": [
       {
         "id": "backup_789",
         "filename": "om_backup_20250115.json.gz",
         "size_bytes": 15420,
         "created_at": "2025-01-15T14:30:00Z"
       }
     ]
   }

🔐 Authentication System
-----------------------

API Key Management
~~~~~~~~~~~~~~~~~

**Generate API Key**:

.. code-block:: bash

   om api generate-key --name "Mobile App" --permissions read,write
   
   Output:
   API Key: om_ak_1234567890abcdef
   Permissions: read, write
   Created: 2025-01-15T10:00:00Z

**List API Keys**:

.. code-block:: bash

   om api list-keys
   
   Output:
   Active API Keys:
   - Mobile App (om_ak_1234567890abcdef) - read,write - Created: 2025-01-15
   - Web Dashboard (om_ak_fedcba0987654321) - read - Created: 2025-01-10

**Revoke API Key**:

.. code-block:: bash

   om api revoke-key om_ak_1234567890abcdef

Permission System
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Permission
     - Description
   * - ``read``
     - Read access to mood data, wellness sessions, achievements
   * - ``write``
     - Create new entries, update existing data
   * - ``admin``
     - Full access including backup, configuration, key management
   * - ``analytics``
     - Access to analytics and pattern analysis endpoints
   * - ``coaching``
     - Access to AI coaching insights and recommendations

Rate Limiting
~~~~~~~~~~~~

.. code-block:: python

   # Rate limits per API key
   RATE_LIMITS = {
       'requests_per_minute': 60,
       'requests_per_hour': 1000,
       'requests_per_day': 10000
   }
   
   # Rate limit headers in response
   X-RateLimit-Limit: 60
   X-RateLimit-Remaining: 45
   X-RateLimit-Reset: 1642248000

🖥️ Client Libraries
------------------

Python Client
~~~~~~~~~~~~~

.. code-block:: python

   from om_api_client import OmClient
   
   # Initialize client
   client = OmClient(
       base_url='http://localhost:8080',
       api_key='om_ak_1234567890abcdef'
   )
   
   # Add mood entry
   mood_entry = client.mood.add(
       mood='happy',
       intensity=8,
       notes='Great day!'
   )
   
   # Get mood analytics
   analytics = client.mood.analytics(period='30d')
   
   # Get dashboard data
   dashboard = client.dashboard.summary()

JavaScript Client
~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   import { OmClient } from './om-client.js';
   
   // Initialize client
   const client = new OmClient({
     baseUrl: 'http://localhost:8080',
     apiKey: 'om_ak_1234567890abcdef'
   });
   
   // Add mood entry
   const moodEntry = await client.mood.add({
     mood: 'calm',
     intensity: 7,
     notes: 'Meditation helped'
   });
   
   // Get dashboard data
   const dashboard = await client.dashboard.summary();
   
   // Update UI
   updateDashboard(dashboard);

🌐 Web Dashboard Example
-----------------------

HTML Interface
~~~~~~~~~~~~~

.. code-block:: html

   <!DOCTYPE html>
   <html>
   <head>
       <title>Om Wellness Dashboard</title>
       <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
       <link rel="stylesheet" href="dashboard.css">
   </head>
   <body>
       <div id="dashboard">
           <h1>🧘‍♀️ Om Wellness Dashboard</h1>
           
           <div class="metrics">
               <div class="metric-card">
                   <h3>Wellness Score</h3>
                   <div id="wellness-score">7.2</div>
               </div>
               
               <div class="metric-card">
                   <h3>Current Streak</h3>
                   <div id="current-streak">5 days</div>
               </div>
           </div>
           
           <div class="charts">
               <canvas id="mood-chart"></canvas>
               <canvas id="activity-chart"></canvas>
           </div>
           
           <div class="quick-actions">
               <button onclick="quickMood()">Quick Mood</button>
               <button onclick="quickGratitude()">Quick Gratitude</button>
           </div>
       </div>
       
       <script src="dashboard.js"></script>
   </body>
   </html>

JavaScript Dashboard Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   class WellnessDashboard {
       constructor(apiKey) {
           this.client = new OmClient({
               baseUrl: 'http://localhost:8080',
               apiKey: apiKey
           });
           this.init();
       }
       
       async init() {
           await this.loadDashboard();
           this.setupCharts();
           this.startAutoRefresh();
       }
       
       async loadDashboard() {
           try {
               const data = await this.client.dashboard.summary();
               this.updateMetrics(data);
               
               const analytics = await this.client.mood.analytics({
                   period: '7d'
               });
               this.updateCharts(analytics);
               
           } catch (error) {
               console.error('Failed to load dashboard:', error);
           }
       }
       
       updateMetrics(data) {
           document.getElementById('wellness-score').textContent = data.wellness_score;
           document.getElementById('current-streak').textContent = `${data.current_streak} days`;
       }
       
       setupCharts() {
           // Mood trend chart
           this.moodChart = new Chart(
               document.getElementById('mood-chart'),
               {
                   type: 'line',
                   data: {
                       labels: [],
                       datasets: [{
                           label: 'Mood',
                           data: [],
                           borderColor: 'rgb(75, 192, 192)',
                           tension: 0.1
                       }]
                   }
               }
           );
       }
       
       async quickMood() {
           const mood = prompt('How are you feeling? (happy, sad, anxious, calm, etc.)');
           const intensity = prompt('Intensity (1-10):');
           
           if (mood && intensity) {
               await this.client.quick.mood({
                   mood: mood,
                   intensity: parseInt(intensity)
               });
               
               this.loadDashboard(); // Refresh
           }
       }
   }
   
   // Initialize dashboard
   const dashboard = new WellnessDashboard('om_ak_1234567890abcdef');

🚀 Deployment and Configuration
------------------------------

Server Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config.py
   import os
   
   class Config:
       # Server settings
       HOST = os.getenv('OM_API_HOST', 'localhost')
       PORT = int(os.getenv('OM_API_PORT', 8080))
       DEBUG = os.getenv('OM_API_DEBUG', 'False').lower() == 'true'
       
       # Security settings
       SECRET_KEY = os.getenv('OM_API_SECRET_KEY', 'your-secret-key')
       API_KEY_LENGTH = 32
       
       # Rate limiting
       RATE_LIMIT_REQUESTS_PER_MINUTE = 60
       RATE_LIMIT_REQUESTS_PER_HOUR = 1000
       
       # CORS settings
       CORS_ORIGINS = os.getenv('OM_API_CORS_ORIGINS', 'http://localhost:3000').split(',')
       
       # Database
       DATABASE_PATH = os.path.expanduser('~/.om/om.db')

Starting the API Server
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start API server
   om api start --host localhost --port 8080
   
   # Start with custom configuration
   om api start --config /path/to/config.py
   
   # Start in background
   om api start --daemon
   
   # Stop API server
   om api stop

Docker Deployment
~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8080
   
   CMD ["python", "-m", "api.server"]

.. code-block:: bash

   # Build and run with Docker
   docker build -t om-api .
   docker run -p 8080:8080 -v ~/.om:/root/.om om-api

🔧 Development and Testing
-------------------------

API Testing
~~~~~~~~~~

.. code-block:: python

   import pytest
   import requests
   
   class TestOmAPI:
       def setup_method(self):
           self.base_url = 'http://localhost:8080'
           self.api_key = 'test_api_key'
           self.headers = {'Authorization': f'Bearer {self.api_key}'}
       
       def test_health_endpoint(self):
           response = requests.get(f'{self.base_url}/health')
           assert response.status_code == 200
           assert response.json()['status'] == 'healthy'
       
       def test_mood_entry_creation(self):
           data = {
               'mood': 'happy',
               'intensity': 8,
               'notes': 'Test entry'
           }
           response = requests.post(
               f'{self.base_url}/api/mood',
               json=data,
               headers=self.headers
           )
           assert response.status_code == 201
           assert 'id' in response.json()

Load Testing
~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import aiohttp
   import time
   
   async def load_test():
       """Simple load test for API endpoints"""
       async with aiohttp.ClientSession() as session:
           tasks = []
           
           for i in range(100):
               task = session.get(
                   'http://localhost:8080/api/dashboard/summary',
                   headers={'Authorization': 'Bearer test_key'}
               )
               tasks.append(task)
           
           start_time = time.time()
           responses = await asyncio.gather(*tasks)
           end_time = time.time()
           
           print(f"100 requests completed in {end_time - start_time:.2f} seconds")
           print(f"Average response time: {(end_time - start_time) / 100:.3f} seconds")

The API implementation provides a robust, secure, and scalable interface for integrating the om mental health platform with external applications while maintaining the core principles of privacy and local data control.
