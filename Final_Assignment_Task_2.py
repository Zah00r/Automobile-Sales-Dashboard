import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data - using try/except to handle local vs online environments
try:
    data = pd.read_csv('automobile-sales.csv')
except:
    data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# List of years 
year_list = [i for i in range(1980, 2024, 1)]

#---------------------------------------------------------------------------------------
# Layout of the app
app.layout = html.Div([
    # TASK 2.1: Title
    html.H1("U.S. Automobile Market Analysis Dashboard", 
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 24}),
    
    # TASK 2.2: Dropdown menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),
    
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select Year',
            style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
        )
    ]),

    # TASK 2.3: Output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'block', 'padding': '10px'})
])

# TASK 2.4: Callback to disable/enable Year Dropdown
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics': 
        return False
    else: 
        return True

# Callback for plotting graphs
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        # Filter for recession
        recession_data = data[data['Recession'] == 1]
        
        # Plot 1: Sales fluctuation
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                            title="Average Automobile Sales fluctuation over Recession Period"))

        # Plot 2: Avg vehicles sold by type 
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                 
        R_chart2 = dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                            title="Average Sales by Vehicle Type during Recession"))
        
        # Plot 3: Pie chart for advertising expenditure
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                            title="Total Advertising Expenditure Share by Vehicle Type"))

        # Plot 4: Effect of unemployment rate (Corrected casing)
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                            title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[R_chart3, R_chart4], style={'display': 'flex'})
        ]

    elif (input_year and selected_statistics == 'Yearly Statistics'):
        # Ensure year is integer
        yearly_data = data[data['Year'] == int(input_year)]
                              
        # Plot 1: Yearly Automobile sales
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales', title='Annual Average Automobile Sales'))
            
        # Plot 2: Total Monthly Automobile sales
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(mas, x='Month', y='Automobile_Sales', title='Total Monthly Automobile Sales in {}'.format(input_year)))

        # Plot 3: Avg vehicles sold by type for year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                            title='Average Vehicles Sold by Vehicle Type in {}'.format(input_year)))

        # Plot 4: Advertisement Expenditure pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                            title='Advertising Expenditure by Vehicle Type in {}'.format(input_year)))

        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2], style={'display':'flex'}),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4], style={'display': 'flex'})
        ]
    
    return None

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)