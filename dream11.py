import json
import os
import re
import time
import crewai
from crewai import Agent, Crew, Task, Process, LLM
from google import genai
from crewai_tools import SerperDevTool
import datetime
import warnings
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import traceback
from google.cloud.firestore_v1 import SERVER_TIMESTAMP


# 2. FIREBASE INITIALIZATION - Add after the existing imports section
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("./dr11-5b3c9-firebase-adminsdk-fbsvc-cca9a29cf8.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase initialized")
        return db
    except Exception as e:
        print(f"❌ Firebase initialization failed:\n{traceback.format_exc()}")
        return None

warnings.filterwarnings("ignore")

os.environ['SERPER_API_KEY'] = " " # Enter your Serper API Key
os.environ["GEMINI_API_KEY"] = " " # Enter your Gemini API Key
llm = LLM(model="gemini/gemini-2.0-flash-lite")

search = SerperDevTool(description="Search for the IPL 2025 match schedule and the records of their teams players that are playing IPL 2025 ", n_results=30)

# IPL 2025 Full Squad Data - Cleaned and Organized
IPL_SQUADS = {
    "Mumbai Indians": [
        "Hardik Pandya", "Jasprit Bumrah", "Rohit Sharma", "Suryakumar Yadav", "Tilak Varma", 
        "Trent Boult", "Naman Dhir", "Robin Minz", "Karn Sharma", "Ryan Rickelton", 
        "Deepak Chahar", "Will Jacks", "Allah Ghazanfar", "Mitchell Santner", "Reece Topley", 
        "Raj Angad Bawa", "Shrijith Krishnan", "Ashwani Kumar", "Venkata Satyanarayana Penmetsa", 
        "Bevon Jacobs", "Arjun Tendulkar", "Lizaad Williams", "Vignesh Puthur"
    ],
    "Royal Challengers Bengaluru": [
        "Virat Kohli", "Rajat Patidar", "Yash Dayal", "Phil Salt", "Jitesh Sharma", 
        "Liam Livingstone", "Josh Hazlewood", "Rasikh Dar", "Suyash Sharma", "Bhuvneshwar Kumar", 
        "Krunal Pandya", "Swapnil Singh", "Tim David", "Romario Shepherd", "Nuwan Thushara", 
        "Jacob Bethell", "Manoj Bhandage", "Devdutt Padikkal", "Swastik Chhikara", "Lungi Ngidi", 
        "Abhinandan Singh", "Mohit Rathee"
    ],
    "Sunrisers Hyderabad": [
        "Pat Cummins", "Travis Head", "Abhishek Sharma", "Heinrich Klaasen", "Nitish Kumar Reddy", 
        "Ishan Kishan", "Mohammed Shami", "Harshal Patel", "Rahul Chahar", "Adam Zampa", 
        "Abhinav Manohar", "Simarjeet Singh", "Atharva Taide", "Brydon Carse", "Jaydev Unadkat", 
        "Kamindu Mendis", "Zeeshan Ansari", "Aniket Verma", "Eshan Malinga", "Sachin Baby"
    ],
    "Chennai Super Kings": [
        "MS Dhoni", "Ayush Mathre", "Ravindra Jadeja", "Shivam Dube", "Matheesha Pathirana", 
        "Noor Ahmad", "Ravichandran Ashwin", "Devon Conway", "Khaleel Ahmed", "Rachin Ravindra", 
        "Rahul Tripathi", "Vijay Shankar", "Sam Curran", "Shaik Rasheed", "Anshul Kamboj", 
        "Mukesh Choudhary", "Deepak Hooda", "Gurjapneet Singh", "Nathan Ellis", "Jamie Overton", 
        "Kamlesh Nagarkoti", "Ramakrishnan Ghosh", "Shreyas Gopal", "Vansh Bedi", "Andre Siddarth"
    ],
    "Punjab Kings": [
        "Shreyas Iyer", "Yuzvendra Chahal", "Arshdeep Singh", "Marcus Stoinis", "Glenn Maxwell", 
        "Shashank Singh", "Prabhsimran Singh", "Harpreet Brar", "Vijaykumar Vyshak", "Yash Thakur", 
        "Marco Jansen", "Josh Inglis", "Lockie Ferguson", "Azmatullah Omarzai", "Harnoor Pannu", 
        "Kuldeep Sen", "Priyansh Arya", "Aaron Hardie", "Musheer Khan", "Suryansh Shedge", 
        "Xavier Bartlett", "Pyla Avinash", "Pravin Dubey", "Nehal Wadhera"
    ],
    "Rajasthan Royals": [
        "Sanju Samson", "Yashasvi Jaiswal", "Riyan Parag", "Dhruv Jurel", "Shimron Hetmyer", 
        "Sandeep Sharma", "Jofra Archer", "Wanindu Hasaranga", "Maheesh Theekshana", "Akash Madhwal", 
        "Kumar Kartikeya Singh", "Nitish Rana", "Tushar Deshpande", "Shubham Dubey", "Yudhvir Charak", 
        "Fazalhaq Farooqi", "Vaibhav Suryavanshi", "Kwena Maphaka", "Kunal Rathore", "Ashok Sharma"
    ],
    "Delhi Capitals": [
        "KL Rahul", "Harry Brook", "Jake Fraser-McGurk", "Karun Nair", "Abishek Porel", 
        "Tristan Stubbs", "Axar Patel", "Kuldeep Yadav", "T Natarajan", "Mitchell Starc", 
        "Sameer Rizvi", "Ashutosh Sharma", "Mohit Sharma", "Mukesh Kumar", "Faf du Plessis", 
        "Dushmantha Chameera", "Vipraj Nigam", "Darshan Nalkande", "Donovan Ferreira", "Ajay Mandal", 
        "Manvanth Kumar L", "Tripurana Vijay", "Madhav Tiwari"
    ],
    "Gujarat Titans": [
        "Shubman Gill", "Jos Buttler", "B Sai Sudharsan", "Shahrukh Khan", "Kagiso Rabada", 
        "Mohammed Siraj", "Prasidh Krishna", "Rahul Tewatia", "Rashid Khan", "Nishant Sindhu", 
        "Mahipal Lomror", "Kumar Kushagra", "Anuj Rawat", "Manav Suthar", "Washington Sundar", 
        "Sherfane Rutherford", "Gerald Coetzee", "R Sai Kishore", "Gurnoor Singh Brar", 
        "Mohd Arshad Khan", "Jayant Yadav", "Ishant Sharma", "Glenn Phillips", "Karim Janat", "Kulwant Khejroliya"
    ],
    "Lucknow Super Giants": [
        "Rishabh Pant", "Nicholas Pooran", "David Miller", "Aiden Markram", "Mitchell Marsh", 
        "Avesh Khan", "Mayank Yadav", "Mohsin Khan", "Ravi Bishnoi", "Abdul Samad", 
        "Aryan Juyal", "Akash Deep", "Himmat Singh", "M Siddharth", "Digvesh Singh", 
        "Akash Singh", "Shamar Joseph", "Prince Yadav", "Yuvraj Chaudhary", "Rajvardhan Hangargekar", 
        "Arshin Kulkarni", "Matthew Breetzke"
    ],
    "Kolkata Knight Riders": [
        "Ajinkya Rahane", "Rinku Singh", "Quinton de Kock", "Rahmanullah Gurbaz", "Angkrish Raghuvanshi", 
        "Venkatesh Iyer", "Ramandeep Singh", "Andre Russell", "Anrich Nortje", "Harshit Rana", 
        "Sunil Narine", "Varun Chakaravarthy", "Vaibhav Arora", "Mayank Markande", "Rovman Powell", 
        "Spencer Johnson", "Manish Pandey", "Luvnith Sisodia"
    ]
}

