import langroid as lr
import langroid.language_models as lm
from langroid.agent.tools.orchestration import FinalResultTool
from fire import Fire

import os
import json
import colorama
from colorama import Fore, Style

from tba.tba_api import TheBlueAllianceAPI
from tba.tba_tool import FetchTeamInfo, FetchTeamEvents, FetchAllEvents

# Initialize colorama
colorama.init(autoreset=True)

# Initialize the TBA API
tba_api = TheBlueAllianceAPI(os.getenv("TBA_API_KEY"))
        
def run(model: str = ""):
    lm_config = lm.OpenAIGPTConfig(
        chat_model="local/localhost:1234/v1",
    )
    
    # Backend LLM configuration
    backend_agent_config = lr.ChatAgentConfig(
        llm=lm_config,
        system_message="""
        You are an assistant for FIRST Robotics information. Your task is to:
        1. Understand the user's query about a FIRST Robotics team.
        2. Decide which tool to use to get the information necessary for a response.
        3. Use the selected tool to get the information.
        After receiving the team information, pass it along with the original query to the response generation LLM.
        Do not generate any response about the team yourself. Only use the selected tool to get real data.

        IMPORTANT: If you don't have all the parameters, use the default value None.
        Tools should be called in the following format:
        {
            "request": tool_name,
            "parameter_name": parameter
        }
        """,
    )
    backend_agent = lr.ChatAgent(backend_agent_config)

    backend_agent.enable_message(FetchTeamInfo)
    backend_agent.enable_message(FetchTeamEvents)
    backend_agent.enable_message(FetchAllEvents)

    # Response generation LLM configuration
    response_agent_config = lr.ChatAgentConfig(
        llm=lm_config,
        system_message="""
        You are a FIRST Robotics expert. Use the provided team information to answer questions about the team.
        Provide a comprehensive and engaging response based on the given information and the user's original query.
        Only use the information provided in the team data. Do not invent or assume any additional information.
        """,
    )
    response_agent = lr.ChatAgent(response_agent_config)

    def backend_callback(message: str):
        """
        Handles interaction with the backend agent (fetching data from api).
        """
        # Beckend LLM processes the query
        backend_task = lr.Task(backend_agent, interactive=False)
        backend_result = backend_task[FinalResultTool].run(message)

        if isinstance(backend_result, FinalResultTool) and hasattr(backend_result, 'api_data'):
            api_data = backend_result.api_data.data
            
            # Prepare context for the response generation LLM
            context = f"""
            Original Query: {message}
            Retrieved Information: {json.dumps(api_data, indent=2)}

            Instructions:
            1. Analyze the original query and the retrieved information.
            2. Provide a concise and informative answer that directly addresses the user's question.
            3. Focus on the most relevant details from the retrieved information.
            4. If the retrieved information is insufficient or irrelevant, acknowledge this and suggest what additional information might be needed.
            5. Ensure your response is clear, accurate, and to the point.
            """

            # Response generation LLM creates the final response
            response = response_agent.llm_response(context)
            return response.content
        else:
            return f"Error: {backend_result}"

    def interactive_chat():

        print()
        print("\033[1;36m" + "Welcome to Chicken AI - A FIRST Robotics Expert" + "\033[0m")
        print("\033[3;32m" + "Gain access to real, up-to-date information about FRC teams and events" + "\033[0m")
        print("""                                                                                      
 ██████╗██╗  ██╗██╗ ██████╗██╗  ██╗███████╗███╗   ██╗       █████╗ ██╗
██╔════╝██║  ██║██║██╔════╝██║ ██╔╝██╔════╝████╗  ██║      ██╔══██╗██║
██║     ███████║██║██║     █████╔╝ █████╗  ██╔██╗ ██║█████╗███████║██║
██║     ██╔══██║██║██║     ██╔═██╗ ██╔══╝  ██║╚██╗██║╚════╝██╔══██║██║
╚██████╗██║  ██║██║╚██████╗██║  ██╗███████╗██║ ╚████║      ██║  ██║██║
 ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝      ╚═╝  ╚═╝╚═╝                                        
        """)
        print("\033[1;36m" + "Powered by The Blue Alliance API" + "\033[0m")
        print("\033[3;32m" + "Type 'exit' or 'quit' to terminate chat at any time" + "\033[0m")
        print()
        while True:
            # Get user input
            user_query = input(Fore.GREEN + "User: " + Style.RESET_ALL)
            
            # Handle exit condition
            if user_query.strip().lower() == 'exit' or user_query.strip().lower() == 'quit':
                print(Fore.MAGENTA + "\nThank you for chatting with me about FIRST Robotics. Have a great day!")
                break
            
            # Call the backend function and handle results
            try:
                result = backend_callback(user_query)
            except Exception as e:
                # Handle any unexpected errors gracefully
                print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)

    # Start the interactive chat
    interactive_chat()

if __name__ == "__main__":
    Fire(run)