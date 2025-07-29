Mental Health Articles Library
==============================

The om platform includes a comprehensive mental health articles library that stores curated resources from the awesome-mental-health repository and allows you to manage your own reading collection.

🎯 Overview
-----------

The mental health articles module provides:

- **Curated Content**: Articles from the awesome-mental-health GitHub repository
- **Personal Library**: Add your own articles and resources
- **Reading Progress**: Track what you've read and rate articles
- **Smart Search**: Find articles by title, description, or tags
- **Collections**: Organize articles into themed collections
- **Statistics**: Monitor your reading progress and habits

📚 Getting Started
------------------

Basic Commands
~~~~~~~~~~~~~

.. code-block:: bash

   # View all available commands
   om articles

   # Import curated articles from awesome-mental-health
   om articles import

   # List all articles
   om articles list

   # Search for specific topics
   om articles search burnout

   # View reading statistics
   om articles stats

   # Show article collections
   om articles collections

🔍 Searching and Browsing
-------------------------

List Articles
~~~~~~~~~~~~

.. code-block:: bash

   # List all articles
   om articles list

   # List articles by category
   om articles list articles    # Blog posts and articles
   om articles list books       # Books and longer content
   om articles list apps        # Mental health applications

Search Articles
~~~~~~~~~~~~~~

.. code-block:: bash

   # Search by keyword
   om articles search depression
   om articles search "imposter syndrome"
   om articles search remote work

   # Search results are ranked by relevance
   # Title matches appear first, followed by description matches

Filter Articles
~~~~~~~~~~~~~~

.. code-block:: bash

   # Show only favorite articles
   om articles favorites

   # Show unread articles
   om articles unread

📊 Reading Management
--------------------

Reading Progress
~~~~~~~~~~~~~~~

The system automatically tracks your reading progress:

- **Read Status**: Mark articles as read
- **Favorites**: Star articles you want to reference later
- **Ratings**: Rate articles from 1-10
- **Notes**: Add personal notes to articles
- **Statistics**: View your reading progress and habits

Reading Statistics
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View comprehensive reading statistics
   om articles stats

Example output:

.. code-block:: text

   📊 Reading Statistics
   ==============================
   📚 Total Articles: 16
   ✅ Read: 3
   ⭐ Favorites: 2
   📈 Progress: 18.8%

   📂 By Category:
      Articles: 10
      Apps: 3
      Books: 3

📁 Collections System
--------------------

Pre-built Collections
~~~~~~~~~~~~~~~~~~~~

The system includes several pre-built collections:

- **Getting Started**: Essential articles for understanding mental health in tech
- **Burnout Recovery**: Resources for preventing and recovering from burnout
- **Anxiety Management**: Tools and techniques for managing anxiety
- **Overcoming Imposter Syndrome**: Resources for dealing with imposter syndrome
- **Remote Work Wellness**: Mental health tips for remote workers
- **Mental Health Leadership**: Resources for leaders and managers
- **Crisis Resources**: Emergency and crisis support resources
- **Personal Stories**: First-hand accounts and experiences
- **Research & Studies**: Academic research and studies
- **Daily Wellness**: Resources for daily mental health practices

Viewing Collections
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Show all collections
   om articles collections

   # View articles in a specific collection (future feature)
   om articles collection getting-started

➕ Adding Your Own Content
--------------------------

Add New Articles
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Add a new article interactively
   om articles add https://example.com/mental-health-article

   # You'll be prompted for:
   # - Article title
   # - Author (optional)
   # - Description (optional)

The system will automatically:
- Check for duplicate URLs
- Generate a unique ID
- Set default category and tags
- Add to your personal library

🗄️ Database Schema
------------------

Article Storage
~~~~~~~~~~~~~~

Articles are stored in a comprehensive SQLite database with the following structure:

**mental_health_articles table**:
   - Basic article information (title, URL, author, description)
   - Categorization (category, subcategory, tags)
   - Reading status (is_read, is_favorite, user_rating)
   - Personal notes and timestamps

**article_categories table**:
   - Category definitions and metadata
   - Icons and display information

