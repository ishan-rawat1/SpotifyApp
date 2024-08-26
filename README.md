# Spotify Track Features Analysis and Mood-Based Playlist Application

**Try it: [betterspotify.streamlit.app](https://betterspotify.streamlit.app/)**

This is a web application built using **Streamlit** and the **Spotify API**. The application allows users to explore track features, generate mood-based playlists, and visualize audio features with interactive charts.

## Features

- **Spotify Authentication**: Log in with your Spotify account to access your personal data.
- **Track Feature Analysis**: Get detailed insights into audio features like danceability, energy, valence, and more.
- **Mood-Based Playlist Generator**: Create playlists tailored to your current mood (e.g., Happy, Sad, Relaxed, Energetic).
- **Playlist Creation**: Generate new playlists directly within the app and add your favorite tracks.
- **Audio Feature Visualizations**: Choose between bar charts, radar charts, and pie charts to visualize track data.
- **Add to Liked Songs**: Easily add recommended tracks to your liked songs.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Spotify API
- **Visualizations**: Plotly, Pandas, Matplotlib

## Setup Instructions

### Prerequisites
- **Python 3.8 - 3.11**: Ensure that you have a compatible version of Python installed.
- **Spotify Developer Account**: Create a Spotify Developer account and set up a new application to get your `CLIENT_ID` and `CLIENT_SECRET`.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ishan-rawat1/SpotifyApp.git
   cd SpotifyApp
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
3. Create a .env file in the root directory and add your Spotify credentials:
   ```bash
   CLIENT_ID='your_spotify_client_id'
   CLIENT_SECRET='your_spotify_client_secret'
   REDIRECT_URI='your_redirect_uri'
4. Running the application
   ```bash
   streamlit run Home.py
This will launch the app in your browser. Follow the authentication flow to log in to your Spotify account

### Contribution
Feel free to open issues or submit pull requests for improvements and new features. Contributions are welcome!





