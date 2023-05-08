import streamlit as st
import pickle
import pandas as pd
import requests
 #function for fetching poster from the api
def fetch_poster(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

# function for recommending movie with poster from the dataframe
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        # fetch poster
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies , recommended_movies_posters


#loading the pickled movie dataframe( as a dictionary because while loading dataframe we are getting error)
movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

# loading the pickled similarity matrix which were created in vectorization step
similarity = pickle.load(open('similarity.pkl','rb'))

#setting title of website
st.title("Movie Recommender System")

# adding a select-box for user input
selected_movie_name = st.selectbox(
    'Enter the movie name you like ',
    movies['title'].values)


#adding a button to get recommendation on clicking
if st.button('Recommend'):
    names , poster  = recommend(selected_movie_name)
    #creating the layout for showing the movie name along with its poster
    col1, col2, col3 , col4 , col5  = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(poster[0])

    with col2:
        st.text(names[1])
        st.image(poster[1])

    with col3:
        st.text(names[2])
        st.image(poster[2])

    with col4:
        st.text(names[3])
        st.image(poster[3])

    with col5:
        st.text(names[4])
        st.image(poster[4])

