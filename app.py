import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

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

data['Normalized Rank'] = (data['Rank On Google'].max() - data['Rank On Google'] + 1)
data['Normalized Reviews'] = (data['Reviews'] - data['Reviews'].min()) / (data['Reviews'].max() - data['Reviews'].min())
data['Normalized Rating'] = (data['Rating'] - data['Rating'].min()) / (data['Rating'].max() - data['Rating'].min())

rank_weight, reviews_weight, rating_weight = 0.25, 0.5, 0.25
data['Combined Reviews Score'] = (
    rank_weight * data['Normalized Rank'] +
    reviews_weight * data['Normalized Reviews'] +
    rating_weight * data['Normalized Rating']
)

final_score_components = [
    'Domain_Strength_10', 'SEO_Backlink_Score_5', 'Page_load_time_5',
    'Total Engagement Score', 'Combined Reviews Score'
]
data[final_score_components] = scaler.fit_transform(data[final_score_components])

weights = {
    'Domain_Strength_10': 0.1,
    'SEO_Backlink_Score_5': 0.1,
    'Page_load_time_5': 0.1,
    'Total Engagement Score': 0.4,
    'Combined Reviews Score': 0.3
}
data['Final Score'] = sum(weights[key] * data[key] for key in weights)

top_10_final_score_fig = px.bar(
    data.nlargest(10, 'Final Score'),
    x='Competition Name',
    y='Final Score',
    color='Final Score',
    title='Top 10 Companies by Final Score',
    labels={"Competition Name": "Competitor"}
)

top_10_engagement_score_fig = px.bar(
    data.nlargest(10, 'Total Engagement Score'),
    x='Competition Name',
    y='Total Engagement Score',
    color='Total Engagement Score',
    title='Top 10 Companies by Engagement Score',
    labels={"Competition Name": "Competitor"}
)

st.subheader("Social Media Engagement by Platform")
engagement_fig = px.bar(
    engagement_data,
    x='Social Media Platform',
    y='Engagement Score',
    color='Competition Name',
    barmode='group',
    title='Social Media Engagement by Platform'
)

st.title("Competitor Analysis Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Engagement by Platform", "Domain Authority", "SEO Score", 
    "Top Final Scores", "Top Engagement Scores"
])

with tab1:
    st.plotly_chart(engagement_fig)

with tab2:
    st.plotly_chart(px.bar(
        data.nlargest(10, 'Domain_Strength_10'),
        x='Competition Name',
        y='Domain_Strength_10',
        title='Top 10 Companies by Domain Authority'
    ))

with tab3:
    st.plotly_chart(px.bar(
        data.nlargest(10, 'SEO_Backlink_Score_5'),
        x='Competition Name',
        y='SEO_Backlink_Score_5',
        title='Top 10 Companies by SEO Score'
    ))

with tab4:
    st.plotly_chart(top_10_final_score_fig)

with tab5:
    st.plotly_chart(top_10_engagement_score_fig)

st.subheader("Top 5 Competitors")
top_5 = data.nlargest(5, 'Final Score')[['Competition Name', 'Final Score']]
st.dataframe(top_5)

st.subheader("Insights")
st.markdown(f"1. Top Competitor In Port Harcourt: {top_5.iloc[0]['Competition Name']}")
st.markdown("2. Best Engagement Platform: Platform with highest engagement score")
st.markdown("3. Key Takeaway: Companies with strong engagement and domain authority are leading the competition.")
st.markdown("[Full Detailed Report](https://docs.google.com/document/d/1UPqLa-lVkh-2O0RA60a3mXay5jjlWAmgShRPARwe_kc/edit?usp=sharing)")
