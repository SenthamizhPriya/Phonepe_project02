
# PhonePe Pulse Data Visualization and Exploration




## Project overview

This Streamlit application is designed to provide in-depth visualization and analysis of transaction and user data for PhonePe. The project is structured to offer insights through geographical data visualization, transactional analysis, and user behavior across different states and time periods in India.
## Features

- Interactive Geo-visualization: View transaction and user data geographically across different states of India.

- Top Data Analysis: Analyze top performing states, districts, and pincodes in terms of transactions and user registrations.

- Questions and Answers: A dedicated page for querying specific data points like transaction volumes, user registration trends, and more.
## Technologies Used

- Streamlit: For creating the interactive web application.
- Plotly: Utilized for dynamic and interactive charts.
- Pandas: For data manipulation and analysis.
- MySQL: Database used for storing and querying transactional and user data.
- Python: Main programming language.

## How to Set Up and Run the Project

To get this application up and running on your local machine, follow these steps:

- Prerequisites
Python installed on your computer.
Access to the Internet to install dependencies.
A Youtube API key to access YouTube data (you can get one from the Google Developers Console).

- Installation
Install required Python libraries:
pip install streamlit pandas mysql-connector sqlalchemy google-api-python-client

- Cloning repository
git clone https://github.com/PhonePe/pulse.git

- Set up your database:
Have the MySQL server or cloud server installed and running.
Create a database for storing the data from cloned github repository.

- Running the Application
To run the app, navigate to the project directory in your terminal and type:
streamlit run phonepe_streamlit.py
This will start the Streamlit application, and it should be accessible via a web browser at localhost:8506.


## Usage

The application is divided into several sections accessible via a sidebar navigation:

- Introduction: Overview of the project and key technologies.
- Geo Visualisation: Interactive maps showing detailed data based on transactions and users.
- Top Data: Analysis of top states, districts, and pincodes.
- Questions and Answers: Dynamic querying and visualization based on common questions related to transaction and user data.
