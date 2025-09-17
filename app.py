import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Cargar el dataset
df = pd.read_csv("student_performance_dataset.csv")
# Reemplazar valores nulos de forma segura (evita FutureWarning)
df["Study_Hours_per_Week"] = df["Study_Hours_per_Week"].fillna(df["Study_Hours_per_Week"].median())
df["Attendance_Rate"] = df["Attendance_Rate"].fillna(df["Attendance_Rate"].median())

# =======================
# Inicializar la app
# =======================
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Rendimiento Estudiantil", style={"textAlign": "center"}),

    # Filtro por género
    html.Label("Selecciona género:"),
    dcc.Dropdown(
        id="gender-filter",
        options=[{"label": g, "value": g} for g in df["Gender"].unique()] + [{"label": "Todos", "value": "Todos"}],
        value="Todos"
    ),

    # Tabs
    dcc.Tabs(id="tabs", value="tab-hist", children=[
        dcc.Tab(label="Histograma de Notas", value="tab-hist"),
        dcc.Tab(label="Horas de Estudio vs Notas", value="tab-scatter"),
        dcc.Tab(label="Asistencia por Educación Parental", value="tab-bar"),
        dcc.Tab(label="Relación Asistencia y Notas", value="tab-box"),
        dcc.Tab(label="Correlación entre Variables", value="tab-heatmap"),
    ]),

    html.Div(id="tabs-content")
])

# =======================
# Callbacks
# =======================
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("gender-filter", "value")]
)
def render_content(tab, gender):
    dff = df.copy()
    if gender != "Todos":
        dff = dff[dff["Gender"] == gender]

    if tab == "tab-hist":
        fig = px.histogram(dff, x="Final_Exam_Score", nbins=20, color="Gender", barmode="overlay")
        fig.update_layout(title="Distribución de notas finales")
        return html.Div([
            html.H3("Distribución de notas finales", style={"textAlign": "center"}),
            html.P("Este histograma muestra cómo se distribuyen las notas finales entre los estudiantes. "
                   "Permite identificar si la mayoría alcanza un rendimiento satisfactorio y si existen "
                   "diferencias relevantes entre géneros."),
            dcc.Graph(figure=fig, style={"height": "600px"})
        ])

    elif tab == "tab-scatter":
        fig = px.scatter(dff, x="Study_Hours_per_Week", y="Final_Exam_Score",
                         color="Gender", size="Attendance_Rate",
                         hover_data=["Parental_Education_Level"])
        fig.update_layout(title="Relación entre horas de estudio y notas")
        return html.Div([
            html.H3("Relación entre horas de estudio y rendimiento académico", style={"textAlign": "center"}),
            html.P("Este diagrama de dispersión permite observar cómo las horas de estudio impactan en el "
                   "rendimiento académico. También muestra diferencias entre géneros y el efecto de la asistencia."),
            dcc.Graph(figure=fig, style={"height": "600px"})
        ])

    elif tab == "tab-bar":
        fig = px.bar(dff, x="Parental_Education_Level", y="Attendance_Rate", color="Gender",
                     barmode="group", height=500)
        fig.update_layout(title="Asistencia según nivel educativo de los padres")
        return html.Div([
            html.H3("Influencia del nivel educativo parental en la asistencia", style={"textAlign": "center"}),
            html.P("Este gráfico de barras ilustra cómo el nivel educativo de los padres puede influir en la "
                   "asistencia de los estudiantes. Es útil para explorar factores externos al rendimiento individual."),
            dcc.Graph(figure=fig, style={"height": "600px"})
        ])

    elif tab == "tab-box":
        fig = px.box(dff, x="Gender", y="Final_Exam_Score", color="Gender",
                     points="all", height=500)
        fig.update_layout(title="Distribución de notas finales por género")
        return html.Div([
            html.H3("Comparación de notas finales entre géneros", style={"textAlign": "center"}),
            html.P("Este boxplot muestra la distribución de las calificaciones finales por género. "
                   "Permite identificar medianas, variabilidad y posibles valores atípicos."),
            dcc.Graph(figure=fig, style={"height": "600px"})
        ])

    elif tab == "tab-heatmap":
        corr = dff[["Study_Hours_per_Week", "Attendance_Rate", "Final_Exam_Score"]].corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r")
        fig.update_layout(title="Mapa de calor de correlaciones")
        return html.Div([
            html.H3("Correlaciones entre variables académicas", style={"textAlign": "center"}),
            html.P("Este mapa de calor presenta las correlaciones entre horas de estudio, asistencia y "
                   "calificaciones finales. Ayuda a identificar qué factores están más asociados con el "
                   "rendimiento académico."),
            dcc.Graph(figure=fig, style={"height": "600px"})
        ])

# =======================
# Ejecutar
# =======================
server = app.server
if __name__ == "__main__":
    app.run(debug=True)
