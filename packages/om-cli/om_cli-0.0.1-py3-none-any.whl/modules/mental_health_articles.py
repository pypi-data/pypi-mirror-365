"""
Mental Health Articles Module for om
Manages curated mental health articles, resources, and reading progress
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
from urllib.parse import urlparse
import re

# Database connection
def get_db_connection():
    """Get database connection"""
    db_path = os.path.expanduser("~/.om/om.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def initialize_articles_db():
    """Initialize the articles database schema"""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mental_health_articles_schema.sql')
    
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = get_db_connection()
        conn.executescript(schema)
        conn.commit()
        conn.close()
        return True
    return False

def add_article(title, url, author=None, description=None, category='articles', 
                subcategory=None, tags=None, target_audience='developers'):
    """Add a new article to the database"""
    conn = get_db_connection()
    
    article_id = str(uuid.uuid4())
    tags_json = json.dumps(tags) if tags else None
    
    try:
        conn.execute("""
            INSERT INTO mental_health_articles 
            (id, title, url, author, description, category, subcategory, 
             tags, target_audience, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (article_id, title, url, author, description, category, 
              subcategory, tags_json, target_audience, 'user_added'))
        
        conn.commit()
        return article_id
    except sqlite3.IntegrityError:
        return None  # URL already exists
    finally:
        conn.close()

def get_articles(category=None, subcategory=None, is_favorite=None, 
                is_read=None, limit=50, offset=0):
    """Get articles with optional filtering"""
    conn = get_db_connection()
    
    query = "SELECT * FROM mental_health_articles WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if subcategory:
        query += " AND subcategory = ?"
        params.append(subcategory)
    
    if is_favorite is not None:
        query += " AND is_favorite = ?"
        params.append(is_favorite)
    
    if is_read is not None:
        query += " AND is_read = ?"
        params.append(is_read)
    
    query += " ORDER BY date_added DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor = conn.execute(query, params)
    articles = cursor.fetchall()
    conn.close()
    
    return [dict(zip([col[0] for col in cursor.description], row)) for row in articles]

def search_articles(search_term, limit=20):
    """Search articles by title, description, or tags"""
    conn = get_db_connection()
    
    query = """
        SELECT * FROM mental_health_articles 
        WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
        ORDER BY 
            CASE 
                WHEN title LIKE ? THEN 1
                WHEN description LIKE ? THEN 2
                ELSE 3
            END,
            date_added DESC
        LIMIT ?
    """
    
    search_pattern = f"%{search_term}%"
    title_pattern = f"%{search_term}%"
    
    cursor = conn.execute(query, [search_pattern, search_pattern, search_pattern,
                                 title_pattern, search_pattern, limit])
    articles = cursor.fetchall()
    conn.close()
    
    return [dict(zip([col[0] for col in cursor.description], row)) for row in articles]

def mark_article_read(article_id, rating=None, notes=None):
    """Mark an article as read with optional rating and notes"""
    conn = get_db_connection()
    
    conn.execute("""
        UPDATE mental_health_articles 
        SET is_read = 1, date_read = ?, user_rating = ?, user_notes = ?,
            updated_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), rating, notes, 
          datetime.now().isoformat(), article_id))
    
    conn.commit()
    conn.close()

def toggle_favorite(article_id):
    """Toggle favorite status of an article"""
    conn = get_db_connection()
    
    # Get current status
    cursor = conn.execute("SELECT is_favorite FROM mental_health_articles WHERE id = ?", 
                         (article_id,))
    result = cursor.fetchone()
    
    if result:
        new_status = not result[0]
        conn.execute("""
            UPDATE mental_health_articles 
            SET is_favorite = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, datetime.now().isoformat(), article_id))
        conn.commit()
        conn.close()
        return new_status
    
    conn.close()
    return None

def get_collections():
    """Get all article collections"""
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT c.*, COUNT(ca.article_id) as article_count
        FROM article_collections c
        LEFT JOIN collection_articles ca ON c.id = ca.collection_id
        GROUP BY c.id
        ORDER BY c.is_system_collection DESC, c.name
    """)
    collections = cursor.fetchall()
    conn.close()
    
    return [dict(zip([col[0] for col in cursor.description], row)) for row in collections]

def get_collection_articles(collection_id):
    """Get articles in a specific collection"""
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT a.*, ca.sort_order, ca.added_at
        FROM mental_health_articles a
        JOIN collection_articles ca ON a.id = ca.article_id
        WHERE ca.collection_id = ?
        ORDER BY ca.sort_order, ca.added_at
    """, (collection_id,))
    articles = cursor.fetchall()
    conn.close()
    
    return [dict(zip([col[0] for col in cursor.description], row)) for row in articles]

