import streamlit as st
import requests


def main():
    st.title("Combine your Playlists into ONE Playlist!")
    st.warning("Currently working on this section / not available yet")
    if 'access_token' not in st.session_state or not st.session_state['access_token']:
        st.error("Please log in through the Home page first.")
        st.stop()
    else:
        access_token = st.session_state['access_token']
        # Try to get the user profile to verify token validity
        user_profile = get_spotify_user_profile(access_token)
        if user_profile is None:
            st.error("Access token has expired or is invalid. Please log in again.")
            st.stop()


def get_spotify_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json() if response.ok else None


if __name__ == "__main__":
    main()
