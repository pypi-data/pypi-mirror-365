#!/usr/bin/env python3
"""
Positive Affirmations Module for om Platform

This module provides daily positive affirmations to support mental health and wellbeing.
Inspired by the affirmations-api by misselliev, this module includes a comprehensive
collection of affirmations for self-love, healing, confidence, and personal growth.

Features:
- Daily random affirmations
- Category-based affirmations (self-love, healing, confidence, etc.)
- Personal affirmation tracking and favorites
- Integration with mood tracking and mental health classification
- Beautiful terminal display with rich formatting
- Offline functionality with local storage
"""

import json
import os
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys

# Rich imports for beautiful terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

class AffirmationsManager:
    """Manages positive affirmations for mental health support"""
    
    def __init__(self):
        self.db_path = os.path.expanduser("~/.om/affirmations.db")
        self.init_database()
        self.load_affirmations()
        
    def init_database(self):
        """Initialize the SQLite database for storing affirmations and user data"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Affirmations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS affirmations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phrase TEXT NOT NULL UNIQUE,
                    category TEXT DEFAULT 'general',
                    source TEXT DEFAULT 'dulce-affirmations-api',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User interactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_affirmations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    affirmation_id INTEGER,
                    date TEXT NOT NULL,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    notes TEXT,
                    mood_before TEXT,
                    mood_after TEXT,
                    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
                )
            """)
            
            # Daily affirmations log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_affirmations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    affirmation_id INTEGER,
                    viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
                )
            """)
            
            # Categories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    color TEXT DEFAULT 'blue'
                )
            """)
            
            # Statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS affirmation_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_viewed INTEGER DEFAULT 0,
                    favorites_count INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    last_viewed TEXT,
                    avg_rating REAL DEFAULT 0.0
                )
            """)
            
            conn.commit()
            
            # Initialize stats if empty
            cursor = conn.execute("SELECT COUNT(*) FROM affirmation_stats")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO affirmation_stats DEFAULT VALUES")
                conn.commit()
    
    def load_affirmations(self):
        """Load affirmations from the dulce-affirmations-api dataset"""
        # Check if affirmations are already loaded
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM affirmations")
            if cursor.fetchone()[0] > 0:
                return  # Already loaded
        
        # Original affirmations text from the dulce-affirmations-api
        affirmations_text = """life loves me. everything is working out for my highest good. out of this situation only good will come. I am safe. it's only a thought and a thought can be changed. the point of power is always in the present moment. every thought we think is creating our future. I am in the process of positive change. I am comfortable looking in the mirror saying I love you. I really love you. it is safe to look within. I forgive myself and set myself free. as I say yes to life life says yes to me. I now go beyond other people. I am divinely guided and protected at all times. I claim my power and move beyond all limitations. I trust the process of life. I am deeply fulfilled by all that I do. we are all family and the planet is our home. I forgive myself and it becomes easier to forgive others. I am willing to let go. deep at the center of my being is an infinite well of love. I prosper wherever I turn. I welcome miracles into my life. whatever I need to know is revealed to me at exactly the right time. I am loved and I am at peace. my happy thoughts help create my healthy body. life supports me in every possible way. my day begins and ends with gratitude. I listen with love to my body's messages. the past is over. only good can come to me. I am beautiful and everybody loves me. everyone I encounter today has my best interests at heart. I always work with and for wonderful people. I love my job. filling my mind with pleasant thoughts is the quickest road to health. I am healthy. I am whole. I am complete. I am at home in my body. I devote a portion of my time to helping others because it is good for my own health. I am greeted by love wherever I go. wellness is the natural state of my body. I am in perfect health. I am pain free and totally in sync with life. I am very thankful for all the love in my life. I find love everywhere. I know that old negative patterns no longer limit me. I let negative patterns go with ease. in the infinity of life everything is perfect whole and complete. I trust my intuition. I am willing to listen to that still small voice within. I am willing to ask for help when I need it. I forgive myself for not being perfect. I honor who I am. I attract only healthy relationships. I am always treated well. I do not have to prove myself to anyone. I come from the loving space of my heart and I know that love opens all doors. I am in harmony with nature. I welcome new ideas. today no person place or thing can irritate or annoy me. I choose to be at peace. I am safe in the universe and all life loves and supports me. I experience love wherever I go. I am willing to change. I drink lots of water to cleanse my body and mind. I choose to see clearly with the eyes of love. I cross all bridges with joy and ease. I release all drama from my life. loving others is easy when I love and accept myself. I balance my life between work rest and play. I return to the basics of life: forgiveness courage gratitude love and humor. I am in charge I now take my own power back. my body appreciates how I take care of it. I spend time with positive energetic people. the more peaceful I am inside the more peace I have to share with others. today is a sacred gift from life. I have the courage to live my dreams. I release all negative thoughts of the past and all worries about the future. I forgive everyone in my past for all perceived wrongs. I release them with love. I only speak positively about those in my world. negativity has no part in my life. we are all eternal spirit. I act as if I already have what I want. it is an excellent way to attract happiness in my life. I enjoy the foods that are best for my body. my life gets better all the time. it is safe for me to speak up for myself. I live in the paradise of my own creation. perfect health is my divine right and I claim it now. I release all criticism. I am on an ever-changing journey. I am grateful for my healthy body. I love life. love flows through my body healing all dis-ease. my income is constantly increasing. my healing is already in process. there is always more to learn. I now live in limitless love light and joy. I become more lovable every day. it is now safe for me to release all of my childhood traumas and move into love. I deserve all that is good. I am constantly discovering new ways to improve my health. love is all there is my life gets more fabulous every day. today I am at peace. loving others is easy when I love and accept myself. I have the perfect living space. I have compassion for all. I trust the universe to help me see the good in everything and in everyone. I love my family members just as they are. I do not try to change anyone. there is plenty for everyone and we bless and prosper each other. I love and approve of myself. life is good. I radiate love and others reflect love back to me. I am loving and lovable. I am attractive. life is full of love and I find it everywhere I go. it is easy for me to look in the mirror and say I love you. my words are always kind and loving and in return I hear kindness and love from others. every day of my life is filled with love. all communication between my partner and I is loving and kind. everything about me is lovable and worthy of love. all of my relationships are healthy because they are based in love and compassion. I wake up happy and excited every single day. each day of my life is filled with joy and love. I am enthusiastic about every second of my life. everything I do is fun healthy and exciting. I am a beacon of love and compassion. everyone sees how much joy and love I have for life. I crave new healthy experiences. all of my relationships are positive and filled with love and compassion. I see others as good people who are trying their best. I find opportunities to be kind and caring everywhere I look. I easily accomplish all of my goals. I only desire things that are healthy for me. I instantly manifest my desires. my life is full of magic and serendipity my thoughts and feelings are nourishing. I am present in every moment. I see beauty in everything. people treat me with kindness and respect. I am surrounded by peaceful people. my environment is calm and supportive. i'm allowed to take up space. I am smart enough to make my own decisions. i'm in control of how I react to others. I choose peace. i'm courageous and stand up for myself. I will succeed today. I deserve to have joy in my life. i'm worthy of love. I approve of myself and love myself deeply. my body is healthy and i'm grateful. i'm more at ease every day. i'm calm happy and content. my life is a gift and I appreciate everything I have. i'll surround myself with positive people who will help bring out the best in me. my potential to succeed is limitless. i'm doing my best and that is enough. I have the power to create change. I know exactly what to do to achieve success. I choose to be proud of myself and the things I choose to do. I am enough. I love myself fully including the way I look. my life becomes richer as I get older. I can absolutely do anything I put my mind to. i'm worthy of respect and acceptance. my contributions to the world are valuable. my needs and wants are important. I make a significant difference to the lives of people around me. I am blessed with an amazing family and friends. I attract money easily into my life. my life is full of amazing opportunities that are ready for me to step into. i'm free to create the life I desire. i'm open to new adventures in my life. i'm bold beautiful and brilliant. my body shape is perfect in the way it's intended to be. when I allow my light to shine I unconsciously give other people permission to do the same. to make small steps toward big goals is progress. I am as god created me. as I become more and more aware of myself as eternal consciousness I become more peaceful and at ease with all that happens in my life. physical reality reflects this peace back to me. everything in my life is exactly should be my relationships are loving and harmonious I am at peace. I trust in the process of life I am connected to divine love and wisdom. I am harmonious and at peace regardless of my surroundings my life is blossoming in perfection I use my emotions thoughts and challenges to lead me to deeper more interesting places within myself. I am grateful for all that I am I feel god's love within me – and all around me I am a channel for loving peaceful energy I radiate with loving kindness and life mirrors that back to me I remember myself as the master that I am the master I have always been. I know I have mastery over my life by how still I can keep my mind and how alert I am in the now. I use my power lovingly when I have influence over others I am clear untouched and unharmed by all that I have experienced in my life. every day and in every way I am getting better and better I am abundantly joyful and happy I am so grateful for my life I find beauty and joy in ordinary things my life is a joy. I relax easily and open myself up to delightful surprises my life is a joy filled with love fun and friendship I choose love joy and freedom open my heart and allow wonderful things to flow into my life. I feel better and better each and every day in each and every way. I accept myself exactly as I am. I am filled with gratitude for all that I have. every cell in my body sparkles with joy and happiness. every cell in my body vibrates with energy and health. life is good. I love life and it loves me. loving kindness fills my body and soul with goodness and health. I am radiantly healthy in body mind and spirit. my cells organs and system function in health and harmony. I heal with ease and joy. I attract and accept perfect health. it makes me feel good. I feel deserving of a healthy happy life and I accept it gratefully. I always maintain a perfectly healthy mind body and spirit. every day and in every way I get better and better. I am kind and loving to myself. I heal myself with love and gratitude. I am attuned to the needs of my body mind and spirit. I pay attention and nourish myself with all that is wholesome. I pay attention and nourish myself with all that is nourishing. I pay attention and nourish myself with all that is good for me. my body is the temple that houses my spirit. I treat my body with reverence and care. I nourish my mind body and soul. my body heals quickly and easily. I love my body and my body loves me. every cell every gland and every organ in my body regenerates itself. I feel the glow of god's love in every cell of my body. I allow accept and appreciate healing throughout my body mind and spirit. I am restoring myself to perfect health. I feel revitalized refreshed and in perfect health. every cell every organ and every gland of every system in my body thrives in ultimate wellness and natural perfection. I feel healthier and happier than I have in years. I am unconditionally accepting of my body and my health. I completely love and accept myself. every part of me easily and effortlessly lets go of hurt and negative feelings. I am perfectly healthy in body mind and emotions. the more I relax the better I feel and the healthier I am. I am cool calm and confident. I am in full control of my body mind and emotions. my body functions in health and harmony. I am relaxed focused and in control. I feel relaxed focused and in full control of my body brain and mind. positive thoughts expand within me and I open myself to all the possibilities and abundance of the universe now. I allow myself to be fully present. feeling relaxed truly enjoying being in the moment. I am calm clear and confident. I feel relaxation flowing from the top of my head down to my toes. every cell in my body relaxes and functions in perfect harmony. I release tension from each and every part of my mind and body now. I feel comfort and relaxation flowing through me now expanding with every breath. peace and harmony flow through my body. it feels so good to be alive and well. with every breath I relax even more. it is a wonderful feeling to be so deeply relaxed and calmly comfortable. with every breath I become more relaxed more focused. with every breath I feel more comfortable. I am whole complete and happy within myself the more. I love myself the more love I have to give. I am filled with gratitude for all the wonderful gifts I have been given. I am unconditionally friendly to myself and others. I am vibrantly healthy and radiantly beautiful. I radiate beauty and positive energy from deep within. I am an open channel of loving creative energy. I love and appreciate myself just as I am. I am blossoming in perfection in a mind clear as still water. Even the waves are reflecting its light."""
        
        # Split into individual affirmations and clean them
        affirmations = [phrase.strip().capitalize() for phrase in affirmations_text.split('.') if phrase.strip()]
        
        # Categorize affirmations based on keywords
        categories = self.categorize_affirmations(affirmations)
        
        # Insert affirmations into database
        with sqlite3.connect(self.db_path) as conn:
            for i, phrase in enumerate(affirmations):
                if phrase:  # Skip empty phrases
                    category = categories[i] if i < len(categories) else 'general'
                    conn.execute("""
                        INSERT OR IGNORE INTO affirmations (phrase, category, source)
                        VALUES (?, ?, ?)
                    """, (phrase, category, 'dulce-affirmations-api'))
            
            # Insert categories
            category_data = [
                ('self-love', 'Affirmations for self-acceptance and self-worth', 'pink'),
                ('healing', 'Affirmations for physical and emotional healing', 'green'),
                ('confidence', 'Affirmations for building confidence and courage', 'blue'),
                ('abundance', 'Affirmations for prosperity and success', 'gold'),
                ('relationships', 'Affirmations for healthy relationships', 'purple'),
                ('peace', 'Affirmations for inner peace and calm', 'cyan'),
                ('health', 'Affirmations for physical and mental health', 'green'),
                ('gratitude', 'Affirmations for thankfulness and appreciation', 'yellow'),
                ('general', 'General positive affirmations', 'white')
            ]
            
            for name, description, color in category_data:
                conn.execute("""
                    INSERT OR IGNORE INTO categories (name, description, color)
                    VALUES (?, ?, ?)
                """, (name, description, color))
            
            conn.commit()
    
    def categorize_affirmations(self, affirmations: List[str]) -> List[str]:
        """Categorize affirmations based on keywords"""
        category_keywords = {
            'self-love': ['love myself', 'i am', 'i deserve', 'i accept', 'i approve', 'worthy', 'enough', 'beautiful'],
            'healing': ['heal', 'healing', 'health', 'healthy', 'body', 'pain', 'wellness', 'restore'],
            'confidence': ['confident', 'courage', 'strong', 'power', 'succeed', 'achieve', 'capable', 'bold'],
            'abundance': ['prosper', 'money', 'income', 'abundance', 'success', 'opportunities', 'wealth'],
            'relationships': ['love', 'relationship', 'family', 'friends', 'partner', 'communication', 'loving'],
            'peace': ['peace', 'calm', 'peaceful', 'relax', 'harmony', 'still', 'quiet', 'serene'],
            'health': ['healthy', 'body', 'mind', 'spirit', 'energy', 'vitality', 'wellness', 'strong'],
            'gratitude': ['grateful', 'gratitude', 'thankful', 'appreciate', 'blessed', 'gift', 'abundance']
        }
        
        categories = []
        for affirmation in affirmations:
            affirmation_lower = affirmation.lower()
            category = 'general'  # default
            
            for cat, keywords in category_keywords.items():
                if any(keyword in affirmation_lower for keyword in keywords):
                    category = cat
                    break
            
            categories.append(category)
        
        return categories
        
    def get_daily_affirmation(self) -> Dict:
        """Get the daily affirmation, ensuring one per day"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if we already have a daily affirmation for today
            cursor = conn.execute("""
                SELECT a.id, a.phrase, a.category 
                FROM daily_affirmations da
                JOIN affirmations a ON da.affirmation_id = a.id
                WHERE da.date = ?
            """, (today,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'phrase': result[1],
                    'category': result[2],
                    'date': today,
                    'is_new': False
                }
            
            # Get a random affirmation
            cursor = conn.execute("""
                SELECT id, phrase, category 
                FROM affirmations 
                ORDER BY RANDOM() 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if not result:
                return {'error': 'No affirmations available'}
            
            affirmation_id, phrase, category = result
            
            # Store as today's daily affirmation
            conn.execute("""
                INSERT INTO daily_affirmations (date, affirmation_id)
                VALUES (?, ?)
            """, (today, affirmation_id))
            
            # Update stats
            conn.execute("""
                UPDATE affirmation_stats 
                SET total_viewed = total_viewed + 1,
                    last_viewed = ?
            """, (datetime.now().isoformat(),))
            
            conn.commit()
            
            return {
                'id': affirmation_id,
                'phrase': phrase,
                'category': category,
                'date': today,
                'is_new': True
            }
    
    def get_affirmations_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get affirmations by category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, phrase, category 
                FROM affirmations 
                WHERE category = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (category, limit))
            
            return [
                {'id': row[0], 'phrase': row[1], 'category': row[2]}
                for row in cursor.fetchall()
            ]
    
    def get_random_affirmation(self) -> Dict:
        """Get a random affirmation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, phrase, category 
                FROM affirmations 
                ORDER BY RANDOM() 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                return {'id': result[0], 'phrase': result[1], 'category': result[2]}
            return {'error': 'No affirmations available'}
    
    def add_to_favorites(self, affirmation_id: int, rating: int = 5, notes: str = ""):
        """Add an affirmation to favorites"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_affirmations 
                (affirmation_id, date, is_favorite, rating, notes)
                VALUES (?, ?, TRUE, ?, ?)
            """, (affirmation_id, today, rating, notes))
            
            # Update stats
            conn.execute("""
                UPDATE affirmation_stats 
                SET favorites_count = (
                    SELECT COUNT(*) FROM user_affirmations WHERE is_favorite = TRUE
                )
            """)
            
            conn.commit()
    
    def get_favorites(self) -> List[Dict]:
        """Get user's favorite affirmations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT a.id, a.phrase, a.category, ua.rating, ua.notes, ua.date
                FROM user_affirmations ua
                JOIN affirmations a ON ua.affirmation_id = a.id
                WHERE ua.is_favorite = TRUE
                ORDER BY ua.date DESC
            """)
            
            return [
                {
                    'id': row[0],
                    'phrase': row[1],
                    'category': row[2],
                    'rating': row[3],
                    'notes': row[4],
                    'date': row[5]
                }
                for row in cursor.fetchall()
            ]
    
    def get_categories(self) -> List[Dict]:
        """Get all available categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT c.name, c.description, c.color, COUNT(a.id) as count
                FROM categories c
                LEFT JOIN affirmations a ON c.name = a.category
                GROUP BY c.name, c.description, c.color
                ORDER BY count DESC
            """)
            
            return [
                {
                    'name': row[0],
                    'description': row[1],
                    'color': row[2],
                    'count': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def get_statistics(self) -> Dict:
        """Get user statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM affirmation_stats LIMIT 1")
            stats = cursor.fetchone()
            
            if not stats:
                return {}
            
            # Calculate streak
            streak = self.calculate_streak()
            
            # Update streak in database
            conn.execute("""
                UPDATE affirmation_stats SET streak_days = ?
            """, (streak,))
            conn.commit()
            
            return {
                'total_viewed': stats[1],
                'favorites_count': stats[2],
                'streak_days': streak,
                'last_viewed': stats[4],
                'avg_rating': stats[5] or 0.0
            }
    
    def calculate_streak(self) -> int:
        """Calculate current daily streak"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT date FROM daily_affirmations 
                ORDER BY date DESC
            """)
            
            dates = [row[0] for row in cursor.fetchall()]
            
            if not dates:
                return 0
            
            streak = 0
            current_date = datetime.now().date()
            
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                if date_obj == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif date_obj == current_date + timedelta(days=1):
                    # Yesterday's affirmation
                    streak += 1
                    current_date = date_obj - timedelta(days=1)
                else:
                    break
            
            return streak
    
    def search_affirmations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search affirmations by text"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, phrase, category 
                FROM affirmations 
                WHERE phrase LIKE ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (f'%{query}%', limit))
            
            return [
                {'id': row[0], 'phrase': row[1], 'category': row[2]}
                for row in cursor.fetchall()
            ]

def display_affirmation(affirmation: Dict, show_category: bool = True):
    """Display an affirmation with beautiful formatting"""
    if 'error' in affirmation:
        if console:
            console.print(f"[red]Error: {affirmation['error']}[/red]")
        else:
            print(f"Error: {affirmation['error']}")
        return
    
    phrase = affirmation['phrase']
    category = affirmation.get('category', 'general')
    
    if not RICH_AVAILABLE:
        print(f"\n✨ Daily Affirmation ✨")
        print("=" * 50)
        print(f"\"{phrase}\"")
        if show_category:
            print(f"\nCategory: {category.title()}")
        print("=" * 50)
        return
    
    # Color mapping for categories
    category_colors = {
        'self-love': 'magenta',
        'healing': 'green',
        'confidence': 'blue',
        'abundance': 'yellow',
        'relationships': 'magenta',
        'peace': 'cyan',
        'health': 'green',
        'gratitude': 'yellow',
        'general': 'white'
    }
    
    color = category_colors.get(category, 'white')
    
    # Create the main panel
    if show_category:
        title = f"✨ Daily Affirmation - {category.title()} ✨"
    else:
        title = "✨ Daily Affirmation ✨"
    
    # Format the phrase with proper styling
    styled_phrase = f"[bold {color}]\"{phrase}\"[/bold {color}]"
    
    console.print(Panel(
        Align.center(styled_phrase),
        title=title,
        border_style=color,
        padding=(1, 2)
    ))

def display_categories(categories: List[Dict]):
    """Display available categories"""
    if not categories:
        if console:
            console.print("[yellow]No categories available.[/yellow]")
        else:
            print("No categories available.")
        return
    
    if not RICH_AVAILABLE:
        print("\nAvailable Categories:")
        print("=" * 30)
        for cat in categories:
            print(f"• {cat['name'].title()}: {cat['description']} ({cat['count']} affirmations)")
        return
    
    table = Table(title="🌟 Affirmation Categories", show_header=True, header_style="bold blue")
    table.add_column("Category", style="cyan", width=15)
    table.add_column("Description", style="white", width=40)
    table.add_column("Count", justify="right", style="green", width=8)
    
    for cat in categories:
        table.add_row(
            cat['name'].title(),
            cat['description'],
            str(cat['count'])
        )
    
    console.print(table)

def display_favorites(favorites: List[Dict]):
    """Display favorite affirmations"""
    if not favorites:
        if console:
            console.print("[yellow]No favorite affirmations yet. Use 'om affirmations favorite' to add some![/yellow]")
        else:
            print("No favorite affirmations yet. Use 'om affirmations favorite' to add some!")
        return
    
    if not RICH_AVAILABLE:
        print("\nYour Favorite Affirmations:")
        print("=" * 40)
        for i, fav in enumerate(favorites, 1):
            print(f"{i}. \"{fav['phrase']}\"")
            print(f"   Category: {fav['category'].title()} | Rating: {fav['rating']}/5")
            if fav['notes']:
                print(f"   Notes: {fav['notes']}")
            print()
        return
    
    for fav in favorites:
        category_colors = {
            'self-love': 'magenta', 'healing': 'green', 'confidence': 'blue',
            'abundance': 'yellow', 'relationships': 'magenta', 'peace': 'cyan',
            'health': 'green', 'gratitude': 'yellow', 'general': 'white'
        }
        
        color = category_colors.get(fav['category'], 'white')
        
        # Rating stars
        stars = "⭐" * fav['rating'] + "☆" * (5 - fav['rating'])
        
        content = f"[bold {color}]\"{fav['phrase']}\"[/bold {color}]\n\n"
        content += f"[dim]Category: {fav['category'].title()} | Rating: {stars}[/dim]"
        
        if fav['notes']:
            content += f"\n[italic]Notes: {fav['notes']}[/italic]"
        
        console.print(Panel(
            content,
            title=f"💖 Favorite from {fav['date']}",
            border_style=color,
            padding=(1, 2)
        ))

def display_statistics(stats: Dict):
    """Display user statistics"""
    if not stats:
        if console:
            console.print("[yellow]No statistics available yet.[/yellow]")
        else:
            print("No statistics available yet.")
        return
    
    if not RICH_AVAILABLE:
        print("\nYour Affirmation Statistics:")
        print("=" * 35)
        print(f"Total Viewed: {stats['total_viewed']}")
        print(f"Favorites: {stats['favorites_count']}")
        print(f"Current Streak: {stats['streak_days']} days")
        print(f"Average Rating: {stats['avg_rating']:.1f}/5")
        if stats['last_viewed']:
            print(f"Last Viewed: {stats['last_viewed'][:19].replace('T', ' ')}")
        return
    
    # Create statistics display
    table = Table(title="📊 Your Affirmation Journey", show_header=False, box=None)
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Value", style="bold green", width=15)
    table.add_column("Icon", width=5)
    
    # Streak emoji based on days
    if stats['streak_days'] >= 30:
        streak_emoji = "🔥"
    elif stats['streak_days'] >= 7:
        streak_emoji = "⚡"
    elif stats['streak_days'] >= 3:
        streak_emoji = "✨"
    else:
        streak_emoji = "🌱"
    
    table.add_row("Total Viewed", str(stats['total_viewed']), "👁️")
    table.add_row("Favorites", str(stats['favorites_count']), "💖")
    table.add_row("Current Streak", f"{stats['streak_days']} days", streak_emoji)
    
    # Handle avg_rating which might be None or string
    avg_rating = stats.get('avg_rating', 0)
    if avg_rating is None:
        avg_rating = 0.0
    elif isinstance(avg_rating, str):
        try:
            avg_rating = float(avg_rating)
        except (ValueError, TypeError):
            avg_rating = 0.0
    
    table.add_row("Average Rating", f"{avg_rating:.1f}/5", "⭐")
    
    console.print(table)
    
    # Motivational message based on streak
    if stats['streak_days'] >= 30:
        message = "[bold green]🎉 Amazing! You're building a powerful daily practice![/bold green]"
    elif stats['streak_days'] >= 7:
        message = "[bold blue]🌟 Great job! You're developing a wonderful habit![/bold blue]"
    elif stats['streak_days'] >= 3:
        message = "[bold yellow]✨ Nice start! Keep up the momentum![/bold yellow]"
    else:
        message = "[dim]💡 Tip: Daily affirmations work best with consistency![/dim]"
    
    console.print(f"\n{message}")

def main():
    """Main function for the affirmations module"""
    manager = AffirmationsManager()
    
    if len(sys.argv) < 2:
        # Default: show daily affirmation
        affirmation = manager.get_daily_affirmation()
        display_affirmation(affirmation)
        return
    
    command = sys.argv[1].lower()
    
    if command == "daily":
        affirmation = manager.get_daily_affirmation()
        display_affirmation(affirmation)
        
    elif command == "random":
        affirmation = manager.get_random_affirmation()
        display_affirmation(affirmation, show_category=True)
        
    elif command == "categories":
        categories = manager.get_categories()
        display_categories(categories)
        
    elif command == "category":
        if len(sys.argv) < 3:
            if console:
                console.print("[red]Usage: om affirmations category <category_name>[/red]")
            else:
                print("Usage: om affirmations category <category_name>")
            return
        
        category = sys.argv[2].lower()
        affirmations = manager.get_affirmations_by_category(category, 5)
        
        if not affirmations:
            if console:
                console.print(f"[yellow]No affirmations found for category '{category}'[/yellow]")
            else:
                print(f"No affirmations found for category '{category}'")
            return
        
        for affirmation in affirmations:
            display_affirmation(affirmation, show_category=False)
            if console:
                console.print()
    
    elif command == "favorite":
        # Get today's daily affirmation and add to favorites
        daily = manager.get_daily_affirmation()
        if 'error' not in daily:
            if console:
                rating = int(Prompt.ask("Rate this affirmation (1-5)", default="5"))
                notes = Prompt.ask("Add notes (optional)", default="")
            else:
                rating = 5
                notes = ""
            
            manager.add_to_favorites(daily['id'], rating, notes)
            if console:
                console.print("[green]✅ Added to favorites![/green]")
            else:
                print("✅ Added to favorites!")
    
    elif command == "favorites":
        favorites = manager.get_favorites()
        display_favorites(favorites)
        
    elif command == "stats":
        stats = manager.get_statistics()
        display_statistics(stats)
        
    elif command == "search":
        if len(sys.argv) < 3:
            if console:
                console.print("[red]Usage: om affirmations search <query>[/red]")
            else:
                print("Usage: om affirmations search <query>")
            return
        
        query = " ".join(sys.argv[2:])
        results = manager.search_affirmations(query)
        
        if not results:
            if console:
                console.print(f"[yellow]No affirmations found matching '{query}'[/yellow]")
            else:
                print(f"No affirmations found matching '{query}'")
            return
        
        if console:
            console.print(f"[bold blue]Search results for '{query}':[/bold blue]\n")
        else:
            print(f"Search results for '{query}':\n")
        
        for affirmation in results:
            display_affirmation(affirmation, show_category=True)
            if console:
                console.print()
    
    else:
        if console:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[yellow]Available commands: daily, random, categories, category, favorite, favorites, stats, search[/yellow]")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: daily, random, categories, category, favorite, favorites, stats, search")

if __name__ == "__main__":
    main()