# IPL 2025 Full Fixture List
ipl_fixtures = [
    {"match_no": 30, "date": "14-04-2025", "day": "Mon", "time": "7:30PM", "home": "Lucknow Super Giants", "away": "Chennai Super Kings", "venue": "Lucknow"},
    {"match_no": 31, "date": "15-04-2025", "day": "Tue", "time": "7:30PM", "home": "Punjab Kings", "away": "Kolkata Knight Riders", "venue": "Chandigarh"},
    {"match_no": 32, "date": "16-04-2025", "day": "Wed", "time": "7:30PM", "home": "Delhi Capitals", "away": "Rajasthan Royals", "venue": "Delhi"},
    {"match_no": 33, "date": "17-04-2025", "day": "Thu", "time": "7:30PM", "home": "Mumbai Indians", "away": "Sunrisers Hyderabad", "venue": "Mumbai"},
    {"match_no": 34, "date": "18-04-2025", "day": "Fri", "time": "7:30PM", "home": "Royal Challengers Bengaluru", "away": "Punjab Kings", "venue": "Bengaluru"},
    {"match_no": 35, "date": "19-04-2025", "day": "Sat", "time": "3:30PM", "home": "Gujarat Titans", "away": "Delhi Capitals", "venue": "Ahmedabad"},
    {"match_no": 36, "date": "19-04-2025", "day": "Sat", "time": "7:30PM", "home": "Rajasthan Royals", "away": "Lucknow Super Giants", "venue": "Jaipur"},
    {"match_no": 37, "date": "20-04-2025", "day": "Sun", "time": "3:30PM", "home": "Punjab Kings", "away": "Royal Challengers Bengaluru", "venue": "Chandigarh"},
    {"match_no": 38, "date": "20-04-2025", "day": "Sun", "time": "7:30PM", "home": "Mumbai Indians", "away": "Chennai Super Kings", "venue": "Mumbai"},
    {"match_no": 39, "date": "21-04-2025", "day": "Mon", "time": "7:30PM", "home": "Kolkata Knight Riders", "away": "Gujarat Titans", "venue": "Kolkata"},
    {"match_no": 40, "date": "22-04-2025", "day": "Tue", "time": "7:30PM", "home": "Lucknow Super Giants", "away": "Delhi Capitals", "venue": "Lucknow"},
    {"match_no": 41, "date": "23-04-2025", "day": "Wed", "time": "7:30PM", "home": "Sunrisers Hyderabad", "away": "Mumbai Indians", "venue": "Hyderabad"},
    {"match_no": 42, "date": "24-04-2025", "day": "Thu", "time": "7:30PM", "home": "Royal Challengers Bengaluru", "away": "Rajasthan Royals", "venue": "Bengaluru"},
    {"match_no": 43, "date": "25-04-2025", "day": "Fri", "time": "7:30PM", "home": "Chennai Super Kings", "away": "Sunrisers Hyderabad", "venue": "Chennai"},
    {"match_no": 44, "date": "26-04-2025", "day": "Sat", "time": "7:30PM", "home": "Kolkata Knight Riders", "away": "Punjab Kings", "venue": "Kolkata"},
    {"match_no": 45, "date": "27-04-2025", "day": "Sun", "time": "3:30PM", "home": "Mumbai Indians", "away": "Lucknow Super Giants", "venue": "Mumbai"},
    {"match_no": 46, "date": "27-04-2025", "day": "Sun", "time": "7:30PM", "home": "Delhi Capitals", "away": "Royal Challengers Bengaluru", "venue": "Delhi"},
    {"match_no": 47, "date": "28-04-2025", "day": "Mon", "time": "7:30PM", "home": "Rajasthan Royals", "away": "Gujarat Titans", "venue": "Jaipur"},
    {"match_no": 48, "date": "29-04-2025", "day": "Tue", "time": "7:30PM", "home": "Delhi Capitals", "away": "Kolkata Knight Riders", "venue": "Delhi"},
    {"match_no": 49, "date": "30-04-2025", "day": "Wed", "time": "7:30PM", "home": "Chennai Super Kings", "away": "Punjab Kings", "venue": "Chennai"},
    {"match_no": 50, "date": "01-05-2025", "day": "Thu", "time": "7:30PM", "home": "Rajasthan Royals", "away": "Mumbai Indians", "venue": "Jaipur"},
    {"match_no": 51, "date": "02-05-2025", "day": "Fri", "time": "7:30PM", "home": "Gujarat Titans", "away": "Sunrisers Hyderabad", "venue": "Ahmedabad"},
    {"match_no": 52, "date": "03-05-2025", "day": "Sat", "time": "7:30PM", "home": "Royal Challengers Bengaluru", "away": "Chennai Super Kings", "venue": "Bengaluru"},
    {"match_no": 53, "date": "04-05-2025", "day": "Sun", "time": "3:30PM", "home": "Kolkata Knight Riders", "away": "Rajasthan Royals", "venue": "Kolkata"},
    {"match_no": 54, "date": "04-05-2025", "day": "Sun", "time": "7:30PM", "home": "Punjab Kings", "away": "Lucknow Super Giants", "venue": "Dharamshala"},
    {"match_no": 55, "date": "05-05-2025", "day": "Mon", "time": "7:30PM", "home": "Sunrisers Hyderabad", "away": "Delhi Capitals", "venue": "Hyderabad"},
    {"match_no": 56, "date": "06-05-2025", "day": "Tue", "time": "7:30PM", "home": "Mumbai Indians", "away": "Gujarat Titans", "venue": "Mumbai"},
    {"match_no": 57, "date": "07-05-2025", "day": "Wed", "time": "7:30PM", "home": "Kolkata Knight Riders", "away": "Chennai Super Kings", "venue": "Kolkata"},
    {"match_no": 60, "date": "17-05-2025", "day": "Sat", "time": "7:30PM", "home": "Royal Challengers Bengaluru", "away": "Kolkata Knight Riders", "venue": "Bengaluru"},
    {"match_no": 61, "date": "18-05-2025", "day": "Sun", "time": "3:30PM", "home": "Rajasthan Royals", "away": "Punjab Kings", "venue": "Jaipur"},
    {"match_no": 62, "date": "18-05-2025", "day": "Sun", "time": "7:30PM", "home": "Delhi Capitals", "away": "Gujarat Titans", "venue": "Delhi"},
    {"match_no": 63, "date": "19-05-2025", "day": "Mon", "time": "7:30PM", "home": "Lucknow Super Giants", "away": "Sunrisers Hyderabad", "venue": "Lucknow"},
    {"match_no": 64, "date": "20-05-2025", "day": "Tue", "time": "7:30PM", "home": "Chennai Super Kings", "away": "Rajasthan Royals", "venue": "Delhi"},
    {"match_no": 65, "date": "21-05-2025", "day": "Wed", "time": "7:30PM", "home": "Mumbai Indians", "away": "Delhi Capitals", "venue": "Mumbai"},
    {"match_no": 66, "date": "22-05-2025", "day": "Thu", "time": "7:30PM", "home": "Gujarat Titans", "away": "Lucknow Super Giants", "venue": "Ahmedabad"},
    {"match_no": 67, "date": "23-05-2025", "day": "Fri", "time": "7:30PM", "home": "Royal Challengers Bengaluru", "away": "Sunrisers Hyderabad", "venue": "Bengaluru"},
    {"match_no": 68, "date": "24-05-2025", "day": "Sat", "time": "7:30PM", "home": "Punjab Kings", "away": "Delhi Capitals", "venue": "Jaipur"},
    {"match_no": 69, "date": "25-05-2025", "day": "Sun", "time": "3:30PM", "home": "Gujarat Titans", "away": "Chennai Super Kings", "venue": "Ahmedabad"},
    {"match_no": 70, "date": "25-05-2025", "day": "Sun", "time": "7:30PM", "home": "Sunrisers Hyderabad", "away": "Kolkata Knight Riders", "venue": "Delhi"},
    {"match_no": 71, "date": "26-05-2025", "day": "Mon", "time": "7:30PM", "home": "Punjab Kings", "away": "Mumbai Indians", "venue": "Jaipur"},
    {"match_no": 72, "date": "27-05-2025", "day": "Tue", "time": "7:30PM", "home": "Lucknow Super Giants", "away": "Royal Challengers Bengaluru", "venue": "Lucknow"}
]

