import streamlit as st
import os
import gc
import base64
import time
import yaml
from tqdm import tqdm
from brightdata_scrapper import *
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool

# Load environment variables
load_dotenv()

# Initialize Tools
docs_tool = FileReadTool()
bright_data_api_key = os.getenv("BRIGHT_DATA_API_KEY")

@st.cache_resource
def load_llm():
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OPENAI_API_KEY is missing in .env file.")
        return None
    return LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# ===========================
#   Define Agents & Tasks
# ===========================
def create_agents_and_tasks():
    """Creates a Crew for analysis of the channel scrapped output"""
    
    # 1. Safe Config Loading
    if not os.path.exists("config.yaml"):
        st.error("CRITICAL ERROR: config.yaml file is missing.")
        return None

    with open("config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    llm_instance = load_llm()
    if not llm_instance:
        return None

    # 2. Agent Definitions
    analysis_agent = Agent(
        role=config["agents"][0]["role"],
        goal=config["agents"][0]["goal"],
        backstory=config["agents"][0]["backstory"],
        verbose=True,
        tools=[docs_tool],
        llm=llm_instance
    )

    response_synthesizer_agent = Agent(
        role=config["agents"][1]["role"],
        goal=config["agents"][1]["goal"],
        backstory=config["agents"][1]["backstory"],
        verbose=True,
        llm=llm_instance
    )

    # 3. Task Definitions
    analysis_task = Task(
        description=config["tasks"][0]["description"],
        expected_output=config["tasks"][0]["expected_output"],
        agent=analysis_agent
    )

    response_task = Task(
        description=config["tasks"][1]["description"],
        expected_output=config["tasks"][1]["expected_output"],
        agent=response_synthesizer_agent
    )

    # 4. Crew Definition
    crew = Crew(
        agents=[analysis_agent, response_synthesizer_agent],
        tasks=[analysis_task, response_task],
        process=Process.sequential,
        verbose=True
    )
    return crew

# ===========================
#   Streamlit Setup
# ===========================

# Safe Image Loading for Header
header_html = """
    <h1>YouTube Trend Analysis</h1>
    <p>Powered by CrewAI & Bright Data</p>
"""
try:
    if os.path.exists("assets/crewai.png") and os.path.exists("assets/brightdata.png"):
        crew_img = base64.b64encode(open("assets/crewai.png", "rb").read()).decode()
        bd_img = base64.b64encode(open("assets/brightdata.png", "rb").read()).decode()
        header_html = f"""
            <h1>YouTube Trend Analysis powered by <img src="data:image/png;base64,{crew_img}" width="120" style="vertical-align: -3px;"> & <img src="data:image/png;base64,{bd_img}" width="120" style="vertical-align: -3px;"></h1>
        """
except Exception:
    pass # Fallback to text header if images missing

st.markdown(header_html, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "response" not in st.session_state:
    st.session_state.response = None

if "crew" not in st.session_state:
    st.session_state.crew = None

def start_analysis():
    # Validation
    if not bright_data_api_key:
        st.error("⚠️ BRIGHT_DATA_API_KEY is missing!")
        return

    with st.spinner('Scraping videos... This may take a moment.'):
        status_container = st.empty()
        status_container.info("Extracting videos from the channels...")
        
        try:
            # Trigger Scraping
            channel_snapshot_id = trigger_scraping_channels(
                bright_data_api_key, 
                st.session_state.youtube_channels, 
                10, 
                st.session_state.start_date, 
                st.session_state.end_date, 
                "Latest", 
                ""
            )
            
            # API Error Check
            if not channel_snapshot_id or 'snapshot_id' not in channel_snapshot_id:
                status_container.error("Failed to start scraping. Please check your API Key and Channel URL.")
                return

            # Poll for Completion
            snapshot_id = channel_snapshot_id['snapshot_id']
            status = get_progress(bright_data_api_key, snapshot_id)

            while status and status.get('status') != "ready":
                if status.get('status') == "failed":
                    status_container.error("Scraping failed on Bright Data side.")
                    return
                
                status_container.info(f"Current status: {status.get('status')}...")
                time.sleep(10)
                status = get_progress(bright_data_api_key, snapshot_id)
            
            if status and status.get('status') == "ready":
                status_container.success("Scraping completed!")

                # Get Data
                raw_output = get_output(bright_data_api_key, snapshot_id, format="json")
                
                # ✅ CRITICAL FIX: Filter Bad Data
                # Removes any entry that doesn't have a 'url' or 'shortcode'
                cleaned_output = [
                    v for v in raw_output 
                    if isinstance(v, dict) and v.get('url') and v.get('shortcode')
                ]

                if not cleaned_output:
                    status_container.warning("Scraping finished, but no valid videos were found.")
                    return

                # Display Videos
                st.markdown("## YouTube Videos Extracted")
                carousel_container = st.container()
                videos_per_row = 3

                with carousel_container:
                    num_videos = len(cleaned_output)
                    num_rows = (num_videos + videos_per_row - 1) // videos_per_row
                    
                    for row in range(num_rows):
                        cols = st.columns(videos_per_row)
                        for col_idx in range(videos_per_row):
                            video_idx = row * videos_per_row + col_idx
                            if video_idx < num_videos:
                                with cols[col_idx]:
                                    # Safe access
                                    st.video(cleaned_output[video_idx]['url'])

                # Save Transcripts
                status_container.info("Processing transcripts...")
                st.session_state.all_files = []
                
                if not os.path.exists("transcripts"):
                    os.makedirs("transcripts")

                for video in tqdm(cleaned_output):
                    vid_id = video['shortcode']
                    file_path = f"transcripts/{vid_id}.txt"
                    st.session_state.all_files.append(file_path)

                    with open(file_path, "w", encoding="utf-8") as f:
                        transcript = video.get('formatted_transcript', [])
                        # Handle missing transcripts
                        if transcript:
                            for entry in transcript:
                                # Use .get() for safety
                                text = entry.get('text', '')
                                start = entry.get('start_time', 0)
                                end = entry.get('end_time', 0)
                                f.write(f"({start}-{end}): {text}\n")
                        else:
                            f.write("No transcript available for this video.")

                st.session_state.channel_scrapped_output = cleaned_output
                status_container.success("Data ready! Analyzing trends...")

        except Exception as e:
            status_container.error(f"An unexpected error occurred: {str(e)}")
            return

    # Run AI Analysis
    if st.session_state.all_files:
        with st.spinner('The AI agent is analyzing the trends...'):
            st.session_state.crew = create_agents_and_tasks()
            if st.session_state.crew:
                try:
                    # Pass file list as a string
                    file_string = ", ".join(st.session_state.all_files)
                    st.session_state.response = st.session_state.crew.kickoff(inputs={"file_paths": file_string})
                except Exception as e:
                    st.error(f"AI Agent Error: {str(e)}")

# ===========================
#   Sidebar
# ===========================
with st.sidebar:
    st.header("YouTube Channels")
    
    if "youtube_channels" not in st.session_state:
        st.session_state.youtube_channels = [""]
    
    def add_channel_field():
        st.session_state.youtube_channels.append("")
    
    for i, channel in enumerate(st.session_state.youtube_channels):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.session_state.youtube_channels[i] = st.text_input(
                "Channel URL",
                value=channel,
                key=f"channel_{i}",
                label_visibility="collapsed"
            )
        with col2:
            if i > 0:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.youtube_channels.pop(i)
                    st.rerun()
    
    st.button("Add Channel ➕", on_click=add_channel_field)
    st.divider()
    
    st.subheader("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
        st.session_state.start_date = start_date.strftime("%Y-%m-%d")
    with col2:
        end_date = st.date_input("End Date")
        st.session_state.end_date = end_date.strftime("%Y-%m-%d")

    st.divider()
    st.button("Start Analysis 🚀", type="primary", on_click=start_analysis)

# ===========================
#   Main Content Area
# ===========================
if st.session_state.response:
    with st.spinner('Formatting results...'):
        try:
            result = st.session_state.response
            st.markdown("### Generated Analysis")
            st.markdown(result)
            
            # Safe Download Button
            st.download_button(
                label="Download Report",
                data=str(result),
                file_name="youtube_trend_analysis.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")

st.markdown("---")
st.markdown("Built with CrewAI, Bright Data and Streamlit")