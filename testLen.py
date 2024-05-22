import streamlit as st

st.set_page_config(layout="wide")


MIN_SCREEN_WIDTH = 1000


# Define a media query in CSS to target larger screens
css = """
<style>
@media screen and (min-width: 1000px) {
    #app-container {
        display: block;
    }
    #screen-size-warning {
        display: none;
    }
}
@media screen and (max-width: 999px) {
    #app-container {
        display: none;
    }
    #screen-size-warning {
        display: block;
    }
}

div[data-testid="stMarkdownContainer"] p {
  font-size: 22px; /* Adjust the font size as needed */
}

</style>
"""


try:
  # Check if streamlit_js_eval is installed
  from streamlit_js_eval import streamlit_js_eval
except ModuleNotFoundError:
  print("streamlit_js_eval library not found. Please install it using pip: pip install streamlit_js_eval")
  st.error("Please install streamlit_js_eval library to enable screen size detection.")
  exit(1)



# Use streamlit_js_eval to get screen width from JavaScript
def get_screen_width():
  try:
    screen_width = streamlit_js_eval(js_expressions="window.outerWidth", key="SCREEN_WIDTH", want_output=True)
    return screen_width
  except Exception as e:
    print(f"Error getting screen width: {e}")
    return None

# Apply the CSS
st.markdown(css, unsafe_allow_html=True)

# Check if the parameter indicating a larger screen is present in the URL query parameters

screen_width = get_screen_width()
print(screen_width)

if screen_width is not None and screen_width >= MIN_SCREEN_WIDTH:
    # Display app content for larger screens
    import pandas as pd
    import time
    # import ollama
    # from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOpenAI
    from langchain_community.tools import YouTubeSearchTool
    # from langchain_community.chat_models import ChatOllama
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, AIMessage

    # @st.cache_resource
    # def load_model():
    #     llm = ChatOllama(model="llama3")
    #     return llm

    @st.cache_resource
    def load_model():
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        return llm

    llm = load_model()
    youtube_tool = YouTubeSearchTool()
    correct_icon = ":white_check_mark:"  # Streamlit icon for correct answer
    incorrect_icon = ":x:"  # Streamlit icon for incorrect answer


    st.markdown("""<style> 
                    /* Add this CSS to increase font size */
                    [data-testid="stMarkdownContainer"] {
                        font-size: 28px; /* Adjust the font size as needed */
                    }

                    .st-emotion-cache-4d1onx p {
                        font-size: 22px; /* Adjust the font size as needed */
                    }
                </style>
                """, unsafe_allow_html=True

            )


    # Error handling for missing Excel file
    try:
        # Read questions and options from Excel
        df = pd.read_excel("ChattyTeacher-test1.xlsx")
        questions = df["Question"].tolist()
        options = df[["Option1", "Option2", "Option3", "Option4"]].values.tolist()
        answers = df["Answer"].tolist()
        question_type = df['QuestionType'].tolist()
        topics = df['Topic'].drop_duplicates().tolist()
        number_correct = df['NumberCorrect'].tolist()
    except FileNotFoundError:
        st.error("Error: 'Untitled.xlsx' file not found. Please ensure the file exists and is in the same directory as your Python script.")
        exit()

    # Session state variables
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
        st.session_state.score = 0
        st.session_state.current_question = 0
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0
        st.session_state.submitted = False
        st.session_state.messages = []
        st.session_state.ai_message_bool = False
        st.session_state.ai_message = ""
        st.session_state.chat_number = 0
        st.session_state.quiz_started = False

    def load_data(selected_page):
        filtered_df = df[df['Topic'] == selected_page]
        return filtered_df

    def navigation_bar():
        selected_page = st.sidebar.selectbox("Select Quiz", ["Home"] + topics, disabled=st.session_state.quiz_started)
 
        st.session_state.current_page = selected_page

        print("inside nav bar")
        


    navigation_bar()  # Call the navigation bar function

    
    @st.experimental_dialog("These videos may help")
    def vote(item):
        display_video()

    def launch_modal():
        vote("A")

    def chatter_func():
        question = questions[st.session_state.current_question]
        option = options[st.session_state.current_question]
        message_to_ai = str(question) + str(option) + ". What is the correct answer."
        st.session_state.ai_message_bool = True
        st.session_state.ai_message = message_to_ai


    def update_func():
        if st.session_state.current_question == len(questions)-1:
            st.session_state.quiz_started = False
        else:
            st.session_state.quiz_started = True
        st.session_state.current_question += 1
        st.session_state.submitted = False
        st.session_state.messages = []
        st.session_state.chat_number = 0

    def display_video():
        recommended_videos = youtube_tool.run(str(questions[st.session_state.current_question]) + ", 1")
        print(recommended_videos)
        # Split the string by comma (assuming comma separation between elements)
        url_strings = recommended_videos.strip('[]').split(',')

        # Remove extra quotes around each URL (assuming double quotes)
        encoded_links = [url.strip('"') for url in url_strings]

        # Now you have a list of URLs
        print(encoded_links)

        recommended_videos_answer = youtube_tool.run(str(answers[st.session_state.current_question]) + ", 1")
        print(recommended_videos_answer)
        # Split the string by comma (assuming comma separation between elements)
        url_strings_answer = recommended_videos_answer.strip('[]').split(',')

        # Remove extra quotes around each URL (assuming double quotes)
        encoded_links_answer = [url.strip('"') for url in url_strings_answer]

        st.subheader("Recommended Videos:")
        st.write("Learn the idea from one of these videos")
        link_text = "Check it out !"
        print("Starting.........")
        video_url = encoded_links[0]
        video_url_answer = encoded_links_answer[0]

        without_quotes = video_url.strip("'")
        without_quotes = video_url.strip(" ")
        without_quotes = without_quotes.strip("'\n")

        without_quotes_answer = video_url_answer.strip("'")
        without_quotes_answer = video_url_answer.strip(" ")
        without_quotes_answer = without_quotes_answer.strip("'\n")

        print("Without:", without_quotes)

        v1, v2 = st.columns(2)
        with v1:
            st.video(str(without_quotes))
            # st.write(f"{link_text} ([{video_url}])")
            st.write(f"[Watch in YouTube]({without_quotes})")

        with v2:
            st.video(str(without_quotes_answer))
            # st.write(f"{link_text} ([{video_url}])")
            st.write(f"[Watch in YouTube]({without_quotes_answer})")


    def display_chat():
        # st.markdown('''
        #         <style>
        #         .st-emotion-cache-1xw8zd0 {height : 80vh;
        #               width : 100%}
        #         </style>''', unsafe_allow_html = True)
        
        with st.container(border=True, height=700):
            st.subheader("Chat with AI Tutor :robot_face:")
            st.write("Chat to explain question or terms for better understanding")
            st.caption(":exclamation: Inaccurate at times !")

            # Display all messages in chat history
            for message in st.session_state.messages:
                if isinstance(message, HumanMessage):
                    with st.chat_message("Human"):
                        st.markdown(message.content)
                else:
                    with st.chat_message("AIMessage"):
                        st.markdown(message.content)

            user_message = st.chat_input(placeholder="Type your message here")

            if st.session_state.ai_message_bool:
                user_message = st.session_state.ai_message

            # Add user message to chat history
            if user_message:
                if st.session_state.ai_message_bool:
                    st.session_state.messages.append(HumanMessage("Explanation for the question shown. Feel free to ask more"))
                else:
                    st.session_state.messages.append(HumanMessage(user_message))

                with st.spinner("Thinking...."):
                    template = """
                        You are a helpful assistant. 

                        You are built into this webpage on the right. On the left is a question and options window.
                        
                        Answer the user question based on the given question and options. Refer to the chat history where necessary.

                        Chat History: {chat_history}

                        Question: {question}

                        options: {options}

                        User question: {user_question}

                        Keep your answer to the point. Keep explanations strictly short and in point form !

                        Only explain more if user asks.
                    """
                    prompt = ChatPromptTemplate.from_template(template)
                    chain = prompt | llm | StrOutputParser()

                    question = questions[st.session_state.current_question]
                    option = options[st.session_state.current_question]
                    
                    if st.session_state.chat_number < 5:

                        st.session_state.chat_number += 1
 
                        response = chain.stream({
                            "user_question": user_message, 
                            "chat_history": st.session_state.messages,
                            "question": question,
                            "options":option
                        })

                        with st.chat_message("AIMessage"):
                            # for res in response:
                            #     print(f"Received partial response: {res}")
                            fullres = st.write_stream(response)


                    else:
                        fullres = "Hi ! I can only respond up to 5 messages for now. You can also watch the videos to learn more."


                    st.session_state.messages.append(AIMessage(fullres))
                    
                st.session_state.ai_message_bool = False
                st.rerun()




    def show_results():
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Correct {correct_icon}", st.session_state.correct_answers)
        col2.metric(f"Wrong {incorrect_icon}", st.session_state.incorrect_answers)
        col3.metric(f"Score :school_satchel:", f"{(st.session_state.correct_answers/len(questions))*100:.2f} %")

    def display_quiz():

        with st.container(border=True):

            # Display progress bar
            progress = (st.session_state.current_question) / len(questions)
            st.progress(progress, f"Progress: {int(progress * 100)}%")

            # Display score with icons
            show_results()

            # Check if all questions have been answered
            if st.session_state.current_question == len(questions):
                st.success(f"You have completed the quiz! Your score is {(st.session_state.correct_answers/len(questions))*100:.2f} %")
                st.balloons()
                st.warning("Select another quiz on the left")
                st.session_state.score = 0
                st.session_state.current_question = 0
                st.session_state.correct_answers = 0
                st.session_state.incorrect_answers = 0
                return

        with st.container(border=True):
            # Display current question and options with unique keys
            question = questions[st.session_state.current_question]
            qn_text = f"{st.session_state.current_question+1}. {question}"

            if question_type[st.session_state.current_question] == "MCQ":
                user_answer = st.radio(qn_text, options[st.session_state.current_question], key=f"question_{st.session_state.current_question}")
            elif question_type[st.session_state.current_question] == "TF":
                user_answer = st.radio(qn_text, options[st.session_state.current_question][:2], key=f"question_{st.session_state.current_question}")
            else:
                st.write(question)
                selected_options = []
                for option in options[st.session_state.current_question]:
                    selected_options.append(st.checkbox(option))

            if st.session_state.submitted:
                print("Submitted")
                if question_type[st.session_state.current_question] == "Multi-Select":
                    user_selections = [option for option, is_checked in zip(options[st.session_state.current_question], selected_options) if is_checked]
                    correct_answer = number_correct[st.session_state.current_question]
                    correct_answer = correct_answer.split(",")
                    total_correct = len(correct_answer)
                    num_correct=0
                    
                    idx = 0
                    for ans in correct_answer:
                        if options[st.session_state.current_question][int(ans)-1] in user_selections:
                            num_correct+=1

                    if num_correct == total_correct and len(user_selections) == total_correct:
                        user_answer = correct_answer
                    else:
                        user_answer = 0
                        correct_answer = "The correct answer is options " + ','.join(correct_answer)
                else:
                    correct_answer = answers[st.session_state.current_question]

                if user_answer == correct_answer:
                    st.success("Correct!")

                else:
                    st.error(f"Incorrect. The answer is {correct_answer}")

                # Next button to move on (only enabled after answering)
                b1, b2, b3 =  st.columns([1,2,2])
                with b1:
                    st.button("Next", on_click=update_func, type="primary") 
                with b2:
                    st.button("Ask AI :robot_face: ", on_click=chatter_func)
                with b3:
                    st.button("Show Videos :video_camera:", on_click=launch_modal)


            else:
            
                print("Not submitted")
                submit_button = st.button("Submit Answer", key="submit_button")
                if submit_button and not st.session_state.submitted:
                    st.session_state.submitted = True
                    if question_type[st.session_state.current_question] == "Multi-Select":
                        user_selections = [option for option, is_checked in zip(options[st.session_state.current_question], selected_options) if is_checked]
                        correct_answer = number_correct[st.session_state.current_question]
                        correct_answer = correct_answer.split(",")
                        total_correct = len(correct_answer)
                        num_correct=0
                        
                        for ans in correct_answer:
                            if options[st.session_state.current_question][int(ans)-1] in user_selections:
                                num_correct+=1

                        if num_correct == total_correct and len(user_selections) == total_correct:
                            user_answer = correct_answer
                        else:
                            user_answer = 0


                    else:
                        correct_answer = answers[st.session_state.current_question]

                    if user_answer == correct_answer:
                        st.success("Correct!")
                        # st.session_state.score += 1
                        # Update score incrementally
                        st.session_state.correct_answers += 1

                    else:
                        st.error(f"Incorrect. The answer is {correct_answer}")
                        st.session_state.incorrect_answers += 1

                    st.rerun()

                    # Next button to move on (only enabled after answering)
                    b1, b2, b3 =  st.columns([1,2,2])
                    with b1:
                        st.button("Next", on_click=update_func, type="primary") 
                    with b2:
                        st.button("Ask AI :robot_face: ", on_click=chatter_func)
                    with b3:
                        st.button("Show Videos :video_camera:", on_click=launch_modal)

                    # recommended_videos = ["https://www.youtube.com/watch?v=...", "https://www.youtube.com/watch?v=..."]  # Replace with actual video URLs

                        


    # Display content based on current page
    if st.session_state.current_page == "Home":
        # Display home page content
        st.header("Welcome to the :robot_face: AI Quiz App!", divider='rainbow')
        st.subheader("This app allows you to test your knowledge through a quiz.")
        st.write("It will provide you automatic feedback and allow you to chat with an AI agent to know more")
        st.write(":arrow_backward: Select the topic you like to practice using the menu on the  left")

    else:
        # Display quiz content
        col_1, col_2 = st.columns([0.7, 0.3])
        print(st.session_state.current_page, "hi prak")
        filtered_df = load_data(st.session_state.current_page)
        questions = filtered_df["Question"].tolist()
        options = filtered_df[["Option1", "Option2", "Option3", "Option4"]].values.tolist()
        answers = filtered_df["Answer"].tolist()
        question_type = filtered_df['QuestionType'].tolist()
        number_correct = filtered_df['NumberCorrect'].tolist()

        with col_1:
            display_quiz()
        with col_2:
            display_chat()


    # Display final result after completing the quiz
    if st.session_state.current_page == "comptia a+" \
            and st.session_state.current_question == len(questions):
        st.balloons()  # Celebrate completion (optional)
else:
    print("Small screen !")
    st.markdown("<div id='screen-size-warning'>This app is best viewed on a larger screen. Please access it from a laptop, desktop or a device with a larger screen.</div>", unsafe_allow_html=True)