match_fix_two = {
    73: "29-05-2025",
    74: "30-05-2025",
    75: "01-06-2025",
    76: "03-06-2025"
}

class FirebaseMemoryManager:
    """Firebase-based persistent storage of Dream11 team selections"""

    def __init__(self, collection_name="dream11_teams"):
        self.db = initialize_firebase()
        self.collection_name = collection_name

        if not self.db:
            print("⚠️ Firebase not initialized, falling back to local storage")
            self.memory_file = "dream11_memory.json"
            self.memory = self.load_local_memory()

    def load_local_memory(self):
        """Fallback local memory loader"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Failed to load local memory: {str(e)}")
                return {}
        return {}

    def get_match_key(self, match_number, home_team, away_team):
        """Generate unique key for match"""
        return f"{match_number}_{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}"

    def has_team(self, match_key):
        """Check if team exists for this match"""
        if not self.db:
            return match_key in self.memory
        try:
            doc_ref = self.db.collection(self.collection_name).document(match_key)
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            print(f"❌ Error checking team existence:\n{traceback.format_exc()}")
            return False

    def get_team(self, match_key):
        """Retrieve stored team"""
        if not self.db:
            return self.memory.get(match_key)
        try:
            doc_ref = self.db.collection(self.collection_name).document(match_key)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"❌ Error retrieving team:\n{traceback.format_exc()}")
            return None

    def store_team(self, match_key, team_data, is_validated=False):
        """Store team data only if validation passed"""
        if not is_validated:
            print("⚠️ Team not stored - validation failed")
            return False

        team_data['validated'] = True
        team_data['stored_at'] = SERVER_TIMESTAMP  # Firestore-friendly timestamp

        if not self.db:
            # Fallback to local storage
            self.memory[match_key] = team_data
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            print(f"💾 Team stored locally (Firebase unavailable)")
            return True

        try:
            doc_ref = self.db.collection(self.collection_name).document(match_key)
            doc_ref.set(team_data)
            print(f"🔥 Team stored in Firebase successfully")
            return True
        except Exception as e:
            print(f"❌ Error storing team in Firebase:\n{traceback.format_exc()}")
            return False

class PlayerValidator:
    """Validates if selected players exist in official squads"""

    def __init__(self, squads):
        self.squads = squads

    def normalize_name(self, name):
        """Normalize player name for comparison"""
        return re.sub(r'[^\w\s]', '', name.strip().lower())

    def find_player_team(self, player_name):
        """Find which team a player belongs to using partial match"""
        normalized_input = self.normalize_name(player_name)

        for team, players in self.squads.items():
            for squad_player in players:
                normalized_squad_player = self.normalize_name(squad_player)
                # Check for full or partial match
                if normalized_input in normalized_squad_player or normalized_squad_player in normalized_input:
                    return team
        return None

    def validate_team_selection(self, selected_players, expected_teams):
        """Validate if all players belong to expected teams"""
        validation_results = {
            "valid": True,
            "invalid_players": [],
            "team_distribution": {}
        }

        for player in selected_players:
            player_team = self.find_player_team(player)
            if player_team is None:
                validation_results["valid"] = False
                validation_results["invalid_players"].append(player)
            elif player_team not in expected_teams:
                validation_results["valid"] = False
                validation_results["invalid_players"].append(f"{player} (belongs to {player_team}, not in {expected_teams})")
            else:
                validation_results["team_distribution"].setdefault(player_team, 0)
                validation_results["team_distribution"][player_team] += 1

        return validation_results

class WebScraper:
    def __init__(self, llm, match_fix_two):
        self.search_tool = SerperDevTool(description="Search for IPL 2025 match details", n_results=5)
        self.llm = llm
        self.match_fix_two = match_fix_two  # Dictionary: match_number -> date (e.g., "28-05-2025")

    def search_fixtures_by_date_task(self, match_number):
        """Create a CrewAI Task for searching match fixtures on a given date"""
        match_date = self.match_fix_two.get(match_number)
        if not match_date:
            raise ValueError(f"No date found for match number {match_number} in match_fix_two")
        query = f"IPL 2025 fixtures on {match_date}"
        
        search_agent = Agent(
            role="Fixture Searcher",
            goal=f"Find all IPL 2025 fixtures on {match_date}",
            backstory="You specialize in looking up IPL fixtures scheduled on specific dates.",
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True
        )
        return Task(
            name=f"Search Fixtures for {match_date}",
            description=f"Search web for all IPL fixtures on {match_date}. Return team names, match number, and venue.",
            expected_output="List of matches and team names playing on that date.",
            agent=search_agent
        )

    def extract_match_details(self, match_number):
        """Search using date from match_fix_two and extract match details"""
        match_date = self.match_fix_two.get(match_number)
        if not match_date:
            raise ValueError(f"No date found for match number {match_number} in match_fix_two")

        # 1. Create the search task using the date
        fixture_task = self.search_fixtures_by_date_task(match_number)

        # 2. Create the scraping agent
        scraper_agent = Agent(
            role="IPL Fixture Scraper",
            goal=f"Extract all match details from fixtures on {match_date}",
            backstory="You are an expert in extracting cricket fixture details from search results.",
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True
        )

        # 3. Define the extraction task
        scrape_task = Task(
            name=f"Extract Fixtures for {match_date}",
            description=f"""
            From the search results about IPL 2025 fixtures on {match_date}, extract the match that corresponds to Match {match_number}.
            Return the following in JSON:
            - match_no
            - date (DD-MM-YYYY)
            - day (3-letter weekday)
            - time (e.g., '7:30PM')
            - home (home team)
            - away (away team)
            - venue (match venue)
            """,
            expected_output="Valid JSON object with all above fields.",
            agent=scraper_agent,
            context=[fixture_task]
        )

        # 4. Run tasks using Crew
        crew = Crew(
            agents=[scraper_agent],
            tasks=[fixture_task, scrape_task],
            process=Process.sequential,
            verbose=True
        )
        result = crew.kickoff()

        # 5. Extract the output string
        result_str = getattr(result, "output", None) or getattr(result, "result", None) or str(result)

        # 6. Extract JSON
        match_details = {}
        json_match = re.search(r'({\s*"match_no".*?})', result_str, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            match_details = json.loads(json_str)
        else:
            # Optional fallback LLM extraction
            extract_agent = Agent(
                role="Data Extractor",
                goal="Extract structured match data from unstructured text",
                backstory="You parse textual match summaries into JSON.",
                llm=self.llm,
                verbose=True
            )
            extract_task = Task(
                name="Fallback JSON Extractor",
                description=f"""
                Extract IPL match details for match number {match_number} from the following text:
                {result_str}
                Return only valid JSON with:
                match_no, date, day, time, home, away, venue
                """,
                agent=extract_agent
            )
            json_result = extract_task.execute()
            json_match = re.search(r'({\s*"match_no".*?})', json_result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                match_details = json.loads(json_str)

        match_details["match_no"] = match_number
        return match_details

class TeamAnalyzer:
    """Analyzes existing Dream11 teams and suggests optimizations"""
    
    def __init__(self, llm, squads):
        self.llm = llm
        self.squads = squads
        self.search_tool = SerperDevTool(description="Search for latest IPL player updates, injuries, and form", n_results=20)
    
    def analyze_stored_team(self, team_data, match_details):
        """Analyze stored team and suggest improvements"""
        
        match_number = team_data.get('match_number')
        home_team = team_data.get('home_team')
        away_team = team_data.get('away_team')
        match_date = team_data.get('date')
        
        print(f"🔍 Analyzing stored team for Match {match_number}: {home_team} vs {away_team}")
        
        # Extract current team from stored data
        current_team_df = None
        if 'dataframe' in team_data and team_data['dataframe']:
            try:
                current_team_df = pd.DataFrame(team_data['dataframe'])
            except:
                print("⚠️  Could not load stored dataframe")
                return None
        
        if current_team_df is None:
            print("❌ No valid team data found for analysis")
            return None
        
        # Create analysis agents
        current_situation_agent = Agent(
            role="Current Situation Analyst",
            goal=f"Get latest updates for Match {match_number}: {home_team} vs {away_team}",
            backstory="You specialize in getting real-time cricket updates including player injuries, team changes, pitch conditions, and toss results.",
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True,
        )
        
        team_optimizer_agent = Agent(
            role="Dream11 Team Optimizer",
            goal="Analyze existing Dream11 team and suggest strategic improvements",
            backstory="You are an expert Dream11 analyst who reviews existing teams and suggests tactical changes based on current match conditions.",
            llm=self.llm,
            verbose=True,
        )
        
        # Tasks
        current_situation_task = Task(
            name="Get Latest Match Updates",
            description=f"""Get the most current information for Match {match_number} on {match_date}:
            1. Latest pitch report and weather conditions
            2. Any player injuries or team changes
            3. Toss result and decision (if available)
            4. Recent form of key players from both teams
            5. Any last-minute team news or updates
            
            Focus on teams: {home_team} and {away_team}""",
            expected_output="""Current match situation report including:
            - Live pitch and weather conditions
            - Player availability and injury updates  
            - Toss details (if available)
            - Recent player form updates
            - Any breaking team news""",
            agent=current_situation_agent,
        )
        
        team_analysis_task = Task(
            name="Analyze Current Dream11 Team",
            description=f"""Analyze the existing Dream11 team and provide insights:
            
            Current Team:
            {current_team_df.to_string() if current_team_df is not None else "No team data"}
            
            Available squads:
            {home_team}: {', '.join(self.squads.get(home_team, []))}
            {away_team}: {', '.join(self.squads.get(away_team, []))}
            
            Provide comprehensive analysis:
            1. Team Strengths: What's working well in current selection
            2. Potential Risks: Players who might underperform
            3. Captaincy Assessment: Current C/VC choices evaluation
            4. Match Conditions Impact: How current conditions affect team
            5. Alternative Suggestions: Better player options if any
            
            Focus on analysis rather than changes. Only suggest critical changes if absolutely necessary.
            
            IMPORTANT: If suggesting changes, include this CSV format:
            
            ## OPTIMIZED_CSV_DATA
            Action,PlayerOut,PlayerIn,Team,Role,Reason
            REPLACE,OldPlayer,NewPlayer,TEAM,ROLE,Critical reason only
            ## END_CSV_DATA""",
            expected_output="""Detailed team analysis focusing on:
            - Current team evaluation and strengths
            - Risk assessment of key players  
            - Captaincy choice analysis
            - Impact of match conditions
            - Only critical change suggestions (if any)""",
            agent=team_optimizer_agent,
            context=[current_situation_task],
        )
        
        # Create and run analysis crew
        analysis_crew = Crew(
            agents=[current_situation_agent, team_optimizer_agent],
            tasks=[current_situation_task, team_analysis_task],
            process=Process.sequential,
            verbose=True,
        )
        
        try:
            analysis_result = analysis_crew.kickoff()
            print("✅ Team analysis completed!")
            
            # Extract optimization suggestions
            result_text = getattr(analysis_result, 'raw', str(analysis_result))
            
            # Parse optimization CSV if available
            optimization_df = self._parse_optimization_csv(result_text)
            
            analysis_data = {
                'match_number': match_number,
                'analysis_date': datetime.now().isoformat(),
                'analysis_result': result_text,
                'optimization_suggestions': optimization_df.to_dict() if optimization_df is not None else None,
                'original_team': current_team_df.to_dict()
            }
            
            return analysis_data, optimization_df
            
        except Exception as e:
            print(f"❌ Error during team analysis: {str(e)}")
            return None, None
    
    def _parse_optimization_csv(self, text):
        """Parse optimization CSV from analysis result"""
        try:
            pattern = r'## OPTIMIZED_CSV_DATA\n(.*?)## END_CSV_DATA'
            match = re.search(pattern, str(text), re.DOTALL)
            
            if not match:
                print("ℹ️  No optimization CSV found")
                return None
            
            csv_text = match.group(1).strip()
            from io import StringIO
            df = pd.read_csv(StringIO(csv_text))
            return df
            
        except Exception as e:
            print(f"⚠️  Could not parse optimization CSV: {str(e)}")
            return None
    
    def apply_optimizations(self, original_team_df, optimization_df):
        """Apply suggested optimizations to create new team"""
        if optimization_df is None:
            return original_team_df
        
        optimized_team = original_team_df.copy()
        
        for _, suggestion in optimization_df.iterrows():
            action = suggestion.get('Action', '').upper()
            
            if action == 'REPLACE':
                player_out = suggestion.get('PlayerOut')
                player_in = suggestion.get('PlayerIn')
                
                if player_out and player_in:
                    # Replace player in dataframe
                    mask = optimized_team['PlayerName'] == player_out
                    if mask.any():
                        optimized_team.loc[mask, 'PlayerName'] = player_in
                        optimized_team.loc[mask, 'Team'] = suggestion.get('Team', optimized_team.loc[mask, 'Team'].iloc[0])
                        optimized_team.loc[mask, 'Role'] = suggestion.get('Role', optimized_team.loc[mask, 'Role'].iloc[0])
                        print(f"🔄 Replaced {player_out} with {player_in}")
            
            elif action == 'CAPTAIN':
                new_captain = suggestion.get('PlayerIn')
                if new_captain:
                    # Reset all captaincy
                    optimized_team['C/VC/None'] = optimized_team['C/VC/None'].replace(['C', 'VC'], 'None')
                    # Set new captain
                    mask = optimized_team['PlayerName'] == new_captain
                    if mask.any():
                        optimized_team.loc[mask, 'C/VC/None'] = 'C'
                        print(f"👑 New Captain: {new_captain}")
        
        return optimized_team

