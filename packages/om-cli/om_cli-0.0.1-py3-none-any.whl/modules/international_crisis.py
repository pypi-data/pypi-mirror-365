#!/usr/bin/env python3
"""
International Crisis Support Module for Om Mental Health Platform
Provides country-specific crisis intervention resources with Nicky Case integration
"""

import json
import locale
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class InternationalCrisisSupport:
    def __init__(self):
        self.data_dir = Path.home() / ".om"
        self.crisis_data_file = self.data_dir / "crisis_resources.json"
        self.user_location_file = self.data_dir / "user_location.json"
        
        # Comprehensive international crisis resources
        self.crisis_resources = {
            # North America
            "US": {
                "country": "United States",
                "emergency": "911",
                "crisis_lines": [
                    {
                        "name": "988 Suicide & Crisis Lifeline",
                        "number": "988",
                        "text": "Text 'HELLO' to 741741",
                        "website": "https://988lifeline.org",
                        "available": "24/7",
                        "languages": ["English", "Spanish"]
                    },
                    {
                        "name": "Crisis Text Line",
                        "number": "Text HOME to 741741",
                        "website": "https://crisistextline.org",
                        "available": "24/7",
                        "languages": ["English", "Spanish"]
                    },
                    {
                        "name": "Trans Lifeline",
                        "number": "877-565-8860",
                        "website": "https://translifeline.org",
                        "available": "24/7",
                        "specialty": "LGBTQ+ support"
                    }
                ],
                "local_resources": [
                    "NAMI (National Alliance on Mental Illness): 1-800-950-NAMI",
                    "SAMHSA National Helpline: 1-800-662-4357"
                ]
            },
            "CA": {
                "country": "Canada",
                "emergency": "911",
                "crisis_lines": [
                    {
                        "name": "Talk Suicide Canada",
                        "number": "1-833-456-4566",
                        "text": "Text 45645",
                        "website": "https://talksuicide.ca",
                        "available": "24/7",
                        "languages": ["English", "French"]
                    },
                    {
                        "name": "Kids Help Phone",
                        "number": "1-800-668-6868",
                        "text": "Text CONNECT to 686868",
                        "website": "https://kidshelpphone.ca",
                        "available": "24/7",
                        "specialty": "Youth support"
                    }
                ]
            },
            
            # Europe
            "GB": {
                "country": "United Kingdom",
                "emergency": "999",
                "crisis_lines": [
                    {
                        "name": "Samaritans",
                        "number": "116 123",
                        "email": "jo@samaritans.org",
                        "website": "https://samaritans.org",
                        "available": "24/7",
                        "languages": ["English"]
                    },
                    {
                        "name": "SHOUT Crisis Text Line",
                        "text": "Text SHOUT to 85258",
                        "website": "https://giveusashout.org",
                        "available": "24/7"
                    }
                ]
            },
            "DE": {
                "country": "Germany",
                "emergency": "112",
                "crisis_lines": [
                    {
                        "name": "Telefonseelsorge",
                        "number": "0800 111 0 111 or 0800 111 0 222",
                        "website": "https://telefonseelsorge.de",
                        "available": "24/7",
                        "languages": ["German"]
                    },
                    {
                        "name": "Nummer gegen Kummer",
                        "number": "116 111 (children/teens)",
                        "website": "https://nummergegenkummer.de",
                        "available": "Mon-Sat 14-20, Sun 10-12"
                    }
                ]
            },
            "FR": {
                "country": "France",
                "emergency": "112",
                "crisis_lines": [
                    {
                        "name": "SOS Amitié",
                        "number": "09 72 39 40 50",
                        "website": "https://sos-amitie.com",
                        "available": "24/7",
                        "languages": ["French"]
                    },
                    {
                        "name": "Suicide Écoute",
                        "number": "01 45 39 40 00",
                        "website": "https://suicide-ecoute.fr",
                        "available": "24/7"
                    }
                ]
            },
            "NL": {
                "country": "Netherlands",
                "emergency": "112",
                "crisis_lines": [
                    {
                        "name": "113 Zelfmoordpreventie",
                        "number": "113",
                        "website": "https://113.nl",
                        "available": "24/7",
                        "languages": ["Dutch"]
                    }
                ]
            },
            
            # Asia-Pacific
            "AU": {
                "country": "Australia",
                "emergency": "000",
                "crisis_lines": [
                    {
                        "name": "Lifeline Australia",
                        "number": "13 11 14",
                        "text": "Text 0477 13 11 14",
                        "website": "https://lifeline.org.au",
                        "available": "24/7",
                        "languages": ["English"]
                    },
                    {
                        "name": "Beyond Blue",
                        "number": "1300 22 4636",
                        "website": "https://beyondblue.org.au",
                        "available": "24/7"
                    }
                ]
            },
            "NZ": {
                "country": "New Zealand",
                "emergency": "111",
                "crisis_lines": [
                    {
                        "name": "Lifeline Aotearoa",
                        "number": "0800 543 354",
                        "text": "Text 4357",
                        "website": "https://lifeline.org.nz",
                        "available": "24/7",
                        "languages": ["English", "Māori"]
                    }
                ]
            },
            "JP": {
                "country": "Japan",
                "emergency": "110 (police), 119 (medical)",
                "crisis_lines": [
                    {
                        "name": "TELL Lifeline",
                        "number": "03-5774-0992",
                        "website": "https://telljp.com",
                        "available": "9:00-23:00",
                        "languages": ["English", "Japanese"]
                    },
                    {
                        "name": "Inochi no Denwa",
                        "number": "0570-783-556",
                        "available": "24/7",
                        "languages": ["Japanese"]
                    }
                ]
            },
            
            # International/Multi-country
            "INTERNATIONAL": {
                "country": "International Resources",
                "crisis_lines": [
                    {
                        "name": "International Association for Suicide Prevention",
                        "website": "https://iasp.info/resources/Crisis_Centres",
                        "description": "Global directory of crisis centers"
                    },
                    {
                        "name": "Befrienders Worldwide",
                        "website": "https://befrienders.org",
                        "description": "Global network of crisis support"
                    }
                ]
            }
        }
        
        self.ensure_data_directory()
        self.load_user_location()

    def ensure_data_directory(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(exist_ok=True)

    def detect_country(self):
        """Detect user's country from system locale"""
        try:
            # Try to get country from locale
            loc = locale.getdefaultlocale()[0]
            if loc:
                if '_' in loc:
                    country_code = loc.split('_')[1]
                    return country_code.upper()
        except:
            pass
        
        # Fallback detection methods
        try:
            # Try to detect from timezone (basic approach)
            import time
            tz = time.tzname[0]
            timezone_country_map = {
                'EST': 'US', 'PST': 'US', 'MST': 'US', 'CST': 'US',
                'GMT': 'GB', 'BST': 'GB',
                'CET': 'DE', 'CEST': 'DE',
                'JST': 'JP',
                'AEST': 'AU', 'AEDT': 'AU'
            }
            if tz in timezone_country_map:
                return timezone_country_map[tz]
        except:
            pass
        
        return None

    def load_user_location(self):
        """Load user's saved location preference"""
        try:
            if self.user_location_file.exists():
                with open(self.user_location_file, 'r') as f:
                    data = json.load(f)
                    self.user_country = data.get('country_code')
            else:
                self.user_country = self.detect_country()
                self.save_user_location()
        except:
            self.user_country = None

    def save_user_location(self):
        """Save user's location preference"""
        try:
            data = {
                'country_code': self.user_country,
                'last_updated': datetime.now().isoformat(),
                'auto_detected': True
            }
            with open(self.user_location_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def set_user_country(self, country_code):
        """Manually set user's country"""
        country_code = country_code.upper()
        if country_code in self.crisis_resources:
            self.user_country = country_code
            self.save_user_location()
            return True
        return False

    def get_crisis_resources(self, country_code=None):
        """Get crisis resources for specific country"""
        if not country_code:
            country_code = self.user_country
        
        if not country_code or country_code not in self.crisis_resources:
            # Return international resources as fallback
            return self.crisis_resources.get('INTERNATIONAL', {})
        
        return self.crisis_resources[country_code]

    def display_crisis_help(self, country_code=None):
        """Display crisis help with Nicky Case integration"""
        resources = self.get_crisis_resources(country_code)
        
        if not resources:
            print("🆘 CRISIS SUPPORT - INTERNATIONAL RESOURCES")
            print("\nIf you're in immediate danger, contact your local emergency services.")
            print("\n🌍 International Crisis Resources:")
            print("• International Association for Suicide Prevention: https://iasp.info/resources/Crisis_Centres")
            print("• Befrienders Worldwide: https://befrienders.org")
            return

        country_name = resources.get('country', 'Your Location')
        emergency = resources.get('emergency', '911/112')
        
        print(f"🆘 CRISIS SUPPORT - {country_name.upper()}")
        print("=" * 50)
        
        # Nicky Case integration - "Fear as Friend" approach
        print("\n🐺 Remember: Your fear is trying to protect you.")
        print("It's okay to reach out. You're not alone in this.")
        print("\n" + "─" * 50)
        
        print(f"\n🚨 EMERGENCY: {emergency}")
        print("Call immediately if you're in immediate physical danger.")
        
        if 'crisis_lines' in resources:
            print(f"\n📞 CRISIS SUPPORT LINES:")
            for line in resources['crisis_lines']:
                print(f"\n• {line['name']}")
                if 'number' in line:
                    print(f"  📞 {line['number']}")
                if 'text' in line:
                    print(f"  💬 {line['text']}")
                if 'email' in line:
                    print(f"  📧 {line['email']}")
                if 'website' in line:
                    print(f"  🌐 {line['website']}")
                if 'available' in line:
                    print(f"  ⏰ Available: {line['available']}")
                if 'languages' in line:
                    print(f"  🗣️  Languages: {', '.join(line['languages'])}")
                if 'specialty' in line:
                    print(f"  ⭐ Specialty: {line['specialty']}")
        
        if 'local_resources' in resources:
            print(f"\n🏥 LOCAL RESOURCES:")
            for resource in resources['local_resources']:
                print(f"• {resource}")
        
        # Nicky Case wisdom integration
        print("\n" + "─" * 50)
        print("🧘 Nicky Case Wisdom:")
        print("• Your feelings are valid and temporary")
        print("• Reaching out is a sign of strength, not weakness")
        print("• You have survived difficult times before")
        print("• There are people who want to help you")
        print("• Tomorrow can be different from today")
        
        print(f"\n💝 You matter. Your life has value.")
        print("These resources are here because people care about you.")

    def list_available_countries(self):
        """List all available countries"""
        print("🌍 Available Countries for Crisis Support:")
        print("=" * 45)
        
        for code, data in self.crisis_resources.items():
            if code != 'INTERNATIONAL':
                country_name = data.get('country', code)
                crisis_count = len(data.get('crisis_lines', []))
                print(f"• {code}: {country_name} ({crisis_count} crisis lines)")
        
        print(f"\n• INTERNATIONAL: Global resources")
        print(f"\nCurrent setting: {self.user_country or 'Not set'}")
        print(f"\nTo change: om crisis --set-country [CODE]")

    def interactive_country_setup(self):
        """Interactive country setup"""
        print("🌍 Crisis Support Country Setup")
        print("=" * 35)
        
        detected = self.detect_country()
        if detected and detected in self.crisis_resources:
            print(f"\n🔍 Detected country: {self.crisis_resources[detected]['country']} ({detected})")
            response = input("Is this correct? (y/n): ").lower().strip()
            if response in ['y', 'yes', '']:
                self.set_user_country(detected)
                print(f"✅ Country set to {detected}")
                return
        
        print("\n📋 Available countries:")
        countries = [(code, data['country']) for code, data in self.crisis_resources.items() 
                    if code != 'INTERNATIONAL']
        countries.sort(key=lambda x: x[1])
        
        for i, (code, name) in enumerate(countries, 1):
            print(f"{i:2d}. {name} ({code})")
        
        try:
            choice = input(f"\nSelect country (1-{len(countries)}) or enter country code: ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(countries):
                    code = countries[idx][0]
                    self.set_user_country(code)
                    print(f"✅ Country set to {code}")
                else:
                    print("❌ Invalid selection")
            else:
                code = choice.upper()
                if self.set_user_country(code):
                    print(f"✅ Country set to {code}")
                else:
                    print("❌ Country code not found")
        except KeyboardInterrupt:
            print("\n\nSetup cancelled.")
        except:
            print("❌ Invalid input")

    def add_custom_resource(self, name, number, description=""):
        """Add custom local crisis resource"""
        try:
            custom_file = self.data_dir / "custom_crisis_resources.json"
            custom_resources = []
            
            if custom_file.exists():
                with open(custom_file, 'r') as f:
                    custom_resources = json.load(f)
            
            custom_resources.append({
                'name': name,
                'number': number,
                'description': description,
                'added_date': datetime.now().isoformat()
            })
            
            with open(custom_file, 'w') as f:
                json.dump(custom_resources, f, indent=2)
            
            print(f"✅ Added custom crisis resource: {name}")
            return True
        except Exception as e:
            print(f"❌ Error adding custom resource: {e}")
            return False

    def show_custom_resources(self):
        """Show user's custom crisis resources"""
        try:
            custom_file = self.data_dir / "custom_crisis_resources.json"
            if not custom_file.exists():
                print("No custom crisis resources added yet.")
                print("Add one with: om crisis --add-custom")
                return
            
            with open(custom_file, 'r') as f:
                resources = json.load(f)
            
            if not resources:
                print("No custom crisis resources found.")
                return
            
            print("🏥 Your Custom Crisis Resources:")
            print("=" * 35)
            
            for resource in resources:
                print(f"\n• {resource['name']}")
                print(f"  📞 {resource['number']}")
                if resource.get('description'):
                    print(f"  📝 {resource['description']}")
                
        except Exception as e:
            print(f"❌ Error loading custom resources: {e}")

def main():
    """Main function for testing"""
    crisis = InternationalCrisisSupport()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--setup":
            crisis.interactive_country_setup()
        elif command == "--list":
            crisis.list_available_countries()
        elif command == "--set-country" and len(sys.argv) > 2:
            country = sys.argv[2].upper()
            if crisis.set_user_country(country):
                print(f"✅ Country set to {country}")
            else:
                print(f"❌ Country {country} not supported")
        elif command == "--add-custom":
            name = input("Resource name: ")
            number = input("Phone number: ")
            description = input("Description (optional): ")
            crisis.add_custom_resource(name, number, description)
        elif command == "--custom":
            crisis.show_custom_resources()
        elif command == "--country" and len(sys.argv) > 2:
            country = sys.argv[2].upper()
            crisis.display_crisis_help(country)
        else:
            crisis.display_crisis_help()
    else:
        crisis.display_crisis_help()

if __name__ == "__main__":
    main()
