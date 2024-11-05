import requests
# from helper_functions.keys import WEATHER_KEY, HUGGING_FACE_KEY
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
# from langchain.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from PIL import Image
import requests
from pydantic import BaseModel
from langchain.agents import create_tool_calling_agent # set up the agent
from langchain.agents import AgentExecutor # execute agent
from langchain_openai import ChatOpenAI # call openAI as agent llm
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv
load_dotenv()
groq_api_key=os.getenv("groq_api_key")

def generate_response(question):


    api_wrapper = WikipediaAPIWrapper(top_k_results=1,lang="en")
    wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)


    # define the function
    def wikipedia_caller(query:str) ->str:
        """This function queries wikipedia through a search query."""
        return api_wrapper.run(query)

    # Input parameter definition
    class QueryInput(BaseModel):
        query: str = Field(description="Input search query")

    # the tool description
    description: str = (
            "A wrapper around Wikipedia. "
            "Useful for when you need to answer general questions about "
            "people, places, companies, facts, historical events, or other subjects. "
            "Input should be a search query."
        )


    # fuse the function, input parameters and description into a tool. 
    my_own_wiki_tool = StructuredTool.from_function(
        func=wikipedia_caller,
        name="wikipedia",
        description=description,
        args_schema=QueryInput,
        return_direct=False,
    )

    # define the function
    def extract_city_weather(city:str)->str:

        # Build the API URL
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?key=536K9BNZU5DKUZDTA2LBHVPB5&unitGroup=metric"
        # url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/west%20bengal?unitGroup=metric&key=536K9BNZU5DKUZDTA2LBHVPB5&contentType=json"

        response = requests.get(url)

        # extract response
        if response.status_code == 200:
            data = response.json()
            current_temp = data['days'][0]['temp']
            output = f"Current temperature in {city}: {current_temp}°C"
        else:
            output = f"Error: {response.status_code}"

        return output

    # Input parameter definition
    class WeatherInput(BaseModel):
        city: str = Field(description="City name")
        # insert your code here

    # the tool description
    # description: str = (
    #         # TODO: insert your code here
    #     )

    # fuse the function, input parameters and description into a tool. 
    my_weather_tool = StructuredTool.from_function(
        func=extract_city_weather,
        name="weather",
        args_schema=WeatherInput,
        description="Tool to get real time weather information",
        return_direct=False,
    )



    # def save_image_from_url(url, save_path):
    #     response = requests.get(url)
    #     response.raise_for_status()  # Ensure the request was successful
        
    #     # Open a file in binary write mode and save the image content
    #     with open(save_path, 'wb') as file:
    #         file.write(response.content)
    def save_image_from_url(url, directory, filename):
        """
        Downloads an image from a given URL and saves it to a specified directory with a user-provided filename.
        
        Parameters:
        - url (str): The URL of the image to download.
        - directory (str): The directory where the image will be saved.
        - filename (str): The name for the saved image file, including the extension (e.g., 'image.jpg').

        Returns:
        - str: The full path to the saved image if successful.
        """
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Full path for saving the image
        save_path = os.path.join(directory, filename)
        
        # Request the image from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        # Save the image content to the specified path
        with open(save_path, 'wb') as file:
            file.write(response.content)
        
        return save_path

    import requests
    def extract_hotel_details(location,checkIn,checkOut,currency="INR"):
        url = "https://airbnb-scraper-api.p.rapidapi.com/airbnb_search_stays"

        querystring = {"location":location,"checkIn":checkIn,"checkOut":checkOut,"locale":"en","currency":currency}

        headers = {
            "x-rapidapi-key": "e1436f9d66msh88b947efbcee0e4p1a1d2djsn8e6af763fcb3",
            "x-rapidapi-host": "airbnb-scraper-api.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code==200:
            info=response.json()["data"][:5]
            for idx in range(len(info)):
                save_image_from_url(info[idx]["images"][0],"images",f"1_{idx}.jpg")
            return response.json()["data"][:2]

        return "I feel due to wrong input information is not coming"

    class extract_hotel_details_Input(BaseModel):
        location: str = Field(description="Location Name")
        checkIn: str = Field(description="Check In Time")
        checkOut: str = Field(description="Check Out Time")

    my_hotel_tool = StructuredTool.from_function(
        func=extract_hotel_details,
        name="hotels",
        args_schema=extract_hotel_details_Input,
        description="Tool to get real time hotel information",
        return_direct=False,
    )


    tools = [my_own_wiki_tool, my_weather_tool, my_hotel_tool]

    llm=ChatGroq(model="llama3-groq-70b-8192-tool-use-preview",api_key=groq_api_key)
    # With this you let the agent know what its purpose is.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a holiday agent.You will have to compare all options and you need to final place for go and with justifications"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Define the agent (load the LLM and the list of tools)
    agent = create_tool_calling_agent(llm = llm, tools = tools, prompt = prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Your agent is ready.")

    question_1 = "I want to go to kolkata or bangalore and i wanted to go on 2024-12-01 and want to come back on 2024-12-10. But I am not sure where I will enjoy the most"
    # print(f"Question 1: {question_1}")
    return agent_executor.invoke({"input": question})["output"]
