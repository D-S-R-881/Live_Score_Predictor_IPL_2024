import streamlit as st
import pickle
import pandas as pd
import numpy as np
import xgboost
from xgboost import XGBRegressor
import os
from dotenv import load_dotenv
import requests

st.set_page_config(page_title = "Score Predictor", initial_sidebar_state="collapsed")
st.title('IPL 2024 1st Innings Score Predictor')


# Get the absolute file path of the model.pkl file
model_file_path = os.path.join(os.path.dirname(__file__), "model.pkl")

# Load the model from the file
with open(model_file_path, 'rb') as f:
    model = pickle.load(f)




load_dotenv()  # Load environment variables from .env file
api_key = os.getenv('API_KEY')


match_url = f"https://api.cricapi.com/v1/currentMatches?apikey={api_key}&offset=0"


response1 = requests.get(match_url)
data2 = response1.json()
teams_to_check = ['CSK', 'DC', 'RR', 'GT', 'MI', 'RCB', 'PBKS', 'SRH', 'KKR', 'LSG']
matches = data2["data"]

match_id = ''
for match in matches:
    teams_playing = match["teamInfo"][0]['shortname']
    if any(team in teams_playing for team in teams_to_check):
        match_id = match["id"]
        break
    
url = f"https://api.cricapi.com/v1/match_bbb?apikey={api_key}&id={match_id}"

response = requests.get(url)
data1 = response.json()


batting_team = data1['data']['teams'][0]
bowling_team = data1['data']['teams'][1]
venue = data1['data']['venue']
current_score = data1['data']['score'][0]['r']

total_over = data1['data']['score'][0]['o']
over = 0
ball_in_over = 0
if total_over == int(total_over):
  over = total_over
  ball = 0
else:
  over, ball_in_over = map(int, str(total_over).split('.'))

balls_left = 120 - (over*6 + ball_in_over)

wickets_left = 10 - data1['data']['score'][0]['w']
current_run_rate = current_score / data1['data']['score'][0]['o']
runs_last_five_overs = sum(ball['runs'] for ball in data1['data']['bbb'][-30:]) + sum(ball['extras'] for ball in data1['data']['bbb'][-30:])


batting_team1 = match["teamInfo"][1]['shortname']
bowling_team1 = match["teamInfo"][0]['shortname']


col1, col2 = st.columns(2)

with col1:
    st.header(batting_team1 + ' vs ' + bowling_team1)
with col2:
    st.header(batting_team1 + " :- " + str(current_score) + "-" + str(10-wickets_left) + " (" + str(total_over) + "/20" +")")


if st.button('Predict Score'):
    input_df = pd.DataFrame(
     {'batting_team': [batting_team], 'bowling_team': [bowling_team],'venue':venue, 'current_score': [current_score],'balls_left': [balls_left], 'wickets_left': [wickets_left], 'current_run_rate': [current_run_rate], 'last_five': [runs_last_five_overs]})
    result = model.predict(input_df)
    st.header("Predicted Score - " + str(int(result[0])))