from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from words import WORDS

# from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import os


class DeepChat:
    def __init__(self, input_string: str, history: "History") -> None:
        """
        Initialize a DeepChat instance.

        Parameters:
            input_string (str): The input string provided by the user.
            history (History): The conversation history object to maintain the chat history.
        """
        # Store the conversation history and append the user's input
        self.conversation_history = history
        self.conversation_history.conversation_history.append(
            {"role": "user", "content": input_string}
        )
        # Start the chat with the current input and conversation history
        self.chat(input=self.conversation_history.conversation_history)

    def chat(self, input: list[dict[str, str]]) -> None:
        """
        Engage in a chat with the AI model and handle its response.

        Parameters:
            input (list[dict[str, str]]): A list containing the chat history with user and assistant messages.

        Process:
            1. Create an instance of the OpenAI client using the provided API key and base URL.
            2. Call the chat completion API to obtain the assistant's reply based on the provided conversation history.
            3. Stream the response and process it chunk by chunk, printing the assistant's reply in real-time.
            4. Append the assistant's reply to the conversation history for future reference.
        """
        # Initialize the OpenAI client with API key and base URL
        client = OpenAI(
            api_key="sk-4791dd28e1fd4527be321350c1591194",
            base_url="https://api.deepseek.com",
        )
        # Request the chat completion response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=input,
            stream=True,
            temperature=1.0,
            max_tokens=8192,
        )
        assistant_reply = ""
        print("agent: ", end="", flush=True)

        # Iterate over each chunk of the response from the assistant
        for chunk in response:
            response_content = chunk.choices[0].delta.content

            # If there's content in the response, print it immediately
            if response_content is not None:
                print(response_content, end="", flush=True)
                assistant_reply += response_content

        print()  # Move to the next line after the assistant's reply is finished
        # Append the assistant's complete reply to the conversation history
        self.conversation_history.conversation_history.append(
            {"role": "assistant", "content": assistant_reply}
        )


class History:
    def __init__(self) -> None:
        """
        Initialize the conversation history.

        Initializes the conversation history with a system message that provides context for the assistant.
        Also sets up a prompt session for handling user input.
        """
        # Set initial conversation history with a system context message
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        self.completer = WordCompleter(WORDS)

        # Define a custom style for prompt display
        self.custom_style = Style.from_dict(
            {
                "prompt": "fg:ansiblue bold",
            }
        )
        history_file = os.path.expanduser("~/AppData/Local/cache/.deep-seek-history")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        # Create a PromptSession for handling user inputs
        self.session = PromptSession(
            "deep-chat> ",
            multiline=True,
            # key_bindings=kb,
            history=FileHistory(history_file),
            completer=self.completer,
            auto_suggest=AutoSuggestFromHistory(),
            style=self.custom_style,
            bottom_toolbar=lambda: HTML(
                '<b><style bg="ansired">Press "q" to quit, "esc + enter" to send content, "enter" to new line! </style></b>'
            ),
        )

    def multiple_input(self) -> str:
        """
        Get multiple lines of user input.

        Returns:
            str: The complete string input provided by the user.

        Process:
            1. Prompt the user to enter input, allowing for multiline entries.
            2. Capture and return the user's input as a single string.
        """

        user_input = self.session.prompt(multiline=True)

        return user_input

    def print_blue(self, text: str) -> None:
        """
        Print text in blue color.

        Parameters:
            text (str): The text to be printed in blue.
        """
        print(f"\033[34m{text}\033[0m")


if __name__ == "__main__":
    # Initialize the conversation history instance
    history = History()

    # Print welcome message and instructions
    history.print_blue(
        """>>> Welcome to the deep-chat AI agent <<<

"""
    )

    while True:
        # Retrieve user input using the history's multiple_input method
        content = history.multiple_input().strip()

        # Check if the user wants to quit the chat
        if content.lower() in ["quit", "q"]:
            print("agent: Goodbye!")
            break  # Exit the loop and terminate the chat
        else:
            # Start a new DeepChat instance with the provided user input
            DeepChat(content, history)
