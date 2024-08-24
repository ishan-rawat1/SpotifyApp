import streamlit as st
import requests
import urllib.parse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



REDIRECT_URI = 'https://betterspotify.streamlit.app/'
SCOPE = 'user-top-read user-read-private user-read-email user-library-read playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative user-library-modify user-library-read user-read-recently-played'

CLIENT_ID = '003c2fa42f88469facbc5a5f83cbfb7f'
CLIENT_SECRET = '3e5da1df76304243992bc28bd0243a53'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'


def main():
    st.title("Spotify Track Features Finder")

    if 'access_token' in st.session_state:
        st.success("Successfully authenticated with Spotify.")
        display_app()
        display_playlist_creation()
    else:
        handle_oauth_flow()


def handle_oauth_flow():
    if 'access_token' in st.session_state and st.session_state['access_token']:
        st.success("Successfully authenticated with Spotify.")
        return
    code = st.query_params.get('code', None)
    if code:
        if 'access_token' not in st.session_state or not st.session_state['access_token']:
            access_token = exchange_code_for_access_token(code)
            if access_token:
                st.session_state['access_token'] = access_token
                st.rerun()
            else:
                st.error("Failed to authenticate with Spotify.")
    else:
        auth_url = generate_auth_url()
        st.markdown(f"Please [log in to Spotify]({auth_url}) to continue.", unsafe_allow_html=True)


def generate_auth_url():
    query = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true"
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(query)}"
    return url


def exchange_code_for_access_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        st.error(f"Error getting access token: {response.text}")
        return None


def get_spotify_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json() if response.ok else None


def radar_chart_features(features):
    categories = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']

    data = [features[feat] for feat in categories]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=data,
        theta=categories,
        fill='toself',
        name='Available Audio Features'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True
    )
    return fig


def plotly_feature_chart(features):
    features_df = pd.DataFrame([features])
    features_df = features_df[['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness']]
    features_df = features_df.T.reset_index()
    features_df.columns = ['Feature', 'Value']

    fig = px.bar(features_df, x='Feature', y='Value', title="Audio Features",
                 labels={'Value': 'Measure', 'Feature': 'Audio Feature'},
                 color='Feature',
                 height=400)
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig


def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=payload, auth=(client_id, client_secret))
    access_token = response.json().get('access_token')
    return access_token


def get_track_id(track_name, artist, access_token):
    url = f"https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "q": f"track: {track_name} artist: {artist}",
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    results = response.json().get('tracks', {}).get('items', [])
    if results:
        return results[0]['id']
    else:
        return None


def get_track_features(track_id, access_token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def display_app():
    track_name = st.text_input("Enter the name of the track: ")
    artist_name = st.text_input("Enter the artist name:")
    visualization_option = ["Bar Chart", "Pie Chart", "Radar Chart", "Numeric Table", "No Visualization"]
    chosen_visualization = st.selectbox("Select the audio features visualization you want to see:",
                                        visualization_option)

    #Solving the streamlit's issue of the nested buttons
    if "get_track_features_pressed" not in st.session_state:
        st.session_state["get_track_features_pressed"] = False

    if st.button("Get Track Features"):
        st.session_state["get_track_features_pressed"] = True

    if st.session_state["get_track_features_pressed"]:
        if track_name == "" and artist_name == "":
            st.error("Track not found")
        else:
            access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
            track_id = get_track_id(track_name, artist_name, access_token)
            if track_id:
                features = get_track_features(track_id, access_token)
                spotify_url = f"https://open.spotify.com/track/{track_id}"
                st.markdown(
                    f'<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png" width="20"/> Play: <a href="{spotify_url}" target="_blank">Listen on Spotify</a>',
                    unsafe_allow_html=True)
                if chosen_visualization == "Bar Chart":
                    fig = plotly_feature_chart(features)
                    st.plotly_chart(fig)
                elif chosen_visualization == "Pie Chart":
                    display_pie_chart(features)
                elif chosen_visualization == "Radar Chart":
                    fig1 = radar_chart_features(features)
                    st.plotly_chart(fig1)
                elif chosen_visualization == "Numeric Table":
                    st.subheader('Audio Features Overview')
                    df = pd.DataFrame([features])
                    df = df[
                        ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness',
                         'speechiness',
                         'tempo', 'loudness']]
                    st.write(df.T)

            else:
                st.error("Track not found.")

    st.sidebar.title("Audio Features Explained")
    with st.sidebar.expander("See explanations"):
        st.write("""
        - **Danceability**: Describes how suitable a track is for dancing. based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.
        - **Energy**: A measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.
        - **Loudness**: The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db.
        - **Speechiness**: Detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.
        - **Acousticness**: A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.
        - **Instrumentalness**: Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.
        - **Liveness**: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.
        - **Valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).
        - **Tempo**: The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.
        """)



# Playlist creation
def create_playlist(user_id, name, description, public, access_token):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"name": name,
            "description": description,
            "public": public
            }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def display_playlist_creation():
    st.subheader("Create a New Playlist")
    name = st.text_input("Playlist Name")
    description = st.text_area("Playlist Description")
    public = st.checkbox("Public", value=True)
    if st.button("Create Playlist"):
        if name == "":
            st.error("Enter playlist name")
        else:
            access_token = st.session_state['access_token']
            user_profile = get_spotify_user_profile(access_token)
            if user_profile:
                user_id = user_profile['id']
                new_playlist = create_playlist(user_id, name, description, public, access_token)
                if new_playlist:
                    st.success("Playlist created successfully!")
                else:
                    st.error("Failed to create playlist.")
            else:
                st.error("Could not retrieve user profile. Make sure you are authenticated.")


def pie_chart_features(features):
    labels = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Instrumentalness', 'Liveness', 'Speechiness']
    values = [features[label.lower()] for label in labels]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text='Audio Features Distribution')
    return fig


def display_pie_chart(features):
    fig = pie_chart_features(features)
    st.plotly_chart(fig)


#adding tracks to playlist
def get_user_playlists(user_id, access_token):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get('items', [])


def add_tracks_to_playlist(playlist_id, track_id, access_token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"uris": [f"spotify:track:{track_id}"]}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code in (200, 201)


def add_track_to_liked_songs(track_id, access_token):
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"ids": [track_id]}
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in (200, 201)


def display_add_to_playlist(track_id):
    st.subheader("Add Track to Playlist or Liked Songs")
    try:
        access_token = st.session_state['access_token']
        user_profile = get_spotify_user_profile(access_token)
        user_id = user_profile['id']
        playlists = get_user_playlists(user_id, access_token)
    except ValueError:
        st.error("Failed to fetch playlists. Please re-authenticate.")
        return

    playlist_options = ["Liked Songs"] + [playlist['name'] for playlist in playlists]
    if "selected_option" not in st.session_state:
        st.session_state["selected_option"] = playlist_options[0]

    st.session_state["selected_option"] = st.selectbox("Select a Playlist or Liked Songs", playlist_options, index=playlist_options.index(st.session_state["selected_option"]))

    if "add_track_button" not in st.session_state:
        st.session_state["add_track_button"] = False

    if st.button("Add Track"):
        st.session_state["add_track_button"] = True

    if st.session_state["add_track_button"]:
        selected_option = st.session_state["selected_option"]
        if selected_option == "Liked Songs":
            success = add_track_to_liked_songs(track_id, access_token)
            if success:
                st.success("Track added to liked songs!")
            else:
                st.error("Failed to add track to liked songs.")
        else:
            selected_playlist = next((playlist for playlist in playlists if playlist['name'] == selected_option),
                                     None)
            if selected_playlist:
                success = add_tracks_to_playlist(selected_playlist['id'], track_id, access_token)
                if success:
                    st.success("Track added to playlist!")
                else:
                    st.error("Failed to add track to playlist.")
            else:
                st.error("Selected playlist not found.")



if __name__ == "__main__":
    main()
