# Import necessary libraries
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Set the page configuration
st.set_page_config(
    page_title="The Peak Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a centered title to the app
st.markdown('<h1 class="center-title">The Peak Predictor</h1>', unsafe_allow_html=True)

# Load the data from CSV file
df = pd.read_csv('./Data/Data For BMI 2.0.csv')

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Drop rows with invalid dates
df.dropna(subset=['Date'], inplace=True)

# Ensure data is sorted by date
df.sort_values('Date', inplace=True)

# Reset index after sorting
df.reset_index(drop=True, inplace=True)

# Scale the Market Cycle Indicator to match the log scale
scaling_factor = 1  # Adjust this to better fit the indicator with the BTC price on the log scale
df['Scaled_Indicator'] = df['Indicator'] * scaling_factor

# Get the date range for the x-axis
start_date = df['Date'].min()
end_date = df['Date'].max()

# Calculate latest indicator value
latest_indicator_value = int(round(df['Indicator'].iloc[-1]))  # Round to nearest integer

# Calculate deltas for the last week, month, six months, and year using the correct number of data points
def get_previous_value(points_ago):
    if len(df) > points_ago:
        return int(round(df['Indicator'].iloc[-points_ago - 1]))
    return None

# Calculate deltas
last_week_value = get_previous_value(1)  # Last week means 1 data point ago
last_month_value = get_previous_value(4)  # Approximately 4 data points ago for last month
last_six_months_value = get_previous_value(26)  # Approximately 26 data points ago for last 6 months
last_year_value = get_previous_value(52)  # Approximately 52 data points ago for last year

# Add deltas to the latest indicator
deltas = {
    "Last Week": last_week_value,
    "Last Month": last_month_value,
    "Last 6 Months": last_six_months_value,
    "Last Year": last_year_value
}

# Create a row with the progress bar on the left and the deltas in a 2x2 grid on the right
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Add a "Thermometer" style widget for the current Market Cycle Indicator
    st.subheader(f"Current Value: {latest_indicator_value}/100")

    # Determine the color of the progress bar based on the market state
    if latest_indicator_value < 30:
        color = 'green'
        description = f"The current value is {latest_indicator_value}, indicating a cool market phase."
    elif latest_indicator_value < 70:
        color = 'yellow'
        description = f"The current value is {latest_indicator_value}, indicating a neutral market phase."
    else:
        color = 'red'
        description = f"The current value is {latest_indicator_value}, indicating a hot market phase."

    # Use HTML and CSS to create a colored progress bar
    progress_html = f"""
    <div style="background-color: lightgray; border-radius: 10px; width: 100%; height: 30px; position: relative; margin-bottom: 25px;">
        <div style="background-color: {color}; width: {latest_indicator_value}%; height: 100%; border-radius: 10px;"></div>
    </div>
    """

    # Display the progress bar using markdown
    st.markdown(progress_html, unsafe_allow_html=True)

    # Display the description based on the current market state
    if color == 'green':
        st.success(description)
    elif color == 'yellow':
        st.warning(description)
    else:
        st.error(description)

# Display deltas in a 2x2 grid format using two columns
with col2:
    # Last Week
    if last_week_value is not None:
        delta = latest_indicator_value - last_week_value
        delta_str = f"+{delta}" if delta >= 0 else f"{delta}"
        st.metric(label="Last Week", value=last_week_value, delta=delta_str)
    else:
        st.metric(label="Last Week", value="N/A")

    # Last 6 Months
    if last_six_months_value is not None:
        delta = latest_indicator_value - last_six_months_value
        delta_str = f"+{delta}" if delta >= 0 else f"{delta}"
        st.metric(label="Last 6 Months", value=last_six_months_value, delta=delta_str)
    else:
        st.metric(label="Last 6 Months", value="N/A")

with col3:
    # Last Month
    if last_month_value is not None:
        delta = latest_indicator_value - last_month_value
        delta_str = f"+{delta}" if delta >= 0 else f"{delta}"
        st.metric(label="Last Month", value=last_month_value, delta=delta_str)
    else:
        st.metric(label="Last Month", value="N/A")

    # Last Year
    if last_year_value is not None:
        delta = latest_indicator_value - last_year_value
        delta_str = f"+{delta}" if delta >= 0 else f"{delta}"
        st.metric(label="Last Year", value=last_year_value, delta=delta_str)
    else:
        st.metric(label="Last Year", value="N/A")

# Add spacing before the chart
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# Create the figure
fig = go.Figure()

# Add an invisible line trace for the Bitcoin Price for hover info
fig.add_trace(
    go.Scatter(
        x=df['Date'],
        y=df['BTC_Price'],
        name='Bitcoin Price',
        line=dict(color='rgba(0,0,0,0)'),
        yaxis='y1',  # Reference to the primary y-axis
        hoverinfo='text',
        text=[f"Date: {date.strftime('%Y-%m-%d')}<br>Bitcoin Price: ${int(round(price))}" for date, price in zip(df['Date'], df['BTC_Price'])],
        showlegend=True  # Include in legend
    )
)

# Add color-coded Bitcoin Price trace without hover info
for i in range(len(df) - 1):
    indicator_value = df['Indicator'][i]
    color = f"rgba({int(2.55 * indicator_value)}, {255 - int(2.55 * indicator_value)}, 0, 1)"  # Reversed colors

    # Add line segments for the Bitcoin Price with color-coded sections
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][i], df['Date'][i + 1]],
            y=[df['BTC_Price'][i], df['BTC_Price'][i + 1]],
            mode='lines',
            line=dict(
                color=color,
                width=2
            ),
            showlegend=False,  # Exclude from legend to avoid excessive entries
            hoverinfo='skip',  # Skip hover info for color-coded segments
            yaxis='y1'  # Reference to the combined y-axis
        )
    )

