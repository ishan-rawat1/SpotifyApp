import streamlit as st
import requests


def main():
    st.title("Profile Management")
    if 'access_token' not in st.session_state:
        st.error("Please log in through the Home page first.")
        st.stop()  # Stop further execution of the script
    display_user_profile()
    display_user_top_items()
    display_user_engagement()


def get_spotify_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json() if response.ok else None


def display_user_profile():
    access_token = st.session_state['access_token']
    if not access_token:
        st.error("You need to log in through the Home page first.")
        return
    user_profile = get_spotify_user_profile(access_token)
    if user_profile:
        st.subheader("User Profile")
        st.write(f"Username: {user_profile['display_name']}")
        st.write(f"Email: {user_profile['email']}")
        if 'images' in user_profile and len(user_profile['images']) > 0:
            st.image(user_profile['images'][0]['url'] if user_profile['images'] else None)
    else:
        st.error("Failed to fetch user profile")


def get_user_top_items(access_token, item_type='tracks', time_range='medium_term'):
    url = f"https://api.spotify.com/v1/me/top/{item_type}"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {"time_range": time_range, "limit": 10}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get('items', [])


def display_user_top_items():
    st.subheader("User's Top Tracks/Artists")
    access_token = st.session_state['access_token']
    if not access_token:
        st.error("You need to log in through the Home page first.")
        return

    time_range = st.selectbox("Select TIme Range", ["short_term", "medium_term", "long_term"])
    item_type = st.selectbox("Select Item Type", ["tracks", "artists"])
    top_items = get_user_top_items(access_token, item_type, time_range)
    if st.button("List Your Top TRACKS/ARTISTS"):
        if top_items:
            st.subheader(f"Your Top {item_type.capitalize()}")
            for item in top_items:
                if item_type == 'tracks':
                    st.write(f"{item['name']} by {item['artists'][0]['name']}")
                else:
                    st.write(item["name"])
        else:
            if item_type == "artists":
                top_items = get_user_top_items(access_token, item_type="tracks", time_range=time_range)
                if top_items:
                    for item in top_items:
                        st.write(item['artists'][0]['name'])
                else:
                    st.write("No top items found")
            else:
                st.write("No top items found")


def get_user_engagement(access_token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get('items', [])


def display_user_engagement():
    access_token = st.session_state['access_token']
    recent_tracks = get_user_engagement(access_token)
    if recent_tracks:
        st.subheader("Recently Played Tracks")
        for track in recent_tracks[:5]:
            track_info = track['track']
            track_name = track_info['name']
            artist_name = track_info['artists'][0]['name']
            spotify_url = track_info['external_urls']['spotify']
            st.markdown(
                f'**{track_name}** by {artist_name} <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/232px-Spotify_icon.svg.png" width="20"/> Play: <a href="{spotify_url}" target="_blank">Listen on Spotify</a>',
                unsafe_allow_html=True)
    else:
        st.write("No recently played tracks found.")


if __name__ == "__main__":
    main()
