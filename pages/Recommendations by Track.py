import streamlit as st
import requests


def main():
    st.title("Recommendations by Track")
    if 'access_token' not in st.session_state:
        st.error("Please log in through the Home page first.")
        st.stop()  # Stop further execution of the script
    display_recommendations()


def recommend_similar_tracks(track_id, access_token):
    url = f"https://api.spotify.com/v1/recommendations"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "seed_tracks": track_id,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        recommendations = response.json().get('tracks', [])
        return recommendations
    else:
        st.error("Error getting recommendations.")
        return []


def display_recommendations():
    track_name = st.text_input("Enter track name for recommendations: ")
    artist_name = st.text_input("Enter artist name to correctly find the track")
    if st.button("Get Recommendations"):
        access_token = st.session_state['access_token']
        track_id = get_track_id(track_name, artist_name, access_token)
        if not track_id or track_name == "":
            st.error("Track not found")
            return
        recommendations = recommend_similar_tracks(track_id, access_token)
        if recommendations:
            for track in recommendations:
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                spotify_url = track['external_urls']['spotify']
                st.markdown(f'**{track_name}** by {artist_name} <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png" width="20"/> Play: <a href="{spotify_url}" target="_blank">Listen on Spotify</a>',
                    unsafe_allow_html=True)
        else:
            st.error("No recommendations found.")


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


if __name__ == "__main__":
    main()