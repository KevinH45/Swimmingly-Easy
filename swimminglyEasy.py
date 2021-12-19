import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize,pos_tag
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import plotly.express as px

#Download stuff required for lemmatizer
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')



st.set_page_config(page_icon=":bar_chart", layout="wide", page_title= "Swimmingly Easy")

vect = TfidfVectorizer()



#Functions
def preprocess(words):
    # Finds the root/stem of the word
    # Ex. connecting - > connect
    wordNet = WordNetLemmatizer()
    # Puts everything back together, back into a string
    lemWords = ""
    for token,tag in pos_tag(word_tokenize(words)):
        pos=tag[0].lower()
        
        if pos not in ['a', 'r', 'n', 'v']:
            pos='n'
        lemWords += " " + wordNet.lemmatize(token,pos)

    return(lemWords)

# way to loop 
def compareStr(str1, str2):
    score = len(str1)
    for i,j in zip(str1,str2):
        if i != j:
            score-=1

    return score





# Start of streamlit stuff
st.title("Swimmingly Easy")


# main function
similarityContainer = st.container()

similarityContainer.subheader("Check essay answers")

ans = similarityContainer.text_input("Answer key",value="Enter your essay answer from an answer key.")
student = similarityContainer.text_input("Student answer",value="Enter the student's essay answer.")

#creates these lists only at the beginning
# doesn't reset till you close tab
if 'studentScores' not in st.session_state:
    st.session_state.studentScores = []
if 'studentMcScores' not in st.session_state:
    st.session_state.studentMcScores = []


button = similarityContainer.button("Check similarity!")
if button:
    if not ans or not student:
        st.error("One of the documents is of a null value")
    else:

        ans = preprocess(ans)
        student = preprocess(student)


        #term frequency inverse document frequency
        TfidfAns = vect.fit_transform([ans])
        TfidfStudent = vect.transform([student])
    
        similarity = round(cosine_similarity(TfidfAns,TfidfStudent)[0][0] * 100,2)

        similarityContainer.write("\n Student's similarity is: {}% ".format(similarity))
        st.session_state.studentScores.append(similarity)


#multiple choice checker here
mcContainer = st.container()


mcContainer.subheader("Check mulitple choice answers")
str1 = mcContainer.text_input("Answer key string")
str2 = mcContainer.text_input("Student test string")


mcButton = mcContainer.button("Check score!")
if mcButton:

    if len(str1)==len(str2):
        total = len(str1)
        score = compareStr(str1,str2)
        st.session_state.studentMcScores.append(score)
    else:
        st.error("Two inputs are not the same length")
            

    mcContainer.write("\n Students score is: {}/{}".format(score,total))


with st.expander("What does this do?"):
    st.markdown(""" 
We have three main features:

- A written question checker
- A multiple choice checker
- A student data visualizer


The written question checker allows for teachers to seamlessly check long/short written question answers by providing the answer key’s example response. This allows the teacher to be more efficient with their work as well as avoid tedious grading of essays and tests.

The multiple-choice checker is an easy way for the teacher to automatically check multiple-choice answers. It is a super simple design that prioritizes usability. 

The data visualizer runs in the background, collecting the data you put in (only for the current browsing session), and plots the score data for both the free-write checker and the multiple-choice checker. This allows for easy analysis of academic data, and helps with the catching of academic dishonesty, and just gives an overall view of how well a particular class is doing.

    """)
with st.expander("How does this work?"):
    st.markdown("""


    When you enter your answer key and student work, we do a few things with that data. First, we apply some lemmatizing on both texts. This basically means we basically take a word and convert is back to its simplest form (studying to study, going to go, etc.).
    Then, we transform it into a vector. Since computers cannot process words and vocabulary, we must transform all textual data into a vector of numbers representing word counts. After we do that, we transform the vector into a sparse matrix using TF-IDF or
    Term Frequency-Inverse Document Frequency. This basically is a mathematical way to take words and reflect how important that word is across all documents provided (in this case, your answer key and the student's answer).

    Once we have these two sparse matrices with TF-IDF features, we can then run a cosine similarity algorithm on it. This mathematically finds the similarity of two documents, irrespective of their size (by finding the cosine of the angle between the two vectors/matrices).

    We then return to you the cosine similarity, for your use.

    If you didn't understand any of that, it is perfectly fine. Our job is to understand it, your job is to teach :).
    """)

st.sidebar.title("Student Grade Plots")

# Essay scores: st.session_state.studentScores
# Mc scores : st.session_state.studentMcScores
# Code for bar graphs for written response
student_number = []
student_mcnumber=[]
for x in range(len(st.session_state.studentScores)):
    student_number.append("Student" + str(x))


S = pd.Series(st.session_state.studentScores, index=student_number)
df = pd.DataFrame({'index' : S.index,
                    'values': S.values})
fig = px.bar(df, x="index", y="values", title="Student Similarity Scores" )

st.sidebar.plotly_chart(fig,use_container_width=True)

# Code for creating visuals for MC
for i in range(len(st.session_state.studentMcScores)):
    student_mcnumber.append("Student" + str(i))

# bar graph, x,y
S2 = pd.Series(st.session_state.studentMcScores, index=student_mcnumber)
df2 = pd.DataFrame({'index' : S2.index,
                    'values': S2.values})
fig2 = px.bar(df2, x="index", y="values", title="Student Multiple Choice Scores" )

st.sidebar.plotly_chart(fig2,use_container_width=True)
