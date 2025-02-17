import dash
from dash import dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import os

# Style constants
FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
TEXT_STYLES = {
    'h1': {
        'color': 'white',
        'textAlign': 'center',
        'padding': '20px',
        'fontFamily': FONT_FAMILY,
        'fontWeight': '600',
        'fontSize': '2rem',
        'lineHeight': '1.4'
    },
    'h2': {
        'color': 'white',
        'textAlign': 'center',
        'fontFamily': FONT_FAMILY,
        'fontWeight': '500',
        'fontSize': '1.5rem'
    },
    'h3': {
        'color': 'white',
        'marginTop': '20px',
        'fontFamily': FONT_FAMILY,
        'fontWeight': '500',
        'fontSize': '1.25rem'
    },
    'h4': {
        'color': 'white',
        'fontFamily': FONT_FAMILY,
        'fontWeight': '500',
        'fontSize': '1.1rem'
    },
    'p': {
        'color': 'gray',
        'fontFamily': FONT_FAMILY,
        'lineHeight': '1.6',
        'fontSize': '1rem'
    }
}

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct path to CSV file
csv_path = os.path.join(current_dir, 'forecast_data.csv')

# Read the CSV data from file and clean it
df = pd.read_csv(csv_path)
df = df.dropna(subset=['End Time'])  # Drop rows with missing End Time

# Get the most recent recency-weighted prediction
latest_recency = df[df['Forecaster Username'] == 'recency_weighted'].iloc[-1]
current_probability = float(latest_recency['Probability Yes']) * 100
current_forecaster_count = latest_recency['Forecaster Count']

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
            title = {'text': "Current Recency-Weighted Prediction", 'font': {'family': FONT_FAMILY}},
            gauge = {
                'axis': {'range': [0, 100], 'ticksuffix': "%"},
                'bar': {'color': "#FFC107"}, #custom yellow 1
                'bgcolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': '#004D40'}, #custom green
                    {'range': [33, 66], 'color': '#E1BE6A'}, #custom yellow 2
                    {'range': [66, 100], 'color': '#DC3220'} #custom red
                ],
            }
        ))

    fig.update_layout(
        plot_bgcolor='#1f2937',
        paper_bgcolor='#1f2937',
        font=dict(family=FONT_FAMILY, color='white'),
        margin=dict(t=60, b=40),
        height=300
    )
    return fig

def create_timeline_figure():
    # Convert 'End Time' to datetime
    df['End Time'] = pd.to_datetime(df['End Time'])

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Split data by prediction type
    metaculus_pred = df[df['Forecaster Username'] == 'metaculus_prediction']
    recency_weighted = df[df['Forecaster Username'] == 'recency_weighted']

    # Add forecaster count histogram
    fig.add_trace(
        go.Bar(
            x=df['End Time'],
            y=df['Forecaster Count'],
            name='Forecaster Count',
            marker_color='#94a3b8',
            opacity=0.3,
            yaxis='y2',
            hovertemplate='%{x}<br>Forecasters: %{y}<extra></extra>'
        )
    )

    # Add metaculus prediction line
    fig.add_trace(
        go.Scatter(
            x=metaculus_pred['End Time'],
            y=metaculus_pred['Probability Yes'].mul(100),
            name='Metaculus Prediction',
            line=dict(color='#4ade80', width=2),
            hovertemplate='%{x}<br>Metaculus: %{y:.1f}%<extra></extra>'
        )
    )

    # Add question mark annotation for last Metaculus prediction
    last_metaculus = metaculus_pred.iloc[-1]
    fig.add_annotation(
        x=last_metaculus['End Time'],
        y=float(last_metaculus['Probability Yes']) * 100,
        text="ℹ️",  # info symbol
        showarrow=True,
        arrowhead=0,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#4ade80",
        font=dict(size=16, color="#4ade80"),
        hovertext="Date of most recent Metaculus prediction as of February 17, 2025",
        hoverlabel=dict(bgcolor="#1f2937"),
        yshift=20
    )
    # Add recency weighted line
    fig.add_trace(
        go.Scatter(
            x=recency_weighted['End Time'],
            y=recency_weighted['Probability Yes'].mul(100),
            name='Recency Weighted',
            line=dict(color='#eab308', width=2, dash='dot'),
            hovertemplate='%{x}<br>Recency: %{y:.1f}%<extra></extra>'
        )
    )

    # Update layout
    fig.update_layout(
        title={'text': 'Prediction History', 'font': {'family': FONT_FAMILY}},
        plot_bgcolor='#1f2937',
        paper_bgcolor='#1f2937',
        font=dict(family=FONT_FAMILY, color='white'),
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
            range=[0, df['Forecaster Count'].max() * 1.2]  # Increased range for histogram
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
        height=400,
        barmode='overlay'  # For the histogram
    )

    return fig

