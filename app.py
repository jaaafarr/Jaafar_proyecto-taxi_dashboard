from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.io as pio

# Usa el motor Kaleido para exportar imágenes estáticas si fuera necesario,
# pero para Flask usamos HTML
pio.templates.default = "plotly_white"

app = Flask(__name__)


def generate_eda_charts(df):
    # --- Preprocesamiento y Limpieza (Esencial para EDA visual) ---

    # Convertir a datetime
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])

    # Crear columna de hora
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour

    # Filtrar valores extremos o erróneos para mejorar la visualización
    df_clean = df[
        (df['trip_distance'] > 0) &
        (df['trip_distance'] < 100) &  # Filtra distancias extremas
        (df['total_amount'] > 0) &
        (df['total_amount'] < 500)  # Filtra tarifas extremas
        ].copy()

    charts = {}

    # 1. Distribución de Distancia (Histograma)
    fig_dist = px.histogram(
        df_clean,
        x='trip_distance',
        nbins=50,
        title='Distribución de Distancia del Viaje',
        labels={'trip_distance': 'Distancia (millas)'}
    )
    charts['distribution'] = fig_dist.to_html(full_html=False)

    # 2. Demanda de Viajes por Hora del Día (Barra)
    hourly_demand = df_clean['pickup_hour'].value_counts().sort_index().reset_index()
    hourly_demand.columns = ['Hora', 'Viajes']

    fig_demand = px.bar(
        hourly_demand,
        x='Hora',
        y='Viajes',
        title='Demanda de Viajes por Hora del Día',
        color='Viajes',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    charts['demand'] = fig_demand.to_html(full_html=False)

    # 3. Tarifa Total vs. Distancia (Scatter plot)
    # Tomamos una muestra para que el gráfico sea más rápido de cargar
    sample_df = df_clean.sample(n=10000, random_state=42) if len(df_clean) > 10000 else df_clean

    fig_scatter = px.scatter(
        sample_df,
        x='trip_distance',
        y='total_amount',
        color='passenger_count',
        title='Relación entre Distancia y Tarifa Total',
        labels={'trip_distance': 'Distancia (millas)', 'total_amount': 'Monto Total ($)'}
    )
    charts['scatter'] = fig_scatter.to_html(full_html=False)

    return charts


@app.route('/')
def index():
    # Load dataset
    try:
        df = pd.read_csv('nyc_taxi.csv')
    except FileNotFoundError:
        return "Error: Asegúrate de que 'nyc_taxi.csv' esté en la misma carpeta que 'app.py'.", 500

    # Estadísticas y primeras filas
    summary = df.describe(include='all').to_html(classes='table table-striped')
    head = df.head().to_html(classes='table table-bordered')

    # Generar gráficos
    charts = generate_eda_charts(df)

    return render_template('index.html',
                           summary=summary,
                           head=head,
                           chart_distribution=charts['distribution'],
                           chart_demand=charts['demand'],
                           chart_scatter=charts['scatter'])


if __name__ == '__main__':
    app.run(debug=True)