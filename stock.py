import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

# Function to preprocess data and prepare sequences
def prepare_data(data, time_steps):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    x, y = [], []
    for i in range(time_steps, len(scaled_data)):
        x.append(scaled_data[i - time_steps:i, 0])  # Only 'Close' price
        y.append(scaled_data[i, 0])  # Only 'Close' price
    return np.array(x), np.array(y), scaler

# Function to plot stock performance using Plotly
def plot_stock_performance(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title='Stock Performance', xaxis_title='Date', yaxis_title='Close Price')
    st.plotly_chart(fig)

# Function to plot volume chart
def plot_volume(data):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='blue'))
    fig.update_layout(title='Trading Volume', xaxis_title='Date', yaxis_title='Volume')
    st.plotly_chart(fig)

# Function to plot moving averages
def plot_moving_averages(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(window=50).mean(), mode='lines', name='50-Day Moving Average', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(window=200).mean(), mode='lines', name='200-Day Moving Average', line=dict(color='green')))
    fig.update_layout(title='Stock Performance with Moving Averages', xaxis_title='Date', yaxis_title='Close Price')
    st.plotly_chart(fig)

# Streamlit web app
st.title('Stock Price Prediction App')
st.write('Upload a CSV file containing historical stock price data with columns for "Date", "Close", and "Volume".')

# User upload section
uploaded_file = st.file_uploader('Upload CSV file', type=['csv'])

if uploaded_file is not None:
    # Load the uploaded data
    dataset = pd.read_csv(uploaded_file)
    dataset['Date'] = pd.to_datetime(dataset['Date'])
    dataset.set_index('Date', inplace=True)
    
    # Display summary statistics
    st.write('**Summary Statistics of the Data**')
    st.write(dataset.describe())
    
    # Plot stock performance
    plot_stock_performance(dataset)
    
    # Plot volume chart
    plot_volume(dataset)
    
    # Plot moving averages
    plot_moving_averages(dataset)
    
    # Prepare data for model training (include only 'Close' price)
    data = dataset[['Close']].values
    time_steps = 60  # Number of time steps
    x_train, y_train, scaler = prepare_data(data, time_steps)
    
    # Define and train the model
    rf_model = RandomForestRegressor()
    rf_model.fit(x_train, y_train)

    # User input section
    prediction_months = st.slider('Select Prediction Horizon (in months)', 1, 12, 6)
    predict_button = st.button('Predict')

    if predict_button:
        # Generate future dates for prediction
        future_dates = pd.date_range(start=dataset.index[-1], periods=prediction_months+1, freq='M')[1:]
        
        # Make predictions for future dates
        future_predictions = []
        for i in range(prediction_months):
            x_input = data[-time_steps:].reshape(1, -1)
            prediction = rf_model.predict(x_input)
            future_predictions.append(prediction[0])
            data = np.roll(data, -1)
            data[-1] = prediction
        
        # Inverse transform the predictions
        future_predictions_inv = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
        
        # Display the predicted prices
        st.write(f'Predicted "Close" prices for the next {prediction_months} months:')
        for i, date in enumerate(future_dates):
            st.write(f'{date}: {future_predictions_inv[i][0]}')