app.layout = html.Div([
    # Main title and current prediction
    html.Div([
        html.H1('Will an avian influenza virus in humans be declared a "Public Health Emergency of International Concern" by the WHO before 2030?',
                style=TEXT_STYLES['h1']),

        # Current prediction display
        html.Div([
            html.H2(
                [
                    "Latest Recency-Weighted Prediction: ",
                    html.Span(
                        f"{current_probability:.1f}% probability",
                        style={'color': '#eab308', 'fontFamily': FONT_FAMILY}
                    )
                ],
                style=TEXT_STYLES['h2']
            ),
            html.P(
                f"Based on {current_forecaster_count} predictions from Metaculus community",
                style=TEXT_STYLES['p']
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
        html.H3("Prediction Timeline", style=TEXT_STYLES['h3']),
        dcc.Graph(
            figure=create_timeline_figure(),
            style={'backgroundColor': '#1f2937'}
        ),
    ]),

    # Question Details
    html.Div([
        html.H3("Question Details", style=TEXT_STYLES['h3']),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Resolution Criteria", style=TEXT_STYLES['h4']),
                    html.P(
                        """This question will resolve as YES if the World Health Organization (WHO) declares a Public Health Emergency of International Concern (PHEIC) for any avian influenza virus strain in humans at any point before 2030.

The declaration must specifically cite an avian influenza virus (e.g. H5N1, H7N9) as the cause.""",
                        style={**TEXT_STYLES['p'], 'whiteSpace': 'pre-wrap'}
                    ),
                    html.A(
                        "View on Metaculus →",
                        href="https://www.metaculus.com/questions/23387/",
                        style={'color': '#4ade80', 'fontFamily': FONT_FAMILY},
                        target="_blank"
                    ),
                ], style={'backgroundColor': '#1f2937', 'padding': '20px', 'borderRadius': '5px'})
            ]),
        ]),
    ]),

    # Additional Context
    html.Div([
        html.H3("What is a PHEIC?", style=TEXT_STYLES['h3']),
        html.P("""
        A Public Health Emergency of International Concern (PHEIC) is a formal declaration by the World Health Organization (WHO)
        of "an extraordinary event which is determined to constitute a public health risk to other States through the international
        spread of disease and to potentially require a coordinated international response."

        This declaration is made under the International Health Regulations (IHR) and represents the highest level of alert that
        the WHO can issue.
        """, style=TEXT_STYLES['p']),
    ]),

    # Methodology section
    html.Div([
        html.H3("About This Prediction", style=TEXT_STYLES['h3']),
        html.P("""
        This dashboard displays predictions from Metaculus, a forecasting platform that aggregates predictions
        from thousands of forecasters. The timeline shows both the official Metaculus prediction (which uses a sophisticated
        algorithm to weight forecasters based on track record) and a recency-weighted aggregate that gives more weight to
        recent predictions.

        Metaculus uses a scoring system that incentivizes accurate predictions, and the community has a strong track record
        of forecasting various events and outcomes.
        """, style=TEXT_STYLES['p']),
    ]),

    # Update time
    html.Div([
        html.P(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            style={**TEXT_STYLES['p'], 'textAlign': 'right', 'marginTop': '20px'}
        ),
    ]),

], style={'backgroundColor': '#111827', 'padding': '20px', 'minHeight': '100vh'})

if __name__ == '__main__':
    app.run_server(debug=True)