def add_to_collection(collection_id, article_id):
    """Add an article to a collection"""
    conn = get_db_connection()
    
    try:
        conn.execute("""
            INSERT INTO collection_articles (id, collection_id, article_id)
            VALUES (?, ?, ?)
        """, (str(uuid.uuid4()), collection_id, article_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Already in collection
    finally:
        conn.close()

def get_reading_stats():
    """Get reading statistics"""
    conn = get_db_connection()
    
    stats = {}
    
    # Total articles
    cursor = conn.execute("SELECT COUNT(*) FROM mental_health_articles")
    stats['total_articles'] = cursor.fetchone()[0]
    
    # Read articles
    cursor = conn.execute("SELECT COUNT(*) FROM mental_health_articles WHERE is_read = 1")
    stats['read_articles'] = cursor.fetchone()[0]
    
    # Favorite articles
    cursor = conn.execute("SELECT COUNT(*) FROM mental_health_articles WHERE is_favorite = 1")
    stats['favorite_articles'] = cursor.fetchone()[0]
    
    # Articles by category
    cursor = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM mental_health_articles
        GROUP BY category
        ORDER BY count DESC
    """)
    stats['by_category'] = dict(cursor.fetchall())
    
    # Reading progress
    if stats['total_articles'] > 0:
        stats['reading_percentage'] = round((stats['read_articles'] / stats['total_articles']) * 100, 1)
    else:
        stats['reading_percentage'] = 0
    
    conn.close()
    return stats

def display_article_list(articles, show_details=False):
    """Display a formatted list of articles"""
    if not articles:
        print("📚 No articles found.")
        return
    
    print(f"📚 Found {len(articles)} article(s):")
    print("=" * 60)
    
    for i, article in enumerate(articles, 1):
        # Status indicators
        read_status = "✅" if article.get('is_read') else "⭕"
        fav_status = "⭐" if article.get('is_favorite') else ""
        rating = f"({article.get('user_rating')}/10)" if article.get('user_rating') else ""
        
        print(f"{i}. {read_status} {fav_status} {article['title']}")
        
        if article.get('author'):
            print(f"   👤 By {article['author']}")
        
        if show_details and article.get('description'):
            print(f"   📝 {article['description'][:100]}{'...' if len(article.get('description', '')) > 100 else ''}")
        
        print(f"   🔗 {article['url']}")
        print(f"   🏷️  {article['category'].title()}", end="")
        
        if article.get('subcategory'):
            print(f" → {article['subcategory'].replace('-', ' ').title()}", end="")
        
        if rating:
            print(f" {rating}", end="")
        
        print()
        
        if article.get('tags'):
            try:
                tags = json.loads(article['tags'])
                if tags:
                    print(f"   🏷️  Tags: {', '.join(tags)}")
            except:
                pass
        
        print()

def display_reading_stats():
    """Display reading statistics"""
    stats = get_reading_stats()
    
    print("📊 Reading Statistics")
    print("=" * 30)
    print(f"📚 Total Articles: {stats['total_articles']}")
    print(f"✅ Read: {stats['read_articles']}")
    print(f"⭐ Favorites: {stats['favorite_articles']}")
    print(f"📈 Progress: {stats['reading_percentage']}%")
    
    if stats['by_category']:
        print("\n📂 By Category:")
        for category, count in stats['by_category'].items():
            print(f"   {category.title()}: {count}")

def display_collections():
    """Display all collections"""
    collections = get_collections()
    
    if not collections:
        print("📁 No collections found.")
        return
    
    print("📁 Article Collections:")
    print("=" * 40)
    
    for collection in collections:
        system_indicator = "🔒" if collection['is_system_collection'] else "📁"
        print(f"{system_indicator} {collection['name']} ({collection['article_count']} articles)")
        
        if collection.get('description'):
            print(f"   {collection['description']}")
        print()

def import_awesome_mental_health_articles():
    """Import articles from the awesome-mental-health repository"""
    
    # Articles data extracted from the repository
    articles_data = [
        {
            "title": "A Programmers Guide To Stress",
            "url": "http://codingmindfully.com/a-programmers-guide-to-stress/",
            "author": "Daragh Byrne",
            "category": "articles",
            "subcategory": "stress-management",
            "tags": ["stress-management", "mindfulness", "programming"],
            "description": "A comprehensive guide for programmers on understanding and managing stress in software development."
        },
        {
            "title": "Are You More Than Okay: The State Of Mental Health In Tech In 2016",
            "url": "https://modelviewculture.com/pieces/are-you-more-than-okay-the-state-of-mental-health-in-tech-in-2016",
            "author": "Julia Nguyen",
            "category": "articles",
            "subcategory": "industry-analysis",
            "tags": ["mental-health", "tech-industry", "survey", "statistics"],
            "description": "An analysis of mental health trends and challenges in the tech industry based on 2016 data."
        },
        {
            "title": "Beating Burnout: A Guide For Supporting Mental Health At Work",
            "url": "https://almanac.io/docs/beating-burnout-a-guide-for-supporting-mental-health-at-work-yDLKVF3uJtMdshcZG37HP7OHpAczogYX",
            "author": "Almanac Core",
            "category": "articles",
            "subcategory": "burnout",
            "tags": ["burnout", "workplace", "prevention", "recovery"],
            "description": "A comprehensive guide for supporting mental health and preventing burnout in the workplace."
        },
        {
            "title": "Developer Depression: Isolation Is The Biggest Problem",
            "url": "https://thenextweb.com/insider/2012/10/20/are-developers-depressed/#gref",
            "author": "Lauren Maffeo",
            "category": "articles",
            "subcategory": "depression",
            "tags": ["depression", "isolation", "remote-work", "social-connection"],
            "description": "Exploring how isolation contributes to depression among software developers."
        },
        {
            "title": "Developers: How to Overcome Imposter Syndrome",
            "url": "https://medium.com/learn-love-code/developers-how-to-overcome-imposter-syndrome-48edee803cf4",
            "author": "Abhishek Pillai",
            "category": "articles",
            "subcategory": "imposter-syndrome",
            "tags": ["imposter-syndrome", "self-confidence", "career-development"],
            "description": "Practical strategies for developers to overcome imposter syndrome and build confidence."
        },
        {
            "title": "How I Beat Impostor Syndrome And Stopped Feeling Like A Fake",
            "url": "http://codingmindfully.com/how-i-beat-impostor-syndrome/",
            "author": "Daragh Byrne",
            "category": "articles",
            "subcategory": "imposter-syndrome",
            "tags": ["imposter-syndrome", "personal-story", "recovery"],
            "description": "A personal account of overcoming impostor syndrome in software development."
        },
        {
            "title": "How To Keep Your Mental Health In Check When You Work From Home",
            "url": "https://weworkremotely.com/how-to-keep-your-mental-health-in-check-when-you-work-from-home",
            "author": "WeWorkRemotely",
            "category": "articles",
            "subcategory": "remote-work",
            "tags": ["remote-work", "work-life-balance", "mental-health"],
            "description": "Essential tips for maintaining mental health while working from home."
        },
        {
            "title": "Mental Illness In The Web Industry",
            "url": "https://alistapart.com/article/mental-illness-in-the-web-industry",
            "author": "Brandon Gregory",
            "category": "articles",
            "subcategory": "industry-analysis",
            "tags": ["mental-illness", "web-development", "stigma", "awareness"],
            "description": "An important discussion about mental illness prevalence and stigma in the web development industry."
        },
        {
            "title": "We Need To Talk About Developers And Depression",
            "url": "https://www.creativebloq.com/web-design/we-need-talk-about-developers-and-depression-101413045",
            "author": "Greg Baugues",
            "category": "articles",
            "subcategory": "depression",
            "tags": ["depression", "awareness", "stigma", "support"],
            "description": "Breaking the silence around depression in the developer community."
        },
        {
            "title": "It's Okay To Not Be Okay",
            "url": "https://dev.to/andrew/its-okay-to-not-be-okay",
            "author": "Andrew Montagne",
            "category": "articles",
            "subcategory": "mental-health-awareness",
            "tags": ["mental-health", "acceptance", "support", "community"],
            "description": "A compassionate reminder that struggling with mental health is normal and acceptable."
        }
    ]
    
    # Books data
    books_data = [
        {
            "title": "Developers and Depression",
            "url": "https://leanpub.com/developers-and-depression",
            "author": "Greg Baugues",
            "category": "books",
            "subcategory": "depression",
            "tags": ["depression", "bipolar", "ADHD", "personal-stories"],
            "description": "A candid collection of essays and talks exploring bipolar disorder, ADHD, and mental illness in the developer community."
        },
        {
            "title": "It Doesn't Have to Be Crazy at Work",
            "url": "https://www.amazon.com/Doesnt-Have-Be-Crazy-Work/dp/0062874780",
            "author": "Jason Fried and David Heinemeier Hansson",
            "category": "books",
            "subcategory": "work-culture",
            "tags": ["work-culture", "burnout", "productivity", "calm-work"],
            "description": "A manifesto for calm work culture from the Basecamp founders, arguing against hustle culture and burnout."
        },
        {
            "title": "Mental Health In Tech: Guidelines For Employees",
            "url": "https://leanpub.com/osmi-guidelines-for-employees",
            "author": "OSMI",
            "category": "books",
            "subcategory": "workplace-guidance",
            "tags": ["workplace", "legal-rights", "accommodations", "advocacy"],
            "description": "A practical guide for employees navigating mental health at work, covering legal rights, accommodations, and advocacy."
        }
    ]
    
    # Applications data
    apps_data = [
        {
            "title": "Headspace",
            "url": "https://www.headspace.com",
            "author": "Headspace Inc.",
            "category": "apps",
            "subcategory": "meditation",
            "tags": ["meditation", "mindfulness", "sleep", "stress-reduction"],
            "description": "A meditation and mindfulness app offering guided sessions, sleep aids, and stress-reduction techniques."
        },
        {
            "title": "Calm",
            "url": "https://www.calm.com",
            "author": "Calm.com Inc.",
            "category": "apps",
            "subcategory": "meditation",
            "tags": ["meditation", "sleep", "anxiety", "breathing"],
            "description": "Provides guided meditations, sleep stories, and breathing exercises to help reduce anxiety and improve sleep quality."
        },
        {
            "title": "Quirk",
            "url": "https://www.quirk.fyi/",
            "author": "Quirk CBT",
            "category": "apps",
            "subcategory": "cbt",
            "tags": ["cbt", "open-source", "privacy", "thought-tracking"],
            "description": "A free, open-source CBT app that helps you identify and reframe distorted thoughts."
        }
    ]
    
    conn = get_db_connection()
    imported_count = 0
    
    # Import all data
    all_data = articles_data + books_data + apps_data
    
    for item in all_data:
        try:
            article_id = str(uuid.uuid4())
            tags_json = json.dumps(item.get('tags', []))
            
            conn.execute("""
                INSERT INTO mental_health_articles 
                (id, title, url, author, description, category, subcategory, 
                 tags, target_audience, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (article_id, item['title'], item['url'], item.get('author'), 
                  item.get('description'), item['category'], item.get('subcategory'),
                  tags_json, 'developers', 'awesome-mental-health'))
            
            imported_count += 1
            
        except sqlite3.IntegrityError:
            # URL already exists, skip
            continue
    
    conn.commit()
    conn.close()
    
    return imported_count

def run(args=None):
    """Main entry point for the mental health articles module"""
    
    # Initialize database
    if not initialize_articles_db():
        print("❌ Could not initialize articles database")
        return
    
    if not args:
        print("📚 Mental Health Articles")
        print("A curated collection of mental health resources for developers")
        print()
        print("Available commands:")
        print("  om articles list          - List all articles")
        print("  om articles search <term> - Search articles")
        print("  om articles stats         - Show reading statistics")
        print("  om articles collections   - Show collections")
        print("  om articles import        - Import awesome-mental-health articles")
        print("  om articles favorites     - Show favorite articles")
        print("  om articles unread        - Show unread articles")
        print("  om articles add <url>     - Add a new article")
        return
    
    command = args[0].lower()
    
    if command == 'list':
        category = args[1] if len(args) > 1 else None
        articles = get_articles(category=category, limit=20)
        display_article_list(articles, show_details=True)
        
    elif command == 'search':
        if len(args) < 2:
            print("❌ Please provide a search term")
            return
        
        search_term = ' '.join(args[1:])
        articles = search_articles(search_term)
        print(f"🔍 Search results for '{search_term}':")
        display_article_list(articles, show_details=True)
        
    elif command == 'stats':
        display_reading_stats()
        
    elif command == 'collections':
        display_collections()
        
    elif command == 'import':
        print("📥 Importing articles from awesome-mental-health repository...")
        count = import_awesome_mental_health_articles()
        print(f"✅ Imported {count} new articles!")
        
    elif command == 'favorites':
        articles = get_articles(is_favorite=True)
        print("⭐ Your Favorite Articles:")
        display_article_list(articles, show_details=True)
        
    elif command == 'unread':
        articles = get_articles(is_read=False)
        print("📖 Unread Articles:")
        display_article_list(articles, show_details=True)
        
    elif command == 'add':
        if len(args) < 2:
            print("❌ Please provide a URL")
            return
        
        url = args[1]
        title = input("Article title: ").strip()
        author = input("Author (optional): ").strip() or None
        description = input("Description (optional): ").strip() or None
        
        article_id = add_article(title, url, author, description)
        if article_id:
            print(f"✅ Article added successfully!")
        else:
            print("❌ Article already exists or could not be added")
            
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'om articles' to see available commands")

def main():
    """Alternative entry point for direct execution"""
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    run(args)

if __name__ == "__main__":
    main()
