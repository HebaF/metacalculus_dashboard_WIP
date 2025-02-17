import dash
from dash import dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import requests

# Initialize the app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

class MetaculusPredictor:
    def __init__(self):
        self.question_id = "23387"  # Avian flu PHEIC question ID
        
    def get_prediction_data(self):
        """Get prediction data from Metaculus API"""
        try:
            url = f"https://www.metaculus.com/api2/questions/{self.question_id}/"
            print(f"Attempting to fetch data from: {url}")  # Debug line
            
            headers = {
                'User-Agent': 'Metaculus Dashboard (Python/Dash)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            print(f"Response status code: {response.status_code}")  # Debug line
            
            if response.status_code == 200:
                data = response.json()
                print(f"Raw prediction data: {data.get('community_prediction')}")  # Debug line
                
                return {
                    'community_prediction': round(data.get('community_prediction', {}).get('q2', 0) * 100, 1),
                    'prediction_count': data.get('prediction_count'),
                    'created_time': data.get('created_time'),
                    'resolution_criteria': data.get('resolution_criteria'),
                    'description': data.get('description'),
                    'close_time': data.get('close_time')
                }
            print(f"Error: API returned status code {response.status_code}")
            return None
        except Exception as e:
            print(f"Error fetching Metaculus data: {e}")
            return None

predictor = MetaculusPredictor()
prediction_data = predictor.get_prediction_data()
print("Prediction data:", prediction_data)  # Debug line

def create_main_figure():
    fig = go.Figure()
    
    # Add a gauge chart for the probability
    if prediction_data and prediction_data.get('community_prediction'):
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = prediction_data['community_prediction'],
            title = {'text': "Probability"},
            gauge = {
                'axis': {'range': [0, 100], 'ticksuffix': "%"},
                'bar': {'color': "#4ade80"},
                'bgcolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': '#ef4444'},
                    {'range': [33, 66], 'color': '#eab308'},
                    {'range': [66, 100], 'color': '#4ade80'}
                ],
            }
        ))
    
    fig.update_layout(
        plot_bgcolor='#1f2937',
        paper_bgcolor='#1f2937',
        font=dict(color='white'),
        margin=dict(t=60, b=40),
        height=300
    )
    return fig

app.layout = html.Div([
    # Main title and current prediction
    html.Div([
        html.H1('Will an avian influenza virus in humans be declared a "Public Health Emergency of International Concern" by the WHO before 2030?', 
                style={'color': 'white', 'textAlign': 'center', 'padding': '20px'}),
        
        # Current prediction display
        html.Div([
            html.H2(
                [
                    "Community Prediction: ",
                    html.Span(
                        f"{prediction_data['community_prediction']}% probability" if prediction_data and prediction_data.get('community_prediction') is not None else 'No data available (API Error)',
                        style={'color': '#4ade80' if prediction_data and prediction_data.get('community_prediction') is not None else '#ef4444'}
                    )
                ], 
                style={'color': 'white', 'textAlign': 'center'}
            ),
            html.P(
                f"Based on {prediction_data['prediction_count'] if prediction_data and prediction_data.get('prediction_count') else 'N/A'} predictions from Metaculus community",
                style={'color': 'gray', 'textAlign': 'center'}
            ),
        ]),
    ]),
    
    # Main probability gauge
    dcc.Graph(
        figure=create_main_figure(),
        style={'backgroundColor': '#1f2937'}
    ),
    
    # Question Details
    html.Div([
        html.H3("Question Details", style={'color': 'white', 'marginTop': '20px'}),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Resolution Criteria", style={'color': 'white'}),
                    html.P(
                        prediction_data['resolution_criteria'] if prediction_data and prediction_data.get('resolution_criteria') else "No data available",
                        style={'color': 'gray'}
                    ),
                    html.A(
                        "View on Metaculus →", 
                        href=f"https://www.metaculus.com/questions/{predictor.question_id}/",
                        style={'color': '#4ade80'},
                        target="_blank"
                    ),
                ], style={'backgroundColor': '#1f2937', 'padding': '20px', 'borderRadius': '5px'})
            ]),
        ]),
    ]),
    
    # Additional Context
    html.Div([
        html.H3("What is a PHEIC?", style={'color': 'white', 'marginTop': '20px'}),
        html.P("""
        A Public Health Emergency of International Concern (PHEIC) is a formal declaration by the World Health Organization (WHO) 
        of "an extraordinary event which is determined to constitute a public health risk to other States through the international 
        spread of disease and to potentially require a coordinated international response."
        
        This declaration is made under the International Health Regulations (IHR) and represents the highest level of alert that 
        the WHO can issue.
        """, style={'color': 'gray'}),
    ]),
    
    # Methodology section
    html.Div([
        html.H3("About This Prediction", style={'color': 'white', 'marginTop': '20px'}),
        html.P("""
        This dashboard displays the community prediction from Metaculus, a forecasting platform that aggregates predictions 
        from thousands of forecasters. The prediction shown represents the community's estimated probability that an avian 
        influenza virus will trigger a WHO PHEIC declaration before 2030.
        
        Metaculus uses a scoring system that incentivizes accurate predictions, and the community has a strong track record 
        of forecasting various events and outcomes.
        """, style={'color': 'gray'}),
    ]),
    
    # Update time
    html.Div([
        html.P(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            style={'color': 'gray', 'textAlign': 'right', 'marginTop': '20px'}
        ),
    ]),
    
], style={'backgroundColor': '#111827', 'padding': '20px', 'minHeight': '100vh'})

if __name__ == '__main__':
    app.run_server(debug=True)