# Add Market Cycle Indicator lines with reversed color (red at the top, green at the bottom)
for i in range(len(df) - 1):
    indicator_value = df['Indicator'][i]
    color = f"rgba({int(2.55 * indicator_value)}, {255 - int(2.55 * indicator_value)}, 0, 0.7)"  # Reversed colors with transparency

    # Add line segments for the scaled indicator
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][i], df['Date'][i + 1]],
            y=[df['Scaled_Indicator'][i], df['Scaled_Indicator'][i + 1]],
            mode='lines',
            line=dict(
                color=color,
                width=2
            ),
            showlegend=False,  # Exclude from legend
            hoverinfo='skip',  # Exclude from hover info for lines
            yaxis='y1'  # Reference to the primary y-axis (combined y-axis)
        )
    )

    # Add filled area for each segment for the scaled indicator
    fig.add_trace(
        go.Scatter(
            x=[df['Date'][i], df['Date'][i + 1], df['Date'][i + 1], df['Date'][i]],
            y=[0, 0, df['Scaled_Indicator'][i + 1], df['Scaled_Indicator'][i]],
            fill='toself',
            mode='none',
            fillcolor=f"rgba({int(2.55 * indicator_value)}, {255 - int(2.55 * indicator_value)}, 0, 0.2)",  # Color-coded fill with lower opacity
            yaxis='y1',  # Reference to the primary y-axis
            hoverinfo='skip',  # No hover info for fill
            showlegend=False  # Do not show in legend
        )
    )

# Add invisible markers to provide hover info for scaled indicator values
fig.add_trace(
    go.Scatter(
        x=df['Date'],
        y=df['Scaled_Indicator'],
        mode='markers',
        marker=dict(
            color='rgba(0,0,0,0)',  # Make markers invisible
            size=6,
            opacity=0.01  # Ensure markers are not visible but still present for hover info
        ),
        name='The Peak Predictor',
        yaxis='y1',  # Reference to the primary y-axis
        hoverinfo='text',  # Include custom hover info
        text=[f"Date: {date.strftime('%Y-%m-%d')}<br>Indicator Value: {int(round(val))}" for date, val in zip(df['Date'], df['Indicator'])]  # Include date and indicator value in hover info
    )
)

# Update layout to include a single y-axis on the right and add a range slider without the selector buttons
fig.update_layout(
    xaxis=dict(
        title='Date',
        showgrid=True,
        gridcolor='darkgray',
        range=[start_date, end_date],  # Set x-axis range to match the date range in the data
        rangeslider=dict(  # Add a range slider for interactive zooming
            visible=True,
            thickness=0.05,
            range=[start_date, end_date]  # Constrain the range slider to the data range
        )
    ),
    yaxis=dict(
        title='BTC Price and The Peak Predictor',
        type='log',
        showgrid=True,
        gridcolor='darkgray',
        tickformat='$,.0f',
        side='right'  # Move y-axis to the right-hand side
    ),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    ),
    height=600,
    hovermode='x unified',
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white', family='Arial'),
    template='plotly_dark'
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)
