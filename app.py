import dash
from dash import dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct path to CSV file
csv_path = os.path.join(current_dir, 'forecast_data.csv')

# Read the CSV data from file
df = pd.read_csv(csv_path)

# Convert probability to percentage and get the most recent prediction
latest_prediction = df.iloc[-1]  # Get the last row
current_probability = float(latest_prediction['Probability Yes']) * 100
current_forecaster_count = latest_prediction['Forecaster Count']

# Initialize the app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

def create_main_figure():
    fig = go.Figure()
    
    # Add a gauge chart for the probability
    if current_probability is not None:
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = current_probability,
            title = {'text': "Current Probability"},
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

def create_timeline_figure():
    # Convert 'End Time' to datetime
    df['End Time'] = pd.to_datetime(df['End Time'])
    
    # Create figure with secondary y-axis
    fig = go.Figure()

    # Add probability line
    fig.add_trace(
        go.Scatter(
            x=df['End Time'],
            y=df['Probability Yes'].mul(100),
            name='Probability',
            line=dict(color='#4ade80', width=2),
            hovertemplate='%{x}<br>Probability: %{y:.1f}%<extra></extra>'
        )
    )

    # Add forecaster count line
    fig.add_trace(
        go.Scatter(
            x=df['End Time'],
            y=df['Forecaster Count'],
            name='Forecaster Count',
            line=dict(color='#94a3b8', width=2, dash='dot'),
            yaxis='y2',
            hovertemplate='%{x}<br>Forecasters: %{y}<extra></extra>'
        )
    )

    # Update layout
    fig.update_layout(
        title='Prediction History',
        plot_bgcolor='#1f2937',
        paper_bgcolor='#1f2937',
        font=dict(color='white'),
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='#374151',
            tickformat='%Y-%m-%d'
        ),
        yaxis=dict(
            title='Probability (%)',
            showgrid=True,
            gridcolor='#374151',
            range=[0, 100]
        ),
        yaxis2=dict(
            title='Number of Forecasters',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, df['Forecaster Count'].max() * 1.1]
        ),
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)'
        ),
        margin=dict(t=60, b=40),
        height=400
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
                        f"{current_probability:.1f}% probability",
                        style={'color': '#4ade80'}
                    )
                ], 
                style={'color': 'white', 'textAlign': 'center'}
            ),
            html.P(
                f"Based on {current_forecaster_count} predictions from Metaculus community",
                style={'color': 'gray', 'textAlign': 'center'}
            ),
        ]),
    ]),
    
    # Main probability gauge
    dcc.Graph(
        figure=create_main_figure(),
        style={'backgroundColor': '#1f2937'}
    ),
    
    # Timeline plot
    html.Div([
        html.H3("Prediction Timeline", style={'color': 'white', 'marginTop': '20px'}),
        dcc.Graph(
            figure=create_timeline_figure(),
            style={'backgroundColor': '#1f2937'}
        ),
    ]),
    
    # Question Details
    html.Div([
        html.H3("Question Details", style={'color': 'white', 'marginTop': '20px'}),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Resolution Criteria", style={'color': 'white'}),
                    html.P(
                        """This question will resolve as YES if the World Health Organization (WHO) declares a Public Health Emergency of International Concern (PHEIC) for any avian influenza virus strain in humans at any point before 2030.

The declaration must specifically cite an avian influenza virus (e.g. H5N1, H7N9) as the cause.""",
                        style={'color': 'gray', 'whiteSpace': 'pre-wrap'}
                    ),
                    html.A(
                        "View on Metaculus →", 
                        href="https://www.metaculus.com/questions/23387/",
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
