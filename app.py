# import streamlit as st
# from holiday_agent import generate_response
# from pydantic import BaseModel
# st.title("Simple chat")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         response = st.write(generate_response(prompt))
#     # Add assistant response to chat history
    

#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     st.session_state.messages.append({"role": "assistant", "content": response})

# import streamlit as st
# from holiday_agent import generate_response
# from pydantic import BaseModel

# st.title("Simple chat")

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
    
#     # Generate assistant response and display it
#     response = generate_response(prompt)
#     if response:  # Ensure response is not None
#         with st.chat_message("assistant"):
#             st.markdown(response)
        
#         # Add user and assistant messages to chat history
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         st.session_state.messages.append({"role": "assistant", "content": response})
import streamlit as st
from holiday_agent import generate_response
from pydantic import BaseModel
import os
from PIL import Image

st.title("Holiday Agent")
st.text("Built by Tanmay Chakraborty")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# # Function to remove last saved image
# def remove_last_image(directory="images/"):
#     if os.path.exists(directory):
#         files = sorted([f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))])
#         if files:
#             last_image_path = os.path.join(directory, files)
#             os.remove(last_image_path)
#             return True
#     return False


import os

def remove_all_images(directory="images/"):
    """
    Removes all image files in the specified directory.

    Parameters:
    - directory (str): The directory from which to remove all images.

    Returns:
    - bool: True if images were found and removed, False if no images were found.
    """
    if os.path.exists(directory):
        files = [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            for file in files:
                image_path = os.path.join(directory, file)
                os.remove(image_path)
            return True
    return False



# Function to check if there are images to display
def get_image_paths(directory="images/"):
    if os.path.exists(directory):
        return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            image_paths = get_image_paths()
            for image_path in image_paths:
                image = Image.open(image_path)
                st.image(image)

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Remove last saved image if it exists
    remove_all_images()
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response and display it
    response = generate_response(prompt)
    print(response)
    if response:  # Ensure response is not None
        with st.chat_message("assistant"):
            st.markdown(response)
            
            # Check if new images are available and display them
            image_paths = get_image_paths()
            if image_paths:
                for image_path in image_paths:
                    image = Image.open(image_path)
                    st.image(image)
        
        # Add user and assistant messages to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response})