**article_tags table**:
   - Tag definitions and usage statistics
   - Flexible categorization system

**reading_progress table**:
   - Detailed reading progress tracking
   - Bookmarks and time spent reading

**article_collections table**:
   - Collection definitions and descriptions
   - System and user-created collections

**collection_articles table**:
   - Many-to-many relationship between articles and collections
   - Sort order and organization

🎯 Use Cases
-----------

Daily Learning
~~~~~~~~~~~~~

.. code-block:: bash

   # Morning routine: Check for new articles
   om articles unread

   # Find articles on current challenges
   om articles search anxiety
   om articles search "work from home"

   # Review progress
   om articles stats

Research and Reference
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Build a research collection
   om articles search research
   om articles favorites

   # Find specific topics
   om articles search "imposter syndrome"
   om articles search burnout

Professional Development
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Leadership resources
   om articles search leadership
   om articles search management

   # Team building and culture
   om articles search culture
   om articles search team

Crisis Support
~~~~~~~~~~~~~

.. code-block:: bash

   # Quick access to crisis resources
   om articles search crisis
   om articles search emergency
   om articles search support

🔧 Technical Features
--------------------

Data Import
~~~~~~~~~~

The system can import articles from various sources:

- **awesome-mental-health repository**: Curated list of mental health resources
- **Manual entry**: Add your own articles and resources
- **Future integrations**: RSS feeds, bookmarks, etc.

Search Algorithm
~~~~~~~~~~~~~~~

The search system uses intelligent ranking:

1. **Title matches**: Highest priority
2. **Description matches**: Medium priority  
3. **Tag matches**: Lower priority
4. **Recency**: Recent articles ranked higher
5. **User behavior**: Favorites and ratings influence results

Privacy and Security
~~~~~~~~~~~~~~~~~~~

- **100% Local**: All data stored in local SQLite database
- **No External Calls**: No data sent to external services
- **User Control**: Complete control over your reading data
- **Backup Support**: Easy backup and export capabilities

🚀 Future Enhancements
----------------------

Planned Features
~~~~~~~~~~~~~~~

- **Reading Time Estimation**: Automatic reading time calculation
- **Progress Tracking**: Detailed reading progress within articles
- **Smart Recommendations**: AI-powered article suggestions
- **Collection Management**: Create and manage custom collections
- **Export Options**: Export reading lists and progress
- **Integration**: Connect with other om modules for personalized suggestions
- **Offline Reading**: Download articles for offline access
- **Social Features**: Share reading lists and recommendations

Advanced Analytics
~~~~~~~~~~~~~~~~~

- **Reading Patterns**: Analyze your reading habits and preferences
- **Topic Analysis**: Identify your most-read topics and interests
- **Progress Trends**: Track reading progress over time
- **Effectiveness Tracking**: Measure impact of articles on wellness

Integration with om Ecosystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Mood Correlation**: Suggest articles based on mood patterns
- **Crisis Integration**: Automatic article suggestions during difficult times
- **Coaching Integration**: AI coach recommends relevant articles
- **Habit Integration**: Articles as part of daily wellness routines

📖 Example Workflow
------------------

Setting Up Your Library
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Import curated articles
   om articles import
   
   # 2. Browse available content
   om articles list
   
   # 3. Search for topics of interest
   om articles search "imposter syndrome"
   
   # 4. Check your reading statistics
   om articles stats

Daily Reading Routine
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Morning: Check unread articles
   om articles unread
   
   # Find something relevant to current mood/situation
   om articles search anxiety
   
   # After reading: mark as read and rate
   # (Future feature: om articles read <id> --rating 8)
   
   # Evening: Review progress
   om articles stats

Research and Learning
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Research a specific topic
   om articles search burnout
   
   # Find related books and resources
   om articles list books
   
   # Check collections for organized content
   om articles collections
   
   # Add your own discoveries
   om articles add https://example.com/great-article

The mental health articles library transforms om into a comprehensive learning and reference platform, helping you build knowledge and find support for your mental health journey.
