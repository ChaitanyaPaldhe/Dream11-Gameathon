🏏 Dream11 Fantasy Team Selector (IPL Edition)
This Jupyter Notebook helps you automatically generate an optimized Dream11 fantasy cricket team using live match data, player stats, and LLM-powered analysis. It supports matches with multiple fixtures on a single day and integrates various tools to generate the most strategic team possible.⚠️ Note: Its an LLM powered Agent so every output will be unique and different.

🗂️ Code Variants

dream11.py – For days with one IPL match.

🔧 How to Run
On days when there is only one match run dream11.py.
command:- docker run -v /path/to/local/folder:/app/output -it mumbai-super-kings python dream11.py <match number>


🔧 How to Use

1. Choose the Match
On certain days (like Sundays), there may be more than one IPL match. After the script lists all matches for that date, you’ll need to choose the specific match number (1 for the first, 2 for the second, etc.).

selected_match_index = 1  # Change this based on which match you want

2. Run the code
Just run the code. The LLM (language model) will fetch, analyze, and generate the best possible Dream11 team based on:

Player stats

Team combinations

Role constraints

Captain/vice-captain logic

⚠️⚠️⚠️ Note: Sometimes the LLM might act up (generate an incomplete or invalid team, or miss roles).
If that happens, just re-run the cells. Usually, a second or third try does the trick.
Occasionally, not all matches for a given date are fetched properly (especially on multi-fixture days). If you don’t see all expected matches, try running the code again—this typically resolves it.

📦 Dependencies
Make sure you have the following packages installed:

openai, crewai, serper, pandas, requests, etc. (install via pip as needed)

🧠 Behind the Scenes
This tool uses a CrewAI agentic pipeline with different agents handling:

Fetching live match data

Player performance analysis

Dream11 rule validation

Optimal team generation via LLMs (Gemini, GPT, etc.)

📝 Tips
Try to run the code multiple times when error occurs, errors usually occur due to free llm limits.

Double-check the generated team on Dream11's official app before submitting!

