import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1("Welcome to Our Air Quality Dashboard"),
    html.Div([
        html.P( "Stay informed with real-time air pollution data powered by the Copernicus Atmosphere Monitoring Service (CAMS). This platform provides accurate, up-to-date insights into air quality across the globe, helping you understand the impact of pollutants like nitrogen dioxide (NO₂), particulate matter (PM2.5 and PM10), ozone (O₃), and more."),
        html.P("Whether you're a concerned citizen, a policymaker, or a researcher, our goal is to make complex environmental data clear, accessible, and actionable. Explore interactive maps, trend analyses, and forecasts to see how air quality affects your region—and the world.")
    ])
])