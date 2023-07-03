import streamlit as st
from datetime import datetime
import pickle
import pandas as pd
import requests
import json


# -----------------------------------------loading data-------------------------------------
# loading the pickle file "df"

df_dict =pickle.load(open('df.pkl','rb'))
df = pd.DataFrame(df_dict)


#loading the pickled movie dataframe( as a dictionary because while loading dataframe we are getting error)
movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

# loading the pickled similarity matrix which were created in vectorization step
similarity = pickle.load(open('similarity.pkl','rb'))





# ---------------------------------------------api calling function----------------------------------------------
def api_call(url):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjM2ZlZGI0NDQ0MDNlYzljZDcwNGQ2Yzg0MmI5NmFkYyIsInN1YiI6IjY0NTc4MzIwNmFhOGUwMDE3MzdmOTc0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.hgyxgLY_KSI_uZD92iyBXqMPI3nSs9SrbrjlMhuDNgQ"
    }
    response = requests.get(url, headers=headers)
    # Get the response text
    response_text = response.text
    # Parse the JSON response
    data=json.loads(response_text)
    return data



# -------------------------------------------------fetching movie id using api--------------------------------------------
def get_movie_id(movie_name):
    # movie_id
    url = ("https://api.themoviedb.org/3/search/movie?query={}&include_adult=false&language=en-US&page=1".format(movie_name))
    data = api_call(url)
    movie_id = data['results'][0]['id']
    return movie_id




# -----------------------------------------------fetching release date ------------------------------------------------
def get_release_date(movie_id):
    url = ("https://api.themoviedb.org/3/movie/{}/release_dates".format(movie_id))
    release_data =api_call(url)
    release_dates = release_data["results"]
    release_date = None
    for release in release_dates:
        if release["iso_3166_1"] == "IN" or release["iso_3166_1"] == "US":
            for date in release["release_dates"]:
                if date["type"] == 3:
                    release_date = date["release_date"]
                    new_format = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    release_date = new_format.strftime("%d-%m-%Y")
                    return release_date
    return "Release date not found"




# --------------------------------------------------recommendation using api----------------------------------------------
def get_recommendation_through_api(movie_id):
    url = ("https://api.themoviedb.org/3/movie/{}/recommendations?language=en-US&page=1".format(movie_id))
    result = api_call(url)
    recommendation = []
    titles = []
    for i in range(0, 12):
        recommendation.append(result['results'][i]['id'])
        titles.append(result['results'][i]['title'])
    return recommendation,titles






# ------------------------------------------- functions for fetching poster from the api---------------------------


def fetch_poster_recommend(movie_id):
        response = requests.get(
            "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id))
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']






# -----------------------------------------------fetching poster using loaded data------------------------------------
def fetch_poster(sorted_data):
    poster = []
    for i in sorted_data:
        response = requests.get(
            "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(i))
        data = response.json()
        poster.append("https://image.tmdb.org/t/p/w500/" + data['poster_path'])
    return poster




# ----------------------------------------------------fetching youtube trailer using api---------------------------------------
def fetch_trailer(sorted_data):
    trailer_url = []
    for i in sorted_data:
        url = ("https://api.themoviedb.org/3/movie/{}/videos?language=en-US".format(i))
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjM2ZlZGI0NDQ0MDNlYzljZDcwNGQ2Yzg0MmI5NmFkYyIsInN1YiI6IjY0NTc4MzIwNmFhOGUwMDE3MzdmOTc0NyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.hgyxgLY_KSI_uZD92iyBXqMPI3nSs9SrbrjlMhuDNgQ"
        }
        response = requests.get(url, headers=headers)
        response_text = response.text
        data = json.loads(response_text)
        for result in data['results']:
            if result['type'] == 'Trailer':
                trailer = result['key']
                trailer_url.append("https://www.youtube.com/watch?v=" + trailer)
                break
    return trailer_url





# -----------------------------------function for recommending movie with poster from uploaded data-------------------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    video_id = []
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        video_id.append(movie_id)
        # fetch poster
        recommended_movies_posters.append(fetch_poster_recommend(movie_id))
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies , recommended_movies_posters,video_id

def sort_dataset(value,num):
    sorted_data = df.sort_values(value, ascending=False)[0:num]['id']
    return sorted_data
def fetch_title(sorted_data):
    title = []
    for i in sorted_data:
        title.append(df[df['id'] == i]['original_title'].values[0])
    return title



# ---------------------------------------------frontend of website--------------------------------------------------


# ----------------------------------------------------Movie Recommender System--------------------------------
st.title("Movie Recommender System")
st.write("Discover your next favorite movie with our personalized recommender system."
         " Get tailored movie recommendations based on your unique preferences and enhance your movie-watching experience.")

# adding space
col = st.columns(1)
for i in range(2):
    with col[0]:
        st.write("")

# adding a select-box for user input
selected_movie_name = st.selectbox(
    'Select your favourite movie',
    movies['title'].values)


#adding a button to get recommendation on clicking
try:    
    if st.button('Recommend'):
        names, poster, movie_id = recommend(selected_movie_name)
        video_url = fetch_trailer(movie_id)
    
        # creating the layout for showing the movie name along with its poster
        for i in range(0, int(10 / 3)):
            col = st.columns(3)
        for i in range(0,10):
            with col[i % 3]:
                st.write(names[i])
                st.video(video_url[i])
    
    
    # adding space
    col = st.columns(1)
    for i in range(5):
        with col[0]:
            st.write("")

except IndexError:
    st.write("Not Found")
except TypeError:
    st.write("Data Not Found")






# -------------------------------------------------------Recommendation Based on Input-------------------------------------

st.title("Recommendation Based on Input")

option = st.selectbox(
        'Recommendation Based on : ',
        ('popularity', 'revenue', 'vote_count'))
num = st.slider('Enter no. of movies you want', 0, 50, 10)
sorted_data = sort_dataset(option,num)
output_title = fetch_title(sorted_data)
output_poster = fetch_poster(sorted_data)
trailer_url = fetch_trailer(sorted_data)


if st.button('Show'):
    st.write("Based on ", option, " ", num, "movies are :")
    for i in range(0,int(num/3)):
        col = st.columns(3)
    for i in range(0,num):
        with col[i%3]:

            # Embed the YouTube video
            st.write(" ")
            st.write(output_title[i])
            st.video(trailer_url[i])
            # st.image(output_poster[i])


# adding space
col = st.columns(1)
for i in range(7):
    with col[0]:
        st.write("")






# -------------------------------------------------------Get Details of Movie----------------------------------------
st.title("Get Details of Movie")
title = st.text_input('Movie title', 'Enter the correct movie name')

try:
    if st.button('Get'):
        movie_id = get_movie_id(title)
        release_date = get_release_date(movie_id)
        poster_path = fetch_poster_recommend(movie_id)
        st.write('Movie title :  ', title)
        st.write('Release Date : ', release_date)
        sorted_data = [movie_id]
        trailer_url = fetch_trailer(sorted_data)
        col1, col2 = st.columns(2)
        with col1:
            st.image(poster_path)

        with col2:
            st.video(trailer_url[0])




            # recommendation based on api calling
        movie_id = get_movie_id(title)
        recommendation, titles = get_recommendation_through_api(movie_id)
        trailer_urls = fetch_trailer(recommendation)
        # adding space
        col = st.columns(1)
        for i in range(5):
            with col[0]:
                st.write("")
        st.title("Recommended Movies")
        for i in range(0, int(num / 3)):
            col = st.columns(3)
        for i in range(0, num):
            with col[i % 3]:
                st.write(titles[i])
                st.video(trailer_urls[i])


except IndexError:
    st.write("Not Found")
except TypeError:
    st.write("Data Not Found")