def get_match_details(match_number):
    """Get match details either from fixtures or by web scraping"""
    if match_number <= 72:
        match = next((m for m in ipl_fixtures if m["match_no"] == match_number), None)
        if match:
            return match
        else:
            print(f"⚠ Match {match_number} not found in fixtures list despite being <= 72")
            return WebScraper(llm, match_fix_two).extract_match_details(match_number)
    else:
        print(f"🔍 Match {match_number} is beyond fixture list. Using web scraping to find details...")
        return WebScraper(llm, match_fix_two).extract_match_details(match_number)

def stringify_keys(d):
    if isinstance(d, dict):
        return {str(k): stringify_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [stringify_keys(i) for i in d]
    else:
        return d


def create_dream11_team(match, memory_manager, validator):
    """Create Dream11 team using AI agents with validation"""
    
    match_number = match["match_no"]
    match_date = match["date"]
    match_day = match["day"]
    match_time = match["time"]
    home_team = match["home"]
    away_team = match["away"]
    venue = match["venue"]
    
    # Check if we have a stored team
    match_key = memory_manager.get_match_key(match_number, home_team, away_team)
    if memory_manager.has_team(match_key):
        print(f"✅ Found existing team for match {match_number}. Loading from memory...")
        stored_team = memory_manager.get_team(match_key)
        return stored_team, stored_team.get('dataframe', None)
    
    print(f"🆕 Creating new team for match {match_number}: {home_team} vs {away_team}")
    
    # Define agents
    todays_teams = Agent(
        role="Match Details Analyst",
        goal=f"Analyze IPL 2025 Match {match_number}: {home_team} vs {away_team} on {match_date}.",
        backstory="You are a seasoned IPL analyst who can pull stats, pitch reports, toss updates, and venue history.",
        tools=[search],
        llm=llm,
        verbose=True,
    )

    get_todays_teams = Task(
        name=f"Match {match_number} IPL Details",
        description=f"""Get full insights for Match {match_number} happening on {match_date} ({match_day}) at {match_time} between {home_team} and {away_team} at {venue}.""",
        expected_output=f"""
        1. Match start time and venue
        2. Live pitch report and conditions
        3. Historical records of both teams at {venue}
        4. IPL 2024 stats for this ground
        5. Who won the toss today and what they chose
        """,
        agent=todays_teams,
    )

    # Fixed team selector - no user input needed
    fixed_team_selector = Agent(
        role="Fixed Team Selector",
        goal="Automatically select the two teams playing in this match for Dream11 analysis.",
        backstory="You automatically identify the playing teams for Dream11 team creation.",
        llm=llm,
        verbose=True,
    )

    select_teams = Task(
        name="Auto Team Selection for Dream11",
        description=f"Automatically select {home_team} and {away_team} as the teams for Dream11 analysis.",
        expected_output=f'{{"selected_match": "{home_team} vs {away_team}", "team_1": "{home_team}", "team_2": "{away_team}"}}',
        agent=fixed_team_selector,
        context=[get_todays_teams],
    )

    # Complete the missing parts of your code

    # Complete the players agent initialization
    players = Agent(
        role="Player Analyst",
        goal="Provide the names and stats of players from the selected teams for IPL 2025.",
        backstory="Expert in IPL player analysis and statistics. You focus only on players from the teams playing in the current match.",
        tools=[search],
        llm=llm,
        verbose=True,
    )

    # Complete the players_task
    players_task = Task(
        name="Player Selector",
        description=f"""Focus ONLY on the teams selected: {home_team} and {away_team}.
        
        Use the following squad information for these teams:
        {home_team}: {IPL_SQUADS.get(home_team, [])}
        {away_team}: {IPL_SQUADS.get(away_team, [])}
        
        Provide detailed analysis of key players from both teams including their recent form, IPL career stats, and expected performance in current match conditions.""",
        expected_output=f"""Player analysis for {home_team} vs {away_team}:
        
        {home_team} Key Players:
        - For Batsmen: Matches, Runs, Average, Strike-Rate, 50s, 100s, HighScore, Recent Form
        - For Bowlers: Matches, Wickets, Economy, Average, Best Bowling, Recent Form
        - For All-Rounders: Batting & Bowling Stats, Recent Form
        
        {away_team} Key Players:
        - For Batsmen: Matches, Runs, Average, Strike-Rate, 50s, 100s, HighScore, Recent Form
        - For Bowlers: Matches, Wickets, Economy, Average, Best Bowling, Recent Form  
        - For All-Rounders: Batting & Bowling Stats, Recent Form
        """,
        agent=players,
        context=[select_teams],
    )

    team_selector = Agent(
        role="Dream11 Team Selector",
        goal="Create the optimal Dream11 team based on match conditions, pitch report, past statistics of the ground, player stats, and team composition rules.",
        backstory="You are a Dream11 expert who balances team selection, captaincy choices, and credit allocation.",
        llm=llm,
        verbose=True,
    )

    select_players = Task(
        name="Select Dream11 Players",
        description=f"""Select the best 15 players (11 main + 4 extras) strictly from {home_team} and {away_team} squads only.
        
        Available Players:
        {home_team}: {', '.join(IPL_SQUADS.get(home_team, []))}
        {away_team}: {', '.join(IPL_SQUADS.get(away_team, []))}
        
        Dream11 rules:
        - Total 15 players (11 main team + 4 extras)
        - 1-4 Wicket-keepers, 3-6 Batsmen, 1-4 All-rounders, 3-6 Bowlers
        - Max 7 players from one team
        - Select Captain and Vice-Captain from the 11 main players
        
        IMPORTANT: You MUST include this exact CSV format at the end:
        
        ## DREAM11_CSV_DATA
        PlayerName,Team,Role,C/VC/None
        Player1,{home_team[:3].upper()},WK,C
        Player2,{away_team[:3].upper()},BAT,VC
        Player3,{home_team[:3].upper()},BAT,None
        ...continue for all 15 players
        ## END_CSV_DATA
        """,
        expected_output="""Dream11 team selection with detailed analysis:
        - 15 players total (11 main + 4 extras)
        - Captain and Vice-Captain with reasoning
        - Team composition breakdown
        - Key selection rationale
        - Must end with the structured CSV data in the specified format""",
        agent=team_selector,
        context=[players_task],
    )

    # Create and run the crew
    team_crew = Crew(
        agents=[todays_teams, fixed_team_selector, players, team_selector],
        tasks=[get_todays_teams, select_teams, players_task, select_players],
        process=Process.sequential,
        verbose=True,
    )

    try:
        team_result = team_crew.kickoff()
        print("✅ Team creation completed!")
        print(team_result)
        
        # Function to extract and convert CSV data
        def convert_dream11_to_csv(markdown_text, output_filename=None):
            # Extract the CSV data between the markers
            pattern = r'## DREAM11_CSV_DATA\n(.*?)## END_CSV_DATA'
            match = re.search(pattern, str(markdown_text), re.DOTALL)
            
            if not match:
                print("❌ No CSV data found in expected format")
                return None
            
            # Extract the CSV text
            csv_text = match.group(1).strip()
            
            # Convert to DataFrame
            from io import StringIO
            df = pd.read_csv(StringIO(csv_text))
            
            # Generate output filename if not specified
            if not output_filename:
                # Create a filename with teams and match number
                home_short = home_team.replace(' ', '').replace('Super', '').replace('Kings', '').replace('Indians', '').replace('Challengers', '')[:3]
                away_short = away_team.replace(' ', '').replace('Super', '').replace('Kings', '').replace('Indians', '').replace('Challengers', '')[:3]
                output_filename = f'dream11_{home_short}vs{away_short}_match{match_number}.xlsx'
                
                # Ensure output directory exists
                os.makedirs('output', exist_ok=True)
                output_filename = f'output/{output_filename}'
            
            # Save to Excel file
            df.to_excel(output_filename, index=False)
            
            print(f"✅ Successfully saved to {output_filename}")
            return df
        
        # Convert to CSV using the team_result
        result_text = getattr(team_result, 'raw', str(team_result))
        dream11_df = convert_dream11_to_csv(result_text)
        
        if dream11_df is not None:
            print("\n🏏 Dream11 Team Selected:")
            print(dream11_df)
            
            # Validate team first
            selected_players = dream11_df['PlayerName'].tolist() if 'PlayerName' in dream11_df.columns else []
            validation_passed = False
            
            if selected_players:
                expected_teams = [home_team, away_team]
                validation = validator.validate_team_selection(selected_players, expected_teams)
                
                if validation['valid']:
                    print("✅ Team validation passed!")
                    print(f"👥 Team distribution: {validation['team_distribution']}")
                    validation_passed = True
                else:
                    print("❌ Team validation failed:")
                    for invalid_player in validation['invalid_players']:
                        print(f"  - {invalid_player}")
                    validation_passed = False
            
            # Store team only if validation passed
            team_data = {
                        'match_number': match_number,
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': match_date,
                        'team_result': result_text,
                        'dataframe': stringify_keys(dream11_df.to_dict()),
                        'created_at': datetime.now().isoformat(),
                        'validation_status': validation_passed
                    }

            
            # Store in Firebase only if validated
            storage_success = memory_manager.store_team(match_key, team_data, is_validated=validation_passed)
            
            if validation_passed and storage_success:
                print(f"🔥 Validated team saved to Firebase")
            elif validation_passed and not storage_success:
                print(f"⚠️ Team validated but storage failed")
            
            return team_data, dream11_df
        else:
            print("❌ Failed to extract team data")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creating Dream11 team: {str(e)}")
        return None, None

def main():
    """Streamlined main function - takes match number and auto-handles team creation or analysis"""
    try:
        # Get match number input
        if len(sys.argv) < 2:
            print("❌ Usage: python test.py <match_number>")
            sys.exit(1)

        match_number = sys.argv[1].strip()
        if not match_number.isdigit():
            print("Invalid input. Please enter a valid match number.")
            return
        
        match_number = int(match_number)
        if match_number < 30 or match_number > 76:
            print("Match number out of range (30-76).")
            return

        print(f"🏏 Processing IPL 2025 Match {match_number}")
        
        # Initialize managers
        memory_manager = FirebaseMemoryManager()
        validator = PlayerValidator(IPL_SQUADS)
        
        # Get match details
        match_details = get_match_details(match_number)
        if not match_details:
            print(f"❌ Could not find details for match {match_number}")
            return

        print(f"📅 Match: {match_details['home']} vs {match_details['away']}")
        print(f"📍 Venue: {match_details['venue']}")
        print(f"🕐 Time: {match_details['date']} at {match_details['time']}")

        # Check if team exists in memory
        match_key = memory_manager.get_match_key(match_number, match_details['home'], match_details['away'])
        
        if memory_manager.has_team(match_key):
            # print(f"✅ Found existing team for match {match_number}")
            stored_team = memory_manager.get_team(match_key)
            
            # Display current team
            if 'dataframe' in stored_team and stored_team['dataframe']:
                current_df = pd.DataFrame(stored_team['dataframe'])
                # print(f"\n🏏 Current Dream11 Team:")
                
            
            # Auto-analyze existing team
            print(f"\n🔍 Analyzing current team for optimizations...")
            analyze_and_display_team(stored_team, match_details)
            print(current_df)
            # print(f"💾 Created: {stored_team.get('created_at', 'Unknown')}")
            
        else:
            print(f"🆕 No existing team found. Creating new team...")
            # Create new team
            team_data, dream11_df = create_dream11_team(match_details, memory_manager, validator)
            
            if team_data and dream11_df is not None:
                print(f"\n🎉 New Dream11 team created successfully!")
                print(dream11_df)
                
                # Validate team
                selected_players = dream11_df['PlayerName'].tolist() if 'PlayerName' in dream11_df.columns else []
                if selected_players:
                    expected_teams = [match_details['home'], match_details['away']]
                    validation = validator.validate_team_selection(selected_players, expected_teams)
                    if validation['valid']:
                        print("✅ Team validation passed!")
                        print(f"👥 Team distribution: {validation['team_distribution']}")
                    else:
                        print(validation['invalid_players'])
                        print("⚠️  Team validation issues found")
            else:
                print("❌ Failed to create Dream11 team")

    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def load_and_display_team(match_number):
    """Load and display a previously created team (simplified)"""
    try:
        memory_manager = FirebaseMemoryManager()

        for match_key, team_data in memory_manager.memory.items():
            if str(match_number) in match_key or team_data.get('match_number') == match_number:
                if 'dataframe' in team_data and team_data['dataframe']:
                    df = pd.DataFrame(team_data['dataframe'])
                    return df
                else:
                    return None

        return None

    except Exception as e:
        print(f"❌ Error loading team: {str(e)}")
        return None


def analyze_existing_team():
    """Analyze and optimize existing Dream11 team"""
    try:
        memory_manager = FirebaseMemoryManager()
        analyzer = TeamAnalyzer(llm, IPL_SQUADS)
        
        # Get match number from user
        match_number = input("Enter match number to analyze (30-76): ").strip()
        if not match_number.isdigit():
            print("Invalid input.")
            return
        
        match_number = int(match_number)
        
        # Find stored team
        stored_team = None
        match_key_found = None
        
        for match_key, team_data in memory_manager.memory.items():
            if str(match_number) in match_key or team_data.get('match_number') == match_number:
                stored_team = team_data
                match_key_found = match_key
                break
        
        if not stored_team:
            print(f"❌ No stored team found for match {match_number}")
            print("Available matches in memory:")
            for key, data in memory_manager.memory.items():
                print(f"  Match {data.get('match_number', '?')}: {data.get('home_team', '?')} vs {data.get('away_team', '?')}")
            return
        
        print(f"✅ Found stored team for Match {match_number}")
        print(f"📅 Original team created: {stored_team.get('created_at', 'Unknown')}")
        
        # Get current match details
        match_details = get_match_details(match_number)
        
        # Analyze the team
        print(f"\n🔍 Starting analysis of stored team...")
        analysis_data, optimization_df = analyzer.analyze_stored_team(stored_team, match_details)
        
        if analysis_data:
            print(f"\n📊 ANALYSIS COMPLETE")
            print("="*50)
            
            # Display original team
            if 'dataframe' in stored_team and stored_team['dataframe']:
                original_df = pd.DataFrame(stored_team['dataframe'])
                print(f"\n🏏 ORIGINAL TEAM:")
                print(original_df)
            
            # Display optimization suggestions
            if optimization_df is not None and not optimization_df.empty:
                print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
                print(optimization_df)
                
                # Ask if user wants to apply optimizations
                apply_changes = input(f"\n🤔 Apply suggested optimizations? (y/n): ").strip().lower()
                
                if apply_changes == 'y':
                    optimized_team = analyzer.apply_optimizations(original_df, optimization_df)
                    
                    print(f"\n🚀 OPTIMIZED TEAM:")
                    print(optimized_team)
                    
                    # Save optimized team
                    save_optimized = input(f"\n💾 Save optimized team? (y/n): ").strip().lower()
                    if save_optimized == 'y':
                        # Update stored team with optimized version
                        stored_team['dataframe'] = optimized_team.to_dict()
                        stored_team['last_optimized'] = datetime.now().isoformat()
                        stored_team['optimization_history'] = stored_team.get('optimization_history', [])
                        stored_team['optimization_history'].append({
                            'date': datetime.now().isoformat(),
                            'changes': optimization_df.to_dict() if optimization_df is not None else None
                        })
                        
                        memory_manager.store_team(match_key_found, stored_team)
                        print("✅ Optimized team saved!")
                        
                        # Export to Excel
                        output_filename = f'output/optimized_match{match_number}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
                        os.makedirs('output', exist_ok=True)
                        optimized_team.to_excel(output_filename, index=False)
                        print(f"📁 Exported to: {output_filename}")
                
            else:
                print(f"\n✅ No optimizations needed - your current team looks good!")
            
            # Display analysis insights
            print(f"\n📝 DETAILED ANALYSIS:")
            print("-" * 30)
            analysis_text = analysis_data.get('analysis_result', '')
            # Print key insights (first 1000 characters)
            print(analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text)
            
        else:
            print("❌ Analysis failed")
    
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

def analyze_and_display_team(stored_team, match_details):
    """Analyze existing team and display insights without menu options"""
    try:
        analyzer = TeamAnalyzer(llm, IPL_SQUADS)
        
        # Perform analysis
        analysis_data, optimization_df = analyzer.analyze_stored_team(stored_team, match_details)
        
        if analysis_data:
            print(f"\n📊 TEAM ANALYSIS COMPLETE")
            print("="*50)
            
            # Extract key insights from analysis
            analysis_text = analysis_data.get('analysis_result', '')
            
            # Display current team strengths/weaknesses
            print(f"\n💪 TEAM INSIGHTS:")
            print("-" * 20)
            
            # Extract and display key sections from analysis
            insights = extract_key_insights(analysis_text)
            for section, content in insights.items():
                if content:
                    print(f"\n{section}:")
                    print(content)
            
            # Show optimization suggestions if any
            if optimization_df is not None and not optimization_df.empty:
                print(f"\n💡 SUGGESTED OPTIMIZATIONS:")
                print(optimization_df[['Action', 'PlayerOut', 'PlayerIn', 'Reason']].to_string(index=False))
            else:
                print(f"\n✅ Your current team is well-optimized!")
                
        else:
            print("❌ Unable to analyze team at this time")
            
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")

def extract_key_insights(analysis_text):
    """Extract key insights from analysis text"""
    insights = {
        "🎯 Current Team Strengths": "",
        "⚠️  Areas for Improvement": "",
        "👑 Captaincy Analysis": "",
        "🏏 Match Conditions Impact": ""
    }
    
    try:
        # Simple text extraction - you can enhance this based on your analysis format
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if any(keyword in line.lower() for keyword in ['strength', 'advantage', 'good']):
                current_section = "🎯 Current Team Strengths"
                insights[current_section] += line + "\n"
            elif any(keyword in line.lower() for keyword in ['weakness', 'risk', 'concern', 'improve']):
                current_section = "⚠️  Areas for Improvement"
                insights[current_section] += line + "\n"
            elif any(keyword in line.lower() for keyword in ['captain', 'vc', 'leadership']):
                current_section = "👑 Captaincy Analysis"
                insights[current_section] += line + "\n"
            elif any(keyword in line.lower() for keyword in ['pitch', 'weather', 'condition', 'toss']):
                current_section = "🏏 Match Conditions Impact"
                insights[current_section] += line + "\n"
            elif current_section and len(line) > 20:  # Continue adding to current section
                insights[current_section] += line + "\n"
        
        # Clean up insights
        for key in insights:
            insights[key] = insights[key][:300] + "..." if len(insights[key]) > 300 else insights[key]
            
    except Exception as e:
        print(f"Note: Could not extract detailed insights: {str(e)}")
    
    return insights

if __name__ == "__main__":
    main()