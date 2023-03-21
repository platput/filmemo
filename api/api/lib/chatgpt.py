import json
import random

import openai

from api.constants import ENVConstants
from api.lib.config import get_env
from api.lib.movies import emoji_movies


class ChatGPTManager:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        openai.api_key = get_env(ENVConstants.OPENAI_API_KEY)
        self.system_message = {
            "role": "system",
            "content": "you are a very liberal game coordinator for a movie emoji guessing game."
        }

    def get_movie_names_in_emoji_repr(self, count=10) -> list[dict[str:str]]:
        """
        Gets the list of movie emoji dictionary in the required format
        Args:
            count: Number of movies

        Returns:

        """
        movie_emojis_message = {
            "role": "user",
            "content": f'I need a list of {count} movie names and their emoji representation. This is for a movie '
                       f'guessing game. Here, each of the item in the list should be a dictionary where there will be '
                       f'2 key value pairs. Keys are "emoji" and "movie_name". The value of emoji will be the emoji '
                       f'and the value of movie_name will be the name of the movie users have to guess from the emoji '
                       f'representation. The movie names should be very very easy to guess from the emojis.'
        }
        messages = [
            self.system_message,
            movie_emojis_message
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        if choices := response.choices:
            content = choices[0].message
            content = content.strip()
            json_start_index = content.find("[")
            json_end_index = content.find("]")
            content = content[json_start_index:json_end_index + 1]
            content = json.loads(content)
            return content
        else:
            return random.choices(emoji_movies, k=count)

    def check_if_right_guess(self, movie_list: list[dict[str:str]], emoji: str, guessed_name: str) -> bool:
        """
        Checks if the given movie name is a correct guess for the given emoji form the movie list.
        Args:
            movie_list: List of movie name and emoji dictionary
            emoji: Emoji for against which the movie name guess has to be checked
            guessed_name: Guessed movie name from the emoji

        Returns:
            Boolean value; True if correct guess, False otherwise
        """
        question = f"given the below list of dictionary with emojis and the movie names from a movie name guessing " \
                   f"game. check if the guess is correct. If the guess is right, start the answer with `yes ` or if " \
                   f"the guess is wrong start the reply with `no `. The list is \n {movie_list}, the emoji is `" \
                   f"{emoji}` and the guessed movie name is `{guessed_name}`"
        question_message = {
            "role": "user",
            "content": question
        }
        messages = [
            self.system_message,
            question_message
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        if choices := response.choices:
            content: str = choices[0].message
            content = content.strip().lower()
            if content.startswith("yes"):
                return True
            else:
                return False