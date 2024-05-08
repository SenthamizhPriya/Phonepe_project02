import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import json
from sqlalchemy import create_engine
import requests
import plotly.express as px

def set_gradient_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: linear-gradient(25deg, #000000, #5E259E);
            color: #ffffff;  
            text-align: center;  
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp .caption, .stApp p, .stApp li { 
            color: #ffffff !important; 
            margin-bottom: 0px;  
        }

        /* Customizing the sidebar background */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(-20deg, #000000, #5E259E);
        }

        /* Customizing button colors in the sidebar */
        .stButton > button {
            display: block;
            width: 100%;
            background-color: rgba(255, 255, 255, 0.1); 
            border-color: transparent;  
            color: #ffffff !important;  
            margin-bottom: 10px; 
        }

        [data-testid="stButton"] > button:hover {
            border-color: transparent;
        }

       /* Focus state */
        .stButton > button:focus, [data-testid="stButton"] > button:focus {
            outline: none;
            border-color: #ffffff; 
            background-color: rgba(255, 255, 255, 0.2); /* Lighter background for focus */
        }

        /* Active state */
        .stButton > button:active, [data-testid="stButton"] > button:active {
            background-color: none;
            color: #ffffff; 
            border-color: #ffffff;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
    

def intro_page():


    st.title("PhonePe Pulse Data Visualisation and Exploration")
    col1, col2, col3 = st.columns([10, 10, 10])
    with col2:
        st.image('phonepe.jpg', width=200, output_format="auto")

    st.markdown("""
<div style='text-align: left; color: white;'>
    <h3 style='color: white; '>Tools Used for the Project:</h3>
    <ul style=font-size: 14px;>
        <li><strong>Streamlit</strong>: For creating the web app.</li>
        <li><strong>Plotly</strong>: For interactive visualizations.</li>
        <li><strong>Pandas</strong>: For data manipulation.</li>
        <li><strong>SQLite</strong>: For database management.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: right; font-size: 16px;margin-bottom: 0px; '>Submitted by</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: right; font-size: 18px;'><b>N. Senthamizh Priya</b></p>", unsafe_allow_html=True)

# Geo visualisation execution

# Function to query data from database
def query_data(category, year, quarter):
    mydb = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="Phonepe_project"
    )
    mycursor = mydb.cursor()
    
    if category == 'Transaction':
        query = """
        SELECT State, Year, Quarter, SUM(Transaction_count) AS All_Transactions, 
        SUM(Transaction_amount) AS Transaction_Amount
        FROM Agg_transaction
        WHERE Year = %s AND Quarter = %s
        GROUP BY State, Year, Quarter
        """
    elif category == 'User':
        query = """
        SELECT State, Year, Quarter, Registeres_users AS Registered_Users, 
        App_open_count AS App_Opens
        FROM Agg_user
        WHERE Year = %s AND Quarter = %s
        """
    
    mycursor.execute(query, (year, quarter))
    rows = mycursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in mycursor.description])
    mycursor.close()
    mydb.close()
    return df

# Custom color scale for the map
coral_scale = [
    [0.0, '#FFC6B7'],  # Very Light Coral
    [0.25,'#FFA494' ], # Light Coral
    [0.5,'#FF7B6F' ],  # Medium Coral
    [0.75, '#FF5240'], # Deep Coral
    [1.0,'#C74444' ]   # Dark Coral
    
]


# Function to load GeoJSON for the map
def load_geojson():
    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    response = requests.get(url)
    return response.json()

# Function to create the choropleth map
def create_choropleth_map(df, category):
    india_geojson = load_geojson()
    color_column = 'Transaction_Amount' if category == 'Transaction' else 'Registered_Users'
    hover_data = ['All_Transactions', 'Transaction_Amount'] if category == 'Transaction' else ['Registered_Users', 'App_Opens']
    
    fig = px.choropleth(
        df,
        geojson=india_geojson,
        locations='State',
        color=color_column,
        hover_name='State',
        hover_data=hover_data,
        color_continuous_scale=coral_scale,  # This will map the numeric range to a color gradient
        featureidkey="properties.ST_NM",
        projection="mercator"
        
    )

    
    fig.update_geos(fitbounds="locations", visible=False)
    
    fig.update_layout(coloraxis_colorbar=dict(title=color_column, thickness = 10,x=60), 
        height=500,                      
        width=500)
    
    
    
    return fig

# Define SQL queries
transaction_query = """
SELECT 
    SUM(Transaction_count) AS Transaction_Count_Sum,
    SUM(Transaction_amount) AS Transaction_Amount_Sum
FROM Agg_transaction
WHERE Year = %s AND Quarter = %s
"""

user_query = """
SELECT SUM(Registeres_users) AS Registered_Users_Sum,
        SUM(App_open_count) AS App_Opens_Sum
FROM Agg_user
WHERE Year = %s AND Quarter = %s
"""

category_query = """
SELECT 
    SUM(CASE WHEN Transaction_type = 'Peer-to-peer payments' THEN Transaction_count ELSE 0 END) AS Peer_to_peer_payments_count,
    SUM(CASE WHEN Transaction_type = 'Merchant payments' THEN Transaction_count ELSE 0 END) AS Merchant_payments_count,
    SUM(CASE WHEN Transaction_type = 'Recharge & bill payments' THEN Transaction_count ELSE 0 END) AS Recharge_and_bill_payments_count,
    SUM(CASE WHEN Transaction_type = 'Financial Services' THEN Transaction_count ELSE 0 END) AS Financial_Services_count,
    SUM(CASE WHEN Transaction_type NOT IN ('Peer-to-peer payments', 'Merchant payments', 'Recharge & bill payments', 'Financial Services') THEN Transaction_count ELSE 0 END) AS Others_count
FROM Agg_transaction
WHERE Year = %s AND Quarter = %s
"""

def Geo_visualisation_page():

        st.header("Geographical Data Visualization")

        col1, col2, col3 = st.columns(3)  # Creates three columns of equal width

        with col1:  # First column for the category dropdown
            option = st.selectbox(
                'Choose a category:',
                ('Transaction', 'User'),
                key='category_select'
            )

        with col2:  # Second column for the year dropdown
            year = st.selectbox(
                'Choose a year:',
                (2018, 2019, 2020, 2021, 2022, 2023),
                key='year_select'
            )

        with col3:  # Third column for the quarter dropdown
            quarter = st.selectbox(
                'Choose a quarter:',
                ('1', '2', '3', '4'),
                key='quarter_select'
            )


            # Button to load data and display map
        if st.button('Show Data'):
            df = query_data(option, year, quarter)
            if not df.empty:
                fig = create_choropleth_map(df, option)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No data available for the selected options.")

            if option == 'Transaction':
            # Fetch transaction data from database
                mydb = mysql.connector.connect(
                    host="localhost", 
                    user="root", 
                    password="", 
                    database="Phonepe_project"
                )
                mycursor = mydb.cursor()

                mycursor.execute(transaction_query, (year, quarter))
                transaction_data = mycursor.fetchone()
                mycursor.close()
                mydb.close()

                sum_transaction_amount = transaction_data[1] / 1e7  # Convert to crores
                formatted_amount = "₹{:,.0f} Cr".format(sum_transaction_amount)
                sum_transaction_count = transaction_data[0]
                formatted_transaction_count = "{:,}".format(sum_transaction_count)


                st.subheader("Transaction Data")
                
                def display_transaction_data(title, value):
                    col1, col2 = st.columns([1, 1])  # Create two columns of equal width
                    with col1:
                        st.write(f"**{title}**")  # Display title in bold font
                    with col2:
                        st.info(value)  # Display value inside a little box

                # Display each transaction data side by side in a box
                display_transaction_data("All Transactions", formatted_transaction_count)
                display_transaction_data("Transaction Value", formatted_amount)

                # Fetch category data from database
                mydb = mysql.connector.connect(
                    host="localhost", 
                    user="root", 
                    password="", 
                    database="Phonepe_project"
                )
                mycursor = mydb.cursor()

                mycursor.execute(category_query,(year, quarter))
                category_data = mycursor.fetchone()
                mycursor.close()
                mydb.close()

                st.subheader("Category Data")
                
                def display_category_data(category_name, category_value):
                    col1, col2 = st.columns([1, 1])  # Create two columns of equal width
                    with col1:
                        st.write(f"**{category_name}**")  # Display category name in bold font
                    with col2:
                        st.info(f"{category_value:,}")  # Display category value inside a little box

                # Display each category data side by side in a box
                display_category_data("Peer-to-peer payments", category_data[0])
                display_category_data("Merchant payments", category_data[1])
                display_category_data("Recharge & bill payments", category_data[2])
                display_category_data("Financial Services", category_data[3])
                display_category_data("Others", category_data[4])

            elif option == 'User':
                # Fetch user data from database
                mydb = mysql.connector.connect(
                    host="localhost", 
                    user="root", 
                    password="", 
                    database="Phonepe_project"
                )
                mycursor = mydb.cursor()

                mycursor.execute(user_query, (year, quarter))
                user_data = mycursor.fetchone()
                mycursor.close()
                mydb.close()

                st.subheader("User Data")

                def display_user_data(title,value):
                    col1,col2 = st.columns([1,1])
                    with col1:
                        st.write(f"**{title}**")
                    with col2:
                        st.info(value)
                
                display_user_data(f"Registered Users",f"{user_data[0]:,}")
                display_user_data(f"App Opens",f"{user_data[1]:,}")



def Top_data_page():
    
    # Create three columns for the dropdowns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox(
            'Choose a category:',
            ('Transaction', 'User'),
            key='category_select'
        )

    with col2:
        year = st.selectbox(
            'Choose a year:',
            ('2018', '2019', '2020', '2021', '2022', '2023'),
            key='year_select'
        )

    with col3:
        quarter = st.selectbox(
            'Choose a quarter:',
            ('1', '2', '3', '4'),
            key='quarter_select'
        )

    # Button to fetch data
    if st.button('Fetch Data'):
        # Connect to MySQL database
        mydb = mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="", 
            database="Phonepe_project"
        )
        mycursor = mydb.cursor()

        # Fetch States data
        if category == 'Transaction':
            state_table = 'Top_state_transaction'
            state_data_column = 'Transaction_count'
        else:
            state_table = 'Top_state_user'
            state_data_column = '`Registered users`'
        
        state_query = f"SELECT `State`, {state_data_column} AS `State Data` FROM {state_table}  WHERE Year = %s AND Quarter = %s"
        mycursor.execute(state_query, (year, quarter))
        state_data = mycursor.fetchall()
        states_df = pd.DataFrame(state_data, columns=['State', 'State Data'])
        st.session_state.states_data = states_df

        # Fetch Districts data
        if category == 'Transaction':
            district_table = 'Top_district_transaction'
            district_data_column = 'Transaction_count'
        else:
            district_table = 'Top_district_user'
            district_data_column = '`Registered users`'
        
        district_query = f"SELECT District, {district_data_column} AS 'District Data' FROM {district_table} WHERE Year = %s AND Quarter = %s"
        mycursor.execute(district_query, (year, quarter))
        district_data = mycursor.fetchall()
        districts_df = pd.DataFrame(district_data, columns=['District', 'District Data'])
        st.session_state.districts_data = districts_df

        # Fetch Pincodes data
        if category == 'Transaction':
            pincode_table = 'Top_pincode_transaction'
            pincode_data_column = 'Transaction_count'
        else:
            pincode_table = 'Top_pincode_user'
            pincode_data_column = '`Registered users`'
        
        pincode_query = f"SELECT Pincode, {pincode_data_column} AS 'Pincode Data' FROM {pincode_table} WHERE Year = %s AND Quarter = %s"
        mycursor.execute(pincode_query, (year, quarter))
        pincode_data = mycursor.fetchall()
        pincodes_df = pd.DataFrame(pincode_data, columns=['Pincode', 'Pincode Data'])
        st.session_state.pincodes_data = pincodes_df

    # Display the data
    if 'states_data' in st.session_state and st.button('Top State Data'):
        st.subheader("State Data")
        st.write(st.session_state.states_data)

    if 'districts_data' in st.session_state and st.button('Top District Data') :
        st.subheader("District Data")
        st.write(st.session_state.districts_data) 

    if 'pincodes_data' in st.session_state and st.button('Top Pincode Data'):
        st.subheader("Pincode Data")
        st.write(st.session_state.pincodes_data)

mydb = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="Phonepe_project"
    )
mycursor = mydb.cursor()


def questions_answers_page():

    # Define function to fetch data and create graph for each question
    def generate_graph(question_number):
        if question_number == 1:

            mycursor.execute('SELECT Year, SUM(Transaction_amount) AS TotalTransactionValue FROM Agg_transaction GROUP BY Year;')
            result = mycursor.fetchall()
            df1 = pd.DataFrame(result, columns=['Year', 'TotalTransactionValue'])
            fig1 = px.bar(df1, x='Year', y='TotalTransactionValue',
                        title='Total Transaction Value Each Year',
                        labels={'TotalTransactionValue': 'Total Transaction Value', 'Year': 'Year'},
                        template='plotly_dark')
            st.plotly_chart(fig1)
        
        elif question_number == 2:

            mycursor.execute('SELECT Year, Quarter, SUM(Transaction_count) AS TotalTransactions FROM Agg_transaction GROUP BY Year, Quarter;')
            result=mycursor.fetchall()
            
            df2 = pd.DataFrame(result, columns=['Year', 'Quarter', 'TotalTransactions'])
            df2['Year_Quarter'] = df2['Year'].astype(str) + ' Q' + df2['Quarter'].astype(str)


            fig2 = px.line(df2, x='Year_Quarter', y='TotalTransactions',
                        title='Number of Transactions Each Quarter Over the Last 5 Years',
                        labels={'TotalTransactions': 'Total Transactions', 'Year_Quarter': 'Year and Quarter'},
                        template='plotly_dark')

            st.plotly_chart(fig2)
            pass
        
        elif question_number == 3:

            mycursor.execute('''SELECT State, SUM(App_open_count) AS TotalAppOpens 
                            FROM Agg_user WHERE Year = (SELECT MAX(Year) FROM Agg_user) GROUP BY State ORDER BY TotalAppOpens DESC; ''')
            result = mycursor.fetchall()

            df3 = pd.DataFrame(result, columns=['State', 'TotalAppOpens'])

            fig3 = px.bar(df3, x='State', y='TotalAppOpens',
                        title='State with the Highest Number of App Opens Last Year',
                        labels={'TotalAppOpens': 'Total App Opens', 'State': 'State'},
                        template='plotly_dark')

            st.plotly_chart(fig3)

            pass

        elif question_number == 4:

            mycursor.execute('SELECT State, SUM(Registeres_users) AS TotalRegistrations FROM Agg_user WHERE Year = (SELECT MAX(Year) FROM Agg_user) AND Quarter = (SELECT MAX(Quarter) FROM Agg_user WHERE Year = (SELECT MAX(Year) FROM Agg_user)) GROUP BY State ORDER BY TotalRegistrations DESC;')
            result=mycursor.fetchall()

            df4 = pd.DataFrame(result, columns=['State', 'TotalRegistrations'])

            fig4 = px.bar(df4, x='State', y='TotalRegistrations',
                        title='State with most User Registrations in the Most Recent Quarter',
                        labels={'TotalRegistrations': 'Total User Registrations', 'State': 'State'},
                        template='plotly_dark')

            st.plotly_chart(fig4)

            pass

        elif question_number == 5:

            mycursor.execute('''SELECT State, SUM(Transaction_amount) AS TotalTransactionValue FROM Agg_transaction 
                            WHERE Year = (SELECT MAX(Year) FROM Agg_transaction) GROUP BY State; ''')
            result = mycursor.fetchall()


            df5 = pd.DataFrame(result, columns=['State', 'TotalTransactionValue'])


            fig5 = px.bar(df5, x='State', y='TotalTransactionValue',
                        title='Transaction Values Across States in the Most Recent Year',
                        labels={'TotalTransactionValue': 'Total Transaction Value', 'State': 'State'},
                        template='plotly_dark')
            
            st.plotly_chart(fig5)

            pass

        elif question_number == 6:

            mycursor.execute( """SELECT State, Year, Quarter, SUM(Transaction_count) AS TotalTransactions FROM Top_state_transaction WHERE Year BETWEEN 2021 AND 2023
                            GROUP BY State, Year, Quarter ORDER BY SUM(Transaction_count) DESC LIMIT 5; """)
            result = mycursor.fetchall()

            df6 = pd.DataFrame(result, columns=['State', 'Year', 'Quarter', 'TotalTransactions'])
            df6['Year_Quarter'] = df6['Year'].astype(str) + ' Q' + df6['Quarter'].astype(str)

            fig6 = px.line(df6, x='Year_Quarter', y='TotalTransactions', color='State',
                        title='Top 5 State Transaction Trends from 2021 to 2023',
                        labels={'TotalTransactions': 'Total Transactions', 'Year_Quarter': 'Year and Quarter'},
                        template='plotly_dark')

            st.plotly_chart(fig6)

            pass

        elif question_number == 7:

            mycursor.execute('''SELECT District_name, SUM(Transaction_amount) AS TotalTransactionValue FROM Map_transaction
                            WHERE Year = (SELECT MAX(Year) FROM Map_transaction) AND Quarter = (SELECT MAX(Quarter) 
                            FROM Map_transaction WHERE Year = (SELECT MAX(Year) FROM Map_transaction))
                            GROUP BY District_name ORDER BY TotalTransactionValue DESC;''')
            result = mycursor.fetchall()


            df7 = pd.DataFrame(result, columns=['District_name', 'TotalTransactionValue'])


            fig7 = px.bar(df7, x='District_name', y='TotalTransactionValue',
                        title='District with the Highest Transaction Value in the Latest Quarter',
                        labels={'TotalTransactionValue': 'Total Transaction Value', 'District_name': 'District'},
                        template='plotly_dark')
            
            st.plotly_chart(fig7)

            pass

        elif question_number == 8:

            mycursor.execute('''SELECT Year, Quarter, SUM(Registeres_users) AS TotalRegisteredUsers FROM Agg_user
            WHERE Year >= (SELECT MAX(Year) FROM Agg_user) - 1 GROUP BY Year, Quarter ORDER BY Year, Quarter;''')
            result = mycursor.fetchall()

            
            df8 = pd.DataFrame(result, columns=['Year', 'Quarter', 'TotalRegisteredUsers'])
            df8['Year_Quarter'] = df8['Year'].astype(str) + ' Q' + df8['Quarter'].astype(str)

            
            fig8 = px.line(df8, x='Year_Quarter', y='TotalRegisteredUsers',
                            title='Trend of Registered User Growth Across Different Quarters for the Last Two Years',
                            labels={'TotalRegisteredUsers': 'Total Registered Users', 'Year_Quarter': 'Year and Quarter'},
                            template='plotly_dark')


            st.plotly_chart(fig8)

            pass

        elif question_number == 9:

            mycursor.execute('''SELECT District_name, SUM(Transaction_count) AS TotalTransactions FROM Map_transaction
                            WHERE Year = (SELECT MAX(Year) FROM Map_transaction) GROUP BY District_name
                            ORDER BY TotalTransactions DESC LIMIT 3;''')
            result = mycursor.fetchall()

            df9 = pd.DataFrame(result, columns=['District_name', 'TotalTransactions'])

            fig9 = px.bar(df9, x='District_name', y='TotalTransactions',
                        title='Top Three Districts by Transaction Count in the Latest Year',
                        labels={'TotalTransactions': 'Total Transactions', 'District_name': 'District'},
                        template='plotly_dark')

            st.plotly_chart(fig9)

            pass

        elif question_number == 10:

    
            mycursor.execute('''SELECT State, SUM(Transaction_amount) AS TotalTransactionValue FROM Agg_transaction
                            WHERE Year = (SELECT MAX(Year) FROM Agg_transaction) GROUP BY State ORDER BY TotalTransactionValue DESC
                            LIMIT 10;''')
            
            result = mycursor.fetchall()

            df10 = pd.DataFrame(result, columns=['State', 'TotalTransactionValue'])

            fig10 = px.bar(df10, x='State', y='TotalTransactionValue',
                                title='State with the Highest Total Transaction Value 2023',
                                labels={'TotalTransactionValue': 'Total Transaction Value', 'State': 'State'},
                                template='plotly_dark')
            
            st.plotly_chart(fig10)

            pass

    # Streamlit app
    def okay():
        st.title("Questions and Answers Page")
        st.write("Select a question from below:")

        # Display buttons for selecting questions
        question_number = st.selectbox("", ['1. What is the total value of transactions each year across India?',
            '2. How has the number of transactions changed each quarter over the last 5 years?',
            '3. Which state had the highest number of app opens last year?',
            '4. Which state saw the most user registrations in the most recent quarter?',
            '5. How do transaction values compare across states in the most recent year?',
            '6. What are the transaction trends over the quarters for the top 5 states with the highest total transactions from 2021 to 2023?',
            '7. Which district had the highest transaction value in the latest quarter?',
            '8. What is the trend of registered user growth across different quarters for the last two years?',
            '9. What are the top three districts with the highest number of transactions in the latest year?',
            '10. Which state had the highest total transaction value in 2023?'])

        # Call function to generate graph based on selected question
        generate_graph(int(question_number.split('.')[0]))

    if __name__ == "__main__":
        okay()




def main():

    set_gradient_bg()  # Set the background globally

    st.sidebar.title("Navigation")

    if 'current_page' not in st.session_state:  
        st.session_state.current_page = 'Introduction'

        # Button navigation
    if st.sidebar.button("Introduction"):
        st.session_state.current_page = 'Introduction'
    if st.sidebar.button("Geo Visualisation"):
        st.session_state.current_page = 'Geo Visualisation'
    if st.sidebar.button("Top Data"):
        st.session_state.current_page = 'Top data'
    if st.sidebar.button("Questions and Answers"):
        st.session_state.current_page = 'Questions and Answers'

        # Display the selected page
    if st.session_state.current_page == "Introduction":
        intro_page()
    elif st.session_state.current_page == "Geo Visualisation":
        Geo_visualisation_page()
    elif st.session_state.current_page == "Top data":
        Top_data_page()
    elif st.session_state.current_page == "Questions and Answers":
        questions_answers_page()

if __name__ == "__main__":
    main()




    