import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Hotel Bookings Dashboard", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("Hotelbookings.csv")
    # Clean missing values for key columns
    df['children'] = df['children'].fillna(0)
    df['country'] = df['country'].fillna('Unknown')
    df['agent'] = df['agent'].fillna(-1)
    df['company'] = df['company'].fillna(-1)
    return df

df = load_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")
hotel_types = st.sidebar.multiselect(
    "Select Hotel Type", options=df["hotel"].unique(), default=df["hotel"].unique()
)
years = st.sidebar.multiselect(
    "Select Year", options=sorted(df["arrival_date_year"].unique()), default=sorted(df["arrival_date_year"].unique())
)
months = st.sidebar.multiselect(
    "Select Month", options=df["arrival_date_month"].unique(), default=df["arrival_date_month"].unique()
)
customer_types = st.sidebar.multiselect(
    "Select Customer Type", options=df["customer_type"].unique(), default=df["customer_type"].unique()
)
min_adr, max_adr = int(df['adr'].min()), int(df['adr'].max())
adr_range = st.sidebar.slider("ADR Range", min_adr, max_adr, (min_adr, max_adr))

# Filter data
filtered_df = df[
    (df["hotel"].isin(hotel_types)) &
    (df["arrival_date_year"].isin(years)) &
    (df["arrival_date_month"].isin(months)) &
    (df["customer_type"].isin(customer_types)) &
    (df["adr"].between(adr_range[0], adr_range[1]))
]

# ---- TABS ----
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "ADR Insights", "Booking & Customer Insights", "Cancellation & Revenue", "Special Requests & Parking"
])

# ---- TAB 1: OVERVIEW ----
with tab1:
    st.title("Hotel Bookings: Executive Dashboard")
    st.write("""
        This interactive dashboard provides comprehensive insights into hotel bookings. 
        Use the sidebar to filter data for specific hotels, years, months, and customer types. 
        All visualizations and tables are designed to support macro- and micro-level analysis for strategic decision-making.
    """)
    
    st.subheader("Key KPIs")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Bookings", f"{filtered_df.shape[0]:,}")
    kpi2.metric("Avg. ADR", f"{filtered_df['adr'].mean():.2f}")
    kpi3.metric("Total Revenue", f"{(filtered_df['adr'] * (filtered_df['stays_in_week_nights'] + filtered_df['stays_in_weekend_nights'])).sum():,.0f}")
    kpi4.metric("Cancellation Rate", f"{filtered_df['is_canceled'].mean()*100:.1f}%")
    st.markdown("---")

    st.write("#### Bookings by Hotel Type")
    st.write("This chart highlights booking volume for each hotel type. Use it to spot trends in demand.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="hotel", ax=ax)
    st.pyplot(fig)

    st.write("#### Bookings Over Years")
    st.write("Year-wise bookings help track growth or seasonality patterns.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="arrival_date_year", hue="hotel", ax=ax)
    st.pyplot(fig)

    st.write("#### Top 10 Countries by Booking Volume")
    st.write("See which source markets are most important for your business.")
    top_countries = filtered_df['country'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(y=top_countries.index, x=top_countries.values, ax=ax)
    st.pyplot(fig)

# ---- TAB 2: ADR INSIGHTS ----
with tab2:
    st.header("ADR (Average Daily Rate) Insights")

    st.write("#### Distribution of ADR")
    st.write("This histogram shows how ADR is distributed. Check for pricing clusters or outliers.")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["adr"], bins=30, kde=True, ax=ax)
    st.pyplot(fig)

    st.write("#### ADR by Hotel Type")
    st.write("Boxplots reveal how pricing differs between hotel types.")
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered_df, x="hotel", y="adr", ax=ax)
    st.pyplot(fig)

    st.write("#### ADR Over Time (by Month & Year)")
    st.write("Identify seasonal patterns in ADR across months/years.")
    monthly_adr = filtered_df.groupby(['arrival_date_year','arrival_date_month'])['adr'].mean().reset_index()
    order = ['January','February','March','April','May','June','July','August','September','October','November','December']
    fig, ax = plt.subplots(figsize=(10,4))
    sns.lineplot(data=monthly_adr, x="arrival_date_month", y="adr", hue="arrival_date_year", ax=ax, sort=False)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels(order, rotation=45)
    st.pyplot(fig)

    st.write("#### ADR by Customer Type")
    st.write("See how pricing varies for different segments of guests.")
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered_df, x="customer_type", y="adr", ax=ax)
    st.pyplot(fig)

    st.write("#### ADR by Distribution Channel")
    st.write("Assess which sales channels yield higher/lower average daily rates.")
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered_df, x="distribution_channel", y="adr", ax=ax)
    st.pyplot(fig)

    st.write("#### ADR by Reserved Room Type")
    st.write("Spot pricing differences across room categories.")
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered_df, x="reserved_room_type", y="adr", ax=ax)
    st.pyplot(fig)

# ---- TAB 3: BOOKING & CUSTOMER INSIGHTS ----
with tab3:
    st.header("Booking & Customer Insights")

    st.write("#### Lead Time Distribution")
    st.write("Longer lead times may indicate advanced planning by guests; short lead times can suggest last-minute deals.")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["lead_time"], bins=30, ax=ax)
    st.pyplot(fig)

    st.write("#### Stay Duration (Week + Weekend Nights)")
    st.write("See how long guests typically stay.")
    stay_duration = filtered_df['stays_in_week_nights'] + filtered_df['stays_in_weekend_nights']
    fig, ax = plt.subplots()
    sns.histplot(stay_duration, bins=20, ax=ax)
    st.pyplot(fig)

    st.write("#### Customer Type Distribution")
    st.write("Identify dominant customer profiles.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="customer_type", ax=ax)
    st.pyplot(fig)

    st.write("#### Market Segment Breakdown")
    st.write("Explore the share of bookings by segment (e.g., online, offline, corporate).")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, y="market_segment", order=filtered_df["market_segment"].value_counts().index, ax=ax)
    st.pyplot(fig)

    st.write("#### Repeat Guest Share")
    st.write("Gauge loyalty: How many guests are repeat vs new?")
    repeat_counts = filtered_df['is_repeated_guest'].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=['New', 'Repeat'], y=repeat_counts.values, ax=ax)
    st.pyplot(fig)

    st.write("#### Room Upgrade Rate")
    st.write("Shows percentage of bookings where assigned room type differs from reserved room type.")
    upgrade_rate = (filtered_df['assigned_room_type'] != filtered_df['reserved_room_type']).mean() * 100
    st.metric("Upgrade Rate", f"{upgrade_rate:.2f}%")

# ---- TAB 4: CANCELLATION & REVENUE ----
with tab4:
    st.header("Cancellation & Revenue Analysis")

    st.write("#### Cancellation Rate by Hotel Type")
    st.write("Visualize which hotels have higher cancellation rates.")
    fig, ax = plt.subplots()
    sns.barplot(data=filtered_df, x="hotel", y="is_canceled", ax=ax)
    ax.set_ylabel("Cancellation Rate")
    st.pyplot(fig)

    st.write("#### Monthly Cancellation Trend")
    st.write("Spot patterns or peaks in cancellation behavior.")
    month_cancel = filtered_df.groupby(['arrival_date_month'])['is_canceled'].mean().reindex(order)
    fig, ax = plt.subplots()
    sns.lineplot(x=month_cancel.index, y=month_cancel.values, ax=ax)
    ax.set_ylabel("Cancellation Rate")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.write("#### Revenue by Month")
    st.write("Understand revenue generation over time.")
    filtered_df["revenue"] = filtered_df["adr"] * (filtered_df["stays_in_week_nights"] + filtered_df["stays_in_weekend_nights"])
    revenue_month = filtered_df.groupby('arrival_date_month')["revenue"].sum().reindex(order)
    fig, ax = plt.subplots()
    sns.barplot(x=revenue_month.index, y=revenue_month.values, ax=ax)
    ax.set_ylabel("Total Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.write("#### Revenue by Market Segment")
    st.write("Shows which segments are most profitable.")
    revenue_segment = filtered_df.groupby('market_segment')["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots()
    sns.barplot(y=revenue_segment.index, x=revenue_segment.values, ax=ax)
    ax.set_xlabel("Total Revenue")
    st.pyplot(fig)

# ---- TAB 5: SPECIAL REQUESTS & PARKING ----
with tab5:
    st.header("Special Requests & Parking Analysis")

    st.write("#### Distribution of Special Requests")
    st.write("Understand how many special requests guests typically make.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="total_of_special_requests", ax=ax)
    st.pyplot(fig)

    st.write("#### Car Parking Space Requests")
    st.write("Track demand for parking facilities.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="required_car_parking_spaces", ax=ax)
    st.pyplot(fig)

    st.write("#### Bookings with Children and Babies")
    st.write("Explore how many bookings include families with kids.")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["children"], bins=10, ax=ax, label='Children')
    sns.histplot(filtered_df["babies"], bins=10, ax=ax, color='orange', label='Babies')
    plt.legend()
    st.pyplot(fig)

    st.write("#### Top 10 Agents by Number of Bookings")
    st.write("See which travel agents drive most bookings.")
    top_agents = filtered_df['agent'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_agents.index.astype(str), y=top_agents.values, ax=ax)
    ax.set_xlabel("Agent")
    st.pyplot(fig)

    st.write("#### Bookings by Reservation Status")
    st.write("Shows share of bookings that are checked out, canceled, or no-show.")
    fig, ax = plt.subplots()
    sns.countplot(data=filtered_df, x="reservation_status", ax=ax)
    st.pyplot(fig)

# ---- END ----
st.sidebar.markdown("---")
st.sidebar.write("Created by Ajay Mishra (2025) | Powered by Streamlit")

