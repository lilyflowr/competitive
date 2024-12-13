from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
app = Dash(__name__)

data = pd.read_excel("umarks_market_research.xlsx", sheet_name="Competition", engine='openpyxl')

data['X Engagement Score'] = data['X_No_of_followers'] * data['X Avg Impressions'] * data['X_Imp_Eng_Rate']
data['IG Engagement Score'] = data['IG Followers'] * data['No_Of_IG_Posts'] * data['IG eng Rate']
data['Youtube Engagement Score'] = data['Youtube Videos'] * data['Youtube subscribers'] * data['Youtube views']
data['Facebook Engagement Score'] = data['Facebook Followers'] * data['Facebook Likes']
data['LinkedIn Engagement Score'] = data['LinkedIn followers']
data['Dribbble Engagement Score'] = data['Dribbble followers']

engagement_columns = [
    'X Engagement Score', 'IG Engagement Score', 'Youtube Engagement Score',
    'Facebook Engagement Score', 'LinkedIn Engagement Score', 'Dribbble Engagement Score'
]
scaler = MinMaxScaler()
data[engagement_columns] = scaler.fit_transform(data[engagement_columns])

engagement_data = data.melt(
    id_vars=['Competition Name'],
    value_vars=engagement_columns,
    var_name='Social Media Platform',
    value_name='Engagement Score'
)

data['Total Engagement Score'] = data[engagement_columns].sum(axis=1)

data['Inverted Rank'] = data['Rank On Google'].max() - data['Rank On Google'] + 1
data['Normalized Rank'] = (data['Inverted Rank'] - data['Inverted Rank'].min()) / (data['Inverted Rank'].max() - data['Inverted Rank'].min())

data['Normalized Reviews'] = (data['Reviews'] - data['Reviews'].min()) / (data['Reviews'].max() - data['Reviews'].min())
data['Normalized Rating'] = (data['Rating'] - data['Rating'].min()) / (data['Rating'].max() - data['Rating'].min())

rank_weight = 0.25
reviews_weight = 0.5
rating_weight = 0.25

data['Combined Reviews Score'] = (
    rank_weight * data['Normalized Rank'] +
    reviews_weight * data['Normalized Reviews'] +
    rating_weight * data['Normalized Rating']
)

weights = {
    'Domain_Strength_10': 0.1,      
    'SEO_Backlink_Score_5': 0.1,  
    'Page_load_time_5': 0.1, 
    'Total Engagement Score': 0.4,
    'Combined Reviews Score': 0.3  
}

final_score_components = [
    'Domain_Strength_10', 'SEO_Backlink_Score_5', 'Page_load_time_5',
    'Total Engagement Score', 'Combined Reviews Score'
]
data[final_score_components] = scaler.fit_transform(data[final_score_components])

data['Final Score'] = (
    weights['Domain_Strength_10'] * data['Domain_Strength_10'] +
    weights['SEO_Backlink_Score_5'] * data['SEO_Backlink_Score_5'] +
    weights['Page_load_time_5'] * data['Page_load_time_5'] +
    weights['Total Engagement Score'] * data['Total Engagement Score'] +
    weights['Combined Reviews Score'] * data['Combined Reviews Score']
)


engagement_fig = px.bar(
    engagement_data,
    x='Social Media Platform',
    y='Engagement Score',
    color='Competition Name',
    barmode='group',
    title='Social Media Engagement by Platform',
    labels={"Competition Name": "Competitor", "Engagement Score": "Score"}
)
engagement_fig.update_layout(
    plot_bgcolor='#f9f9f9',
    paper_bgcolor='#f9f9f9',
    title_font_size=18
)

domain_fig = px.bar(
    data.nlargest(10, 'Domain_Strength_10'),
    x= 'Competition Name',
    y='Domain_Strength_10',
    title='Top 10 Companies By Domain Authority',
    labels={"Competition Name": "Competitor"}
)

seo_fig = px.bar(
    data.nlargest(10,'SEO_Backlink_Score_5'),
    x='Competition Name',
    y='SEO_Backlink_Score_5',
    title='Top 10 Companies by SEO Score',
    labels={"Competition Name": "Competitor"}
)

top_5 = data.nlargest(5, 'Final Score')[
    ['Competition Name', 'Total Engagement Score', 'Domain_Strength_10',
     'SEO_Backlink_Score_5', 'Combined Reviews Score', 'Final Score']
]

insights = html.Div([
    html.P(f"1. Top Competitor in Port Harcourt: {top_5.iloc[0]['Competition Name']}", style={'margin-bottom': '10px'}),
    html.P(f"2. Best Social Media Engagement Platform: {engagement_data.loc[engagement_data['Engagement Score'].idxmax(), 'Social Media Platform']}", style={'margin-bottom': '10px'}),
    html.P("3. Key Takeaway: Companies with strong engagement and domain authority are leading the competition.", style={'margin-bottom': '10px'}),
    html.A("Full Detailed Report", href="https://docs.google.com/document/d/1UPqLa-lVkh-2O0RA60a3mXay5jjlWAmgShRPARwe_kc/edit?usp=sharing", target="_blank", style={'font-weight': 'bold', 'text-decoration': 'none', 'color': '#007BFF'})
], style={'padding': '20px', 'background-color': '#f1f1f1', 'border-radius': '5px'})


app.layout = html.Div([
    html.H1("Competitor Analysis Dashboard", style={'text-align': 'center', 'color': '#333', 'margin-bottom': '20px'}),
    
    dcc.Tabs([
        dcc.Tab(label="Engagement Score", children=[dcc.Graph(figure=engagement_fig)], style={'padding': '20px'}),
        dcc.Tab(label="Domain Authority", children=[dcc.Graph(figure=domain_fig)], style={'padding': '20px'}),
        dcc.Tab(label="SEO Score", children=[dcc.Graph(figure=seo_fig)], style={'padding': '20px'}),
    ], style={'margin-bottom': '30px'}),

    html.H2("Top 5 Competitors", style={'text-align': 'center', 'color': '#444', 'margin-bottom': '15px'}),
    dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in top_5.columns],
        data=top_5.to_dict('records'),
        style_table={'margin': '0 auto', 'width': '90%'},
        style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold', 'textAlign': 'center'},
        style_cell={'textAlign': 'center'}
    ),

    html.H2("Insights", style={'text-align': 'center', 'color': '#444', 'margin-top': '30px'}),
    insights
], style={'font-family': 'Arial, sans-serif', 'padding': '20px', 'background-color': '#fafafa'})

if __name__ == "__main__":
    app.run_server(debug=True)
