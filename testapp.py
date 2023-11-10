import streamlit as st
import openai
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with your API key
client = OpenAI()

# Upload a file with an "assistants" purpose
file = client.files.create(
    file=open("Kinton_Reviews_1500.jsonl", "rb"),
    purpose='assistants'
)

# Add the file to the assistant
assistant = client.beta.assistants.create(
    name="Kinton Ramen Reviewer",
    instructions="You are an assistant that reads the entire file of Kinton Ramen restaurant data and reviews. You are to analyze \
                the each restaurant based on scores and individual reviews and answer incoming questions and queries from the user.",
    model="gpt-4-1106-preview",  # specify the model here
    tools=[{"type": "code_interpreter"}, {"type": "retrieval"}]
)

# Create a thread to handle the conversation
thread = client.beta.threads.create()

# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Streamlit app layout
st.title("Kinton Ramen Reviewer Chatbot")

# Text input for user question
user_input = st.text_input("Type your question here:", key="input")
st.caption("Note: Type 'exit' and click send to end the chat.")

# Function to send message and get response
def send_message_get_response(user_input):
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
        file_ids=[file.id]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please try to answer as best as you can. If unsure or query has nothing to do with data, state that."
    )

    while True:
        time.sleep(2)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'completed':
            break

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    return messages.data[0].content[0].text.value

# Function to update conversation
def update_conversation(user_question, bot_answer):
    st.session_state.conversation.append("User: " + user_question)
    st.session_state.conversation.append("Bot: " + bot_answer)

# Button to send the message
if st.button("Send"):
    if user_input.lower() != 'exit':
        response = send_message_get_response(user_input)
        update_conversation(user_input, response)
    else:
        st.session_state.conversation = []  # Clear the conversation
        st.write("Exiting the chat.")

# Display conversation history
for message in st.session_state.conversation:
    st.text(message)
