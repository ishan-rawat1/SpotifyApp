import streamlit as st
import requests
import math


def main():
    st.title("Mood-Based Playlist Creation")
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

        display_mood_based_playlist_creation()


def create_playlist(user_id, name, description, public, access_token):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"name": name,
            "description": description,
            "public": public
            }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def get_spotify_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json() if response.ok else None


def display_mood_based_playlist_creation():
    st.subheader("Mood-Based Playlist Creation")

    # Mood selection
    mood_options = {
        "Happy": {"valence_range": (0.5, 1.0), "energy_range": (0.4, 1.0)},
        "Relaxed": {"valence_range": (0.3, 0.7), "energy_range": (0.0, 0.6)},
        "Energetic": {"valence_range": (0.4, 1.0), "energy_range": (0.7, 1.0)},
        "Sad": {"valence_range": (0.0, 0.4), "energy_range": (0.0, 0.5)}
    }

    mood = st.selectbox("Select a mood:", list(mood_options.keys()))
    playlist_name = st.text_input("Enter the playlist name:")
    if st.button("Create Mood-Based Playlist"):
        if not playlist_name:
            st.error("Please provide a playlist name.")
        else:
            access_token = st.session_state['access_token']
            user_profile = get_spotify_user_profile(access_token)

            if user_profile is None:
                st.error("Failed to fetch user profile. Please make sure you are authenticated.")
                return

            user_id = user_profile.get('id')
            if not user_id:
                st.error("Failed to retrieve user ID from profile.")
                return
            warning_placeholder = st.empty()
            warning_placeholder = st.warning("Fetching and filtering tracks, this might take a while. Please be patient...")

            # Fetch user's saved tracks
            user_tracks = get_user_saved_tracks(access_token)

            # Filter tracks by mood
            mood_tracks = filter_tracks_by_mood(user_tracks, mood_options[mood], access_token)

            if mood_tracks:
                playlist = create_playlist(user_id, playlist_name, f"A {mood} playlist.", True, access_token)
                playlist_id = playlist.get('id')

                if not playlist_id:
                    st.error("Failed to create playlist.")
                    warning_placeholder.empty()
                    return

                success = add_tracks_to_playlist(playlist_id, mood_tracks, access_token)
                warning_placeholder.empty()

                if success:
                    st.success(f"{mood} playlist created successfully!")
                else:
                    st.error("Failed to add tracks to playlist.")
            else:
                st.error(f"No tracks found that match the {mood} mood.")
                warning_placeholder.empty()


def get_user_saved_tracks(access_token, limit=50):
    """
    Fetches all of the user's saved tracks from Spotify by handling pagination.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/me/tracks?limit={limit}"

    tracks = []
    while url:
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            tracks.extend(data.get('items', []))
            url = data.get('next')  # Get the next page URL from the response
        else:
            st.error(f"Failed to fetch tracks: {response.status_code} - {response.text}")
            break

    return tracks


def filter_tracks_by_mood(tracks, mood_criteria, access_token):
    """
    Filters tracks based on the mood criteria (valence and energy ranges).
    """
    mood_tracks = []
    for track in tracks:
        track_id = track['track']['id']
        features = get_track_features(track_id, access_token)

        if features:
            valence = features.get('valence')
            energy = features.get('energy')

            if (mood_criteria["valence_range"][0] <= valence <= mood_criteria["valence_range"][1] and
                    mood_criteria["energy_range"][0] <= energy <= mood_criteria["energy_range"][1]):
                mood_tracks.append(f"spotify:track:{track_id}")

        if len(mood_tracks) >= 30:
            break

    return mood_tracks if mood_tracks else None


def get_track_features(track_id, access_token):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def add_tracks_to_playlist(playlist_id, track_uris, access_token, batch_size=100):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    total_tracks = len(track_uris)
    num_batches = math.ceil(total_tracks / batch_size)

    for i in range(num_batches):
        batch_start = i * batch_size
        batch_end = min(batch_start + batch_size, total_tracks)
        batch_uris = track_uris[batch_start:batch_end]

        data = {"uris": batch_uris}

        response = requests.post(url, headers=headers, json=data)

        # Check if the request was successful
        if response.status_code not in (200, 201):
            st.error(f"Error adding tracks in batch {i + 1}: {response.status_code} - {response.text}")
            return False  # If one batch fails, return False immediately

    return True  # Return True if all batches succeed


if __name__ == "__main__":
    main()
