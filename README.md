# 📊 YouTube Trend Analysis with AI Agents

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Powered-orange)
![Bright Data](https://img.shields.io/badge/Bright%20Data-Scraping-green)

An intelligent application that automates the process of finding and analyzing YouTube trends. This tool scrapes the latest videos from specified channels, extracts transcripts, and uses multi-agent AI systems to generate deep insights, trend patterns, and sentiment analysis.

## 🚀 Features

* **Automated Scraping:** Fetches the latest video data and transcripts from any YouTube channel using **Bright Data**.
* **Multi-Agent Analysis:** Utilizes **CrewAI** to orchestrate two specialized agents:
    * 🕵️‍♂️ **Transcript Analyzer:** Breaks down video content into topics, sentiment, and keywords.
    * 📝 **Response Synthesizer:** Compiles findings into actionable executive summaries.
* **Interactive Dashboard:** Built with **Streamlit** for easy input of channels, date ranges, and viewing results.
* **Video Carousel:** Watch the scraped videos directly within the app.
* **Exportable Reports:** Download the final AI-generated trend report as a Markdown file.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **AI Orchestration:** CrewAI
* **LLM:** OpenAI (GPT-4o / GPT-4o-mini)
* **Data Acquisition:** Bright Data (Web Scraper API)
* **Language:** Python 3.12

## 📂 Project Structure

```text
youtube-trend-analysis/
├── assets/                  # Images for the UI (logos)
├── transcripts/             # Temp storage for scraped video text
├── venv/                    # Virtual Environment (Excluded from Git)
├── .env                     # API Keys (Excluded from Git)
├── .gitignore               # Git configuration
├── app.py                   # Main Streamlit application
├── brightdata_scrapper.py   # Bright Data API integration logic
├── config.yaml              # Agent roles, goals, and tasks definition
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
⚙️ Prerequisites
Before running the application, ensure you have the following:

Python 3.10+ installed.

An OpenAI API Key (Paid account required).

A Bright Data Account with a valid API Token and Dataset ID.

📦 Installation
Clone the repository:

Bash
git clone [https://github.com/skafroz2005/youtube-trend-analysis.git](https://github.com/skafroz2005/youtube-trend-analysis.git)
cd youtube-trend-analysis
Create and activate a virtual environment:

Windows:

Bash
python -m venv venv
.\venv\Scripts\activate
Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate
Install dependencies:

Bash
pip install streamlit crewai crewai-tools brightdata-sdk python-dotenv pyyaml tqdm
Configure Environment Variables: Create a file named .env in the root directory and add your keys:

Code snippet
BRIGHT_DATA_API_KEY=your_bright_data_key_here
OPENAI_API_KEY=your_openai_key_here
🚀 Usage
Run the application:

Bash
streamlit run app.py
Using the App:

Open your browser (usually http://localhost:8501).

Enter YouTube Channel URLs in the sidebar.

Select the Date Range for analysis.

Click Start Analysis 🚀.

View Results:

The app will display the scraped videos.

Once processing is complete, the AI report will appear.

Click "Download Content" to save the report.

🧠 Configuration (config.yaml)
You can customize the behavior of the AI agents by editing config.yaml. This file defines:

Agent Roles: Who the AI is pretending to be.

Backstories: The context given to the AI.

Tasks: Specific instructions on what to analyze (e.g., focusing on specific keywords or sentiment).


👤 Author
Afroz

GitHub: @skafroz2005