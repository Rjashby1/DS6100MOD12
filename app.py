# Import necessary packages
import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.figure_factory as ff

# --- Load and Clean Data (From Problem 0) ---
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 'educ':'education', 'coninc':'income', 
                              'prestg10':'job_prestige', 'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'}, axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

# --- Create Figures (From Problems 1-6) ---

# Problem 1: Markdown Text
markdown_text = '''
### The Gender Wage Gap

According to analysis from the [Pew Research Center](https://www.pewresearch.org/short-reads/2025/03/04/gender-pay-gap-in-us-has-narrowed-slightly-over-2-decades/), the gap has narrowed only slightly over the past two decades, with women earning about 82 cents for every dollar earned by men in 2022. Research from UVA's [Darden School of Business](https://news.darden.virginia.edu/2024/04/04/why-the-gender-pay-gap-persists-in-american-businesses/) suggests that factors such as differences in industry, work experience, and education levels contribute to this disparity, though a significant portion remains unexplained and may be attributed to gender discrimination.

### About the General Social Survey (GSS)

The data for this dashboard comes from the [General Social Survey (GSS)](https://gss.norc.org/us/en/gss/about-the-gss.html), one of the most influential social science projects in the United States. Since 1972, the GSS has collected data on American society to monitor and explain trends in attitudes, behaviors, and attributes. It is conducted by NORC at the University of Chicago and provides a wealth of information on a wide range of topics, making it an invaluable resource for understanding societal change.
'''

# Problem 2: Table Figure
summary_df = gss_clean.groupby('sex').agg({
    'income': 'mean', 'job_prestige': 'mean',
    'socioeconomic_index': 'mean', 'education': 'mean'
}).round(2).reset_index()
summary_df = summary_df.rename(columns={
    'sex': 'Sex', 'income': 'Mean Income', 'job_prestige': 'Mean Job Prestige',
    'socioeconomic_index': 'Mean Socioeconomic Index', 'education': 'Mean Education (Years)'
})
table_fig = ff.create_table(summary_df)

# Problem 4: Scatter Plot Figure
scatter_data = gss_clean[['job_prestige', 'income', 'sex', 'education', 'socioeconomic_index']].dropna()
scatter_fig = px.scatter(scatter_data, x='job_prestige', y='income', color='sex',
                         hover_data=['education', 'socioeconomic_index'],
                         labels={'job_prestige': 'Job Prestige Score', 'income': 'Annual Income', 'sex': 'Sex'})

# Problem 5: Box Plot Figures
box_data = gss_clean[['income', 'job_prestige', 'sex']].dropna()
income_boxplot_fig = px.box(box_data, x='sex', y='income', color='sex', labels={'income': 'Annual Income', 'sex': ''})
income_boxplot_fig.update_layout(showlegend=False)
prestige_boxplot_fig = px.box(box_data, x='sex', y='job_prestige', color='sex', labels={'job_prestige': 'Job Prestige Score', 'sex': ''})
prestige_boxplot_fig.update_layout(showlegend=False)

# Problem 6: Faceted Box Plot Figure
facet_df = gss_clean[['income', 'sex', 'job_prestige']].copy()
facet_df['prestige_category'] = pd.cut(facet_df['job_prestige'], bins=6)
facet_df = facet_df.dropna()
facet_fig = px.box(facet_df, x='sex', y='income', color='sex', facet_col='prestige_category', 
                   facet_col_wrap=2, color_discrete_map={'male': 'blue', 'female': 'red'},
                   labels={'income': 'Annual Income', 'sex': ''})
facet_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

# Define lists for the dropdown menus
xaxis_options = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
color_options = ['sex', 'region', 'education']

# Use a dark theme stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# --- Initialize the Dash App ---
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server # This is the line that PythonAnywhere needs

# --- Define the Dashboard Layout ---
app.layout = html.Div(style={'backgroundColor': '#111111', 'color': '#7FDBFF'}, children=[
    html.H1(children='GSS 2018: Gender, Occupation, and Income', style={'textAlign': 'center'}),
    html.Div([
        html.H3("Dashboard Context & Controls", style={'textAlign':'center'}),
        html.Details([html.Summary('About This Dashboard'), dcc.Markdown(children=markdown_text)]),
        html.Hr(),
        html.H4("Bar Plot Controls"),
        html.Label("Select a Survey Question:"),
        dcc.Dropdown(id='xaxis-dropdown', options=[{'label': i.replace('_', ' ').title(), 'value': i} for i in xaxis_options], value='male_breadwinner'),
        html.Label("Group By:"),
        dcc.Dropdown(id='color-dropdown', options=[{'label': i.title(), 'value': i} for i in color_options], value='sex'),
    ], style={'width': '24%', 'float': 'left', 'padding': '1%'}),

    html.Div([
        html.H2("Key Metrics by Gender"), dcc.Graph(figure=table_fig),
        html.H2("Attitudes on Social Issues"), dcc.Graph(id='interactive-bar-graph'),
        html.H2("Income vs. Job Prestige"), dcc.Graph(figure=scatter_fig),
        html.Div([
            html.Div([html.H2("Income Distribution"), dcc.Graph(figure=income_boxplot_fig)], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div([html.H2("Job Prestige Distribution"), dcc.Graph(figure=prestige_boxplot_fig)], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'})
        ]),
        html.H2("Income by Job Prestige Level"), dcc.Graph(figure=facet_fig)
    ], style={'width': '72%', 'float': 'right', 'padding': '1%'})
])

# --- Define the Callback for Interactivity ---
@app.callback(
    Output('interactive-bar-graph', 'figure'),
    [Input('xaxis-dropdown', 'value'), Input('color-dropdown', 'value')]
)
def update_graph(xaxis_col, color_col):
    df = gss_clean.copy()
    if color_col == 'education':
        bins = [0, 8, 12, 16, 25]
        labels = ['<9 years', '9-12 years', '13-16 years', '>16 years']
        df['education_binned'] = pd.cut(df['education'], bins=bins, labels=labels, right=True)
        color_col_plot = 'education_binned'
    else:
        color_col_plot = color_col

    df_plot = df.dropna(subset=[xaxis_col, color_col_plot])
    grouped_df = df_plot.groupby([xaxis_col, color_col_plot]).size().reset_index(name='count')
    fig = px.bar(grouped_df, x=xaxis_col, y='count', color=color_col_plot, barmode='group',
                 labels={
                     xaxis_col: xaxis_col.replace('_', ' ').title(),
                     'count': 'Number of Respondents',
                     color_col_plot: color_col.replace('_binned', '').title()
                 })
    fig.update_layout(transition_duration=500, plot_bgcolor='#222222', paper_bgcolor='#111111', font_color='#FFFFFF')
    return fig

# This is for the production server
server = app_final.server

