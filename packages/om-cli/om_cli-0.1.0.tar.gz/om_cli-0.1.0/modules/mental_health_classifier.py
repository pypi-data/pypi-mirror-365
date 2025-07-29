#!/usr/bin/env python3
"""
Mental Health Text Classification Module for om Platform

This module provides AI-powered mental health text classification using a fine-tuned BERT model
that can identify 15 different mental health categories from text input. It integrates with the
om platform's existing mental health tracking and provides insights for better support.

Categories supported:
- EDAnonymous (eating disorders)
- addiction
- alcoholism  
- adhd
- anxiety
- autism
- bipolarreddit (bipolar disorder)
- bpd (borderline personality disorder)
- depression
- healthanxiety
- lonely (loneliness)
- ptsd
- schizophrenia
- socialanxiety
- suicidewatch

Model: tahaenesaslanturk/mental-health-classification-v0.1
Accuracy: 64% (as noted by model author)
"""

import json
import os
import sqlite3
from datetime import datetime
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
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Transformers imports for the model
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

class MentalHealthClassifier:
    """Mental Health Text Classification using Hugging Face model"""
    
    def __init__(self):
        self.db_path = os.path.expanduser("~/.om/mental_health_classifier.db")
        self.model_name = "tahaenesaslanturk/mental-health-classification-v0.1"
        self.model = None
        self.tokenizer = None
        self.categories = {
            0: "EDAnonymous",
            1: "addiction", 
            2: "alcoholism",
            3: "adhd",
            4: "anxiety",
            5: "autism",
            6: "bipolarreddit",
            7: "bpd",
            8: "depression",
            9: "healthanxiety",
            10: "lonely",
            11: "ptsd",
            12: "schizophrenia",
            13: "socialanxiety",
            14: "suicidewatch"
        }
        self.category_descriptions = {
            "EDAnonymous": "Eating disorders and body image issues",
            "addiction": "Substance or behavioral dependencies",
            "alcoholism": "Alcohol-related problems and dependencies",
            "adhd": "Attention deficit hyperactivity disorder",
            "anxiety": "General anxiety and worry",
            "autism": "Autism spectrum conditions",
            "bipolarreddit": "Bipolar disorder and mood swings",
            "bpd": "Borderline personality disorder",
            "depression": "Depression and persistent sadness",
            "healthanxiety": "Health-related anxiety and hypochondria",
            "lonely": "Loneliness and social isolation",
            "ptsd": "Post-traumatic stress disorder",
            "schizophrenia": "Schizophrenia and psychotic symptoms",
            "socialanxiety": "Social anxiety and social fears",
            "suicidewatch": "Suicidal thoughts and crisis situations"
        }
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database for storing classifications"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    text TEXT NOT NULL,
                    predicted_category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    all_scores TEXT NOT NULL,
                    user_feedback TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS category_stats (
                    category TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0,
                    last_detected TEXT
                )
            """)
            
            # Initialize category stats
            for category in self.categories.values():
                conn.execute("""
                    INSERT OR IGNORE INTO category_stats (category, count, avg_confidence)
                    VALUES (?, 0, 0.0)
                """, (category,))
            
            conn.commit()
    
    def load_model(self):
        """Load the Hugging Face model and tokenizer"""
        if not TRANSFORMERS_AVAILABLE:
            if console:
                console.print("[red]Error: transformers library not available. Install with: pip install transformers torch[/red]")
            else:
                print("Error: transformers library not available. Install with: pip install transformers torch")
            return False
            
        try:
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Loading mental health classification model...", total=None)
                    
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                    
                    progress.update(task, description="Model loaded successfully!")
            else:
                print("Loading mental health classification model...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
                print("Model loaded successfully!")
                
            return True
            
        except Exception as e:
            if console:
                console.print(f"[red]Error loading model: {e}[/red]")
            else:
                print(f"Error loading model: {e}")
            return False
    
    def classify_text_fallback(self, text: str) -> Dict:
        """Fallback classification using keyword matching when AI model isn't available"""
        text_lower = text.lower()
        
        # Keyword patterns for each category
        keyword_patterns = {
            "depression": [
                "sad", "hopeless", "depressed", "empty", "worthless", "suicidal", "suicide",
                "nothing matters", "can't go on", "want to die", "end it all", "no point",
                "tired of living", "hate myself", "useless", "burden", "alone", "isolated"
            ],
            "anxiety": [
                "anxious", "worried", "panic", "fear", "scared", "nervous", "stress",
                "overwhelmed", "racing heart", "can't breathe", "sweating", "trembling",
                "restless", "on edge", "tense", "catastrophic", "worst case"
            ],
            "socialanxiety": [
                "social anxiety", "social fear", "embarrassed", "judged", "awkward",
                "avoid people", "social situations", "public speaking", "blushing",
                "self-conscious", "humiliated", "rejection", "social phobia"
            ],
            "adhd": [
                "can't focus", "distracted", "hyperactive", "impulsive", "forgetful",
                "disorganized", "procrastinate", "restless", "fidgety", "scattered",
                "attention", "concentrate", "mind racing", "jumping thoughts"
            ],
            "ptsd": [
                "trauma", "flashbacks", "nightmares", "triggered", "avoidance",
                "hypervigilant", "startled", "intrusive thoughts", "dissociation",
                "numb", "detached", "survivor guilt", "reliving"
            ],
            "addiction": [
                "addiction", "addicted", "substance", "drugs", "alcohol", "dependency",
                "craving", "withdrawal", "relapse", "recovery", "sober", "clean",
                "using", "drinking", "high", "fix", "habit"
            ],
            "alcoholism": [
                "alcohol", "drinking", "drunk", "hangover", "liquor", "beer", "wine",
                "alcoholic", "binge drinking", "blackout", "liver", "DUI", "AA"
            ],
            "EDAnonymous": [
                "eating disorder", "anorexia", "bulimia", "binge eating", "purging",
                "body image", "fat", "skinny", "weight", "calories", "diet", "food guilt",
                "body dysmorphia", "mirror", "appearance", "ugly"
            ],
            "bpd": [
                "borderline", "unstable relationships", "identity crisis", "abandonment",
                "splitting", "black and white", "self-harm", "cutting", "emotional",
                "intense emotions", "mood swings", "impulsive"
            ],
            "bipolarreddit": [
                "bipolar", "manic", "mania", "hypomanic", "mood swings", "cycling",
                "elevated mood", "grandiose", "racing thoughts", "sleepless",
                "euphoric", "irritable", "mixed episode"
            ],
            "autism": [
                "autism", "autistic", "asperger", "sensory", "stimming", "routine",
                "social cues", "eye contact", "repetitive", "special interest",
                "meltdown", "overwhelmed by sounds", "texture"
            ],
            "schizophrenia": [
                "hallucinations", "voices", "delusions", "paranoid", "psychotic",
                "hearing things", "seeing things", "conspiracy", "thought insertion",
                "disorganized", "word salad", "catatonic"
            ],
            "healthanxiety": [
                "health anxiety", "hypochondria", "medical anxiety", "symptoms",
                "disease", "illness", "doctor", "medical tests", "body checking",
                "WebMD", "googling symptoms", "convinced I have"
            ],
            "lonely": [
                "lonely", "alone", "isolated", "no friends", "disconnected",
                "empty", "nobody cares", "social isolation", "withdrawn",
                "loneliness", "solitude", "abandoned"
            ],
            "suicidewatch": [
                "suicide", "suicidal", "kill myself", "end my life", "want to die",
                "not worth living", "better off dead", "suicide plan", "overdose",
                "hanging", "jumping", "gun", "pills", "final goodbye"
            ]
        }
        
        # Calculate scores for each category
        category_scores = {}
        total_words = len(text_lower.split())
        
        for category, keywords in keyword_patterns.items():
            matches = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer phrases more heavily
                    weight = len(keyword.split())
                    matches += weight
            
            # Normalize by text length and keyword count
            score = matches / (total_words + len(keywords)) if total_words > 0 else 0
            category_scores[category] = min(score * 10, 1.0)  # Scale and cap at 1.0
        
        # Find the highest scoring category
        if not category_scores or max(category_scores.values()) == 0:
            # Default to anxiety if no clear match (most common)
            predicted_category = "anxiety"
            confidence = 0.3
        else:
            predicted_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[predicted_category]
        
        # Boost confidence for very clear indicators
        high_confidence_keywords = {
            "suicidewatch": ["suicide", "kill myself", "want to die", "end my life"],
            "depression": ["suicidal", "hopeless", "worthless", "want to die"],
            "addiction": ["addicted", "withdrawal", "craving", "relapse"],
            "ptsd": ["flashbacks", "nightmares", "trauma", "triggered"]
        }
        
        for category, keywords in high_confidence_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if category == predicted_category:
                        confidence = min(confidence + 0.3, 0.95)
                    elif confidence < 0.5:
                        predicted_category = category
                        confidence = 0.7
        
        # Store classification
        self.store_classification(text, predicted_category, confidence, category_scores)
        
        return {
            "predicted_category": predicted_category,
            "confidence": confidence,
            "all_scores": category_scores,
            "description": self.category_descriptions.get(predicted_category, ""),
            "timestamp": datetime.now().isoformat(),
            "method": "keyword_fallback"
        }
    
    def classify_text(self, text: str) -> Dict:
        """Classify text into mental health categories"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                # Use fallback method
                if console:
                    console.print("[yellow]Using keyword-based classification (AI model not available)[/yellow]")
                else:
                    print("Using keyword-based classification (AI model not available)")
                return self.classify_text_fallback(text)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get all scores
            scores = predictions[0].tolist()
            all_scores = {self.categories[i]: scores[i] for i in range(len(scores))}
            
            # Get top prediction
            predicted_idx = torch.argmax(predictions, dim=-1).item()
            predicted_category = self.categories[predicted_idx]
            confidence = scores[predicted_idx]
            
            # Store classification
            self.store_classification(text, predicted_category, confidence, all_scores)
            
            return {
                "predicted_category": predicted_category,
                "confidence": confidence,
                "all_scores": all_scores,
                "description": self.category_descriptions.get(predicted_category, ""),
                "timestamp": datetime.now().isoformat(),
                "method": "ai_model"
            }
            
        except Exception as e:
            # Fallback to keyword method on error
            if console:
                console.print(f"[yellow]AI model error, using fallback: {e}[/yellow]")
            else:
                print(f"AI model error, using fallback: {e}")
            return self.classify_text_fallback(text)
    
    def store_classification(self, text: str, category: str, confidence: float, all_scores: Dict):
        """Store classification result in database"""
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Store classification
            conn.execute("""
                INSERT INTO classifications (timestamp, text, predicted_category, confidence, all_scores)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, text, category, confidence, json.dumps(all_scores)))
            
            # Update category stats
            conn.execute("""
                UPDATE category_stats 
                SET count = count + 1,
                    avg_confidence = (avg_confidence * (count - 1) + ?) / count,
                    last_detected = ?
                WHERE category = ?
            """, (confidence, timestamp, category))
            
            conn.commit()
    
    def get_classification_history(self, limit: int = 10) -> List[Dict]:
        """Get recent classification history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, text, predicted_category, confidence, user_feedback, notes
                FROM classifications
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "timestamp": row[0],
                    "text": row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                    "category": row[2],
                    "confidence": row[3],
                    "feedback": row[4],
                    "notes": row[5]
                })
            
            return results
    
    def get_category_statistics(self) -> Dict:
        """Get statistics for all categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT category, count, avg_confidence, last_detected
                FROM category_stats
                WHERE count > 0
                ORDER BY count DESC
            """)
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = {
                    "count": row[1],
                    "avg_confidence": row[2],
                    "last_detected": row[3],
                    "description": self.category_descriptions.get(row[0], "")
                }
            
            return stats
    
    def add_feedback(self, classification_id: int, feedback: str, notes: str = ""):
        """Add user feedback to a classification"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE classifications
                SET user_feedback = ?, notes = ?
                WHERE id = ?
            """, (feedback, notes, classification_id))
            conn.commit()

def display_classification_result(result: Dict):
    """Display classification result with rich formatting"""
    if not RICH_AVAILABLE:
        print(f"\nClassification Result:")
        print(f"Category: {result.get('predicted_category', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Description: {result.get('description', '')}")
        method = result.get('method', 'unknown')
        if method == 'keyword_fallback':
            print("Method: Keyword-based (AI model not available)")
        elif method == 'ai_model':
            print("Method: AI Model (BERT-based)")
        return
    
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return
    
    # Main result panel
    category = result['predicted_category']
    confidence = result['confidence']
    description = result['description']
    method = result.get('method', 'unknown')
    
    # Color coding based on confidence
    if confidence > 0.7:
        color = "green"
    elif confidence > 0.5:
        color = "yellow"
    else:
        color = "red"
    
    main_text = f"[bold {color}]{category}[/bold {color}]\n"
    main_text += f"Confidence: [{color}]{confidence:.1%}[/{color}]\n"
    main_text += f"[dim]{description}[/dim]\n\n"
    
    # Add method information
    if method == 'keyword_fallback':
        main_text += "[dim yellow]Method: Keyword-based classification[/dim yellow]"
    elif method == 'ai_model':
        main_text += "[dim green]Method: AI Model (BERT-based)[/dim green]"
    
    console.print(Panel(main_text, title="🧠 Mental Health Classification", border_style=color))
    
    # Top 3 scores table
    sorted_scores = sorted(result['all_scores'].items(), key=lambda x: x[1], reverse=True)[:3]
    
    table = Table(title="Top 3 Categories", show_header=True, header_style="bold blue")
    table.add_column("Category", style="cyan")
    table.add_column("Confidence", justify="right")
    table.add_column("Description", style="dim")
    
    for cat, score in sorted_scores:
        table.add_row(
            cat,
            f"{score:.1%}",
            classifier.category_descriptions.get(cat, "")[:50] + "..."
        )
    
    console.print(table)
    
    # Warning for high-risk categories
    if category in ["suicidewatch", "depression", "ptsd"] and confidence > 0.6:
        console.print(Panel(
            "[red]⚠️  High-risk category detected. Please consider seeking professional help.[/red]\n"
            "[yellow]Crisis resources:[/yellow]\n"
            "• National Suicide Prevention Lifeline: 988\n"
            "• Crisis Text Line: Text HOME to 741741\n"
            "• Emergency: 911",
            title="Important Notice",
            border_style="red"
        ))

def display_history(history: List[Dict]):
    """Display classification history"""
    if not history:
        if console:
            console.print("[yellow]No classification history found.[/yellow]")
        else:
            print("No classification history found.")
        return
    
    if not RICH_AVAILABLE:
        print("\nClassification History:")
        for i, item in enumerate(history, 1):
            print(f"{i}. {item['timestamp'][:19]} - {item['category']} ({item['confidence']:.1%})")
            print(f"   Text: {item['text']}")
        return
    
    table = Table(title="🕒 Recent Classifications", show_header=True, header_style="bold blue")
    table.add_column("Time", style="dim")
    table.add_column("Category", style="cyan")
    table.add_column("Confidence", justify="right")
    table.add_column("Text Preview", style="dim")
    table.add_column("Feedback", style="green")
    
    for item in history:
        timestamp = item['timestamp'][:19].replace('T', ' ')
        confidence_color = "green" if item['confidence'] > 0.7 else "yellow" if item['confidence'] > 0.5 else "red"
        
        table.add_row(
            timestamp,
            item['category'],
            f"[{confidence_color}]{item['confidence']:.1%}[/{confidence_color}]",
            item['text'],
            item['feedback'] or "-"
        )
    
    console.print(table)

def display_statistics(stats: Dict):
    """Display category statistics"""
    if not stats:
        if console:
            console.print("[yellow]No statistics available yet.[/yellow]")
        else:
            print("No statistics available yet.")
        return
    
    if not RICH_AVAILABLE:
        print("\nCategory Statistics:")
        for category, data in stats.items():
            avg_conf = data.get('avg_confidence', 0) or 0
            print(f"{category}: {data['count']} detections, {avg_conf:.1%} avg confidence")
        return
    
    table = Table(title="📊 Mental Health Category Statistics", show_header=True, header_style="bold blue")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Avg Confidence", justify="right")
    table.add_column("Last Detected", style="dim")
    table.add_column("Description", style="dim")
    
    for category, data in stats.items():
        avg_conf = data.get('avg_confidence', 0) or 0
        confidence_color = "green" if avg_conf > 0.7 else "yellow" if avg_conf > 0.5 else "red"
        last_detected = data.get('last_detected', '')
        if last_detected:
            last_detected = last_detected[:19].replace('T', ' ')
        else:
            last_detected = "Never"
        
        table.add_row(
            category,
            str(data.get('count', 0)),
            f"[{confidence_color}]{avg_conf:.1%}[/{confidence_color}]",
            last_detected,
            data.get('description', '')[:40] + "..." if len(data.get('description', '')) > 40 else data.get('description', '')
        )
    
    console.print(table)

def interactive_classification():
    """Interactive text classification session"""
    if console:
        console.print(Panel(
            "[bold blue]Mental Health Text Classification[/bold blue]\n\n"
            "This tool uses AI to analyze text and identify potential mental health categories.\n"
            "[yellow]Note: This is for informational purposes only and not a substitute for professional help.[/yellow]\n\n"
            "Type 'quit' to exit, 'history' to see recent classifications, or 'stats' for statistics.",
            title="🧠 AI Mental Health Classifier",
            border_style="blue"
        ))
    else:
        print("\n=== Mental Health Text Classification ===")
        print("Type 'quit' to exit, 'history' for recent classifications, or 'stats' for statistics.")
    
    while True:
        if console:
            text = Prompt.ask("\n[bold cyan]Enter text to classify[/bold cyan]")
        else:
            text = input("\nEnter text to classify: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        elif text.lower() == 'history':
            history = classifier.get_classification_history(20)
            display_history(history)
            continue
        elif text.lower() == 'stats':
            stats = classifier.get_category_statistics()
            display_statistics(stats)
            continue
        elif not text.strip():
            continue
        
        # Classify the text
        result = classifier.classify_text(text)
        display_classification_result(result)

def main():
    """Main function for the mental health classifier"""
    global classifier
    classifier = MentalHealthClassifier()
    
    if len(sys.argv) < 2:
        interactive_classification()
        return
    
    command = sys.argv[1].lower()
    
    if command == "classify":
        if len(sys.argv) < 3:
            if console:
                console.print("[red]Usage: om classify <text>[/red]")
            else:
                print("Usage: om classify <text>")
            return
        
        text = " ".join(sys.argv[2:])
        result = classifier.classify_text(text)
        display_classification_result(result)
        
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        history = classifier.get_classification_history(limit)
        display_history(history)
        
    elif command == "stats":
        stats = classifier.get_category_statistics()
        display_statistics(stats)
        
    elif command == "interactive":
        interactive_classification()
        
    elif command == "test":
        # Test with example texts
        test_texts = [
            "I feel so sad and hopeless lately, nothing seems to matter anymore",
            "I can't focus on anything, my mind keeps jumping from task to task",
            "I'm having panic attacks and my heart races in social situations",
            "I keep checking my body for signs of illness even though doctors say I'm fine"
        ]
        
        if console:
            console.print("[bold blue]Testing with example texts...[/bold blue]\n")
        else:
            print("Testing with example texts...\n")
        
        for i, text in enumerate(test_texts, 1):
            if console:
                console.print(f"[dim]Test {i}: {text}[/dim]")
            else:
                print(f"Test {i}: {text}")
            
            result = classifier.classify_text(text)
            display_classification_result(result)
            print()
    
    else:
        if console:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[yellow]Available commands: classify, history, stats, interactive, test[/yellow]")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: classify, history, stats, interactive, test")

if __name__ == "__main__":
    main()
