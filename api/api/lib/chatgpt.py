import json
import random
from json import JSONDecodeError

import openai

from api.constants import ENVConstants
from api.lib.config import get_env
from api.lib.movies import emoji_movies


class ChatGPTManager:
    def __init__(self):
        self.model = "gpt-3.5-turbo"
        # self.model = "text-davinci-003"
        openai.api_key = get_env(ENVConstants.OPENAI_API_KEY)
        self.game_helper_content = f'''
Act like a movie emoji game helper program which takes numbers as inputs. 
When I give a number, you will generate that many movie name and emojis in a json array. For example if 
 I were to give the number 2, the result will be of the format: 
`[{{"<emoji_representation>": "<movie_name>"}}, {{"<emoji_representation>": "<movie_name>"}}]`.  
The movie name should be very very easy to guess from the emoji. 
Use more than a couple of emojis for each movie name so that it makes easier to guess the movie.
        '''
        self.result_helper_content = f'''
Act like a movie emoji game helper program which takes an input. The input will have two parts. One part will be 
a list of movies and their emoji representations. The other part will be an emoji representation from the above list 
and the movie name which is guessed by the users. You have to check if the guess is right or wrong. If it is right,  
reply with `yes` and if the guess is wrong, reply with `no`. 
The reply shouldn't have anything part from either `yes` or `no`.
        '''

    def get_movie_names_in_emoji_repr(self, count=10) -> list[dict[str:str]]:
        """
        Gets the list of movie emoji dictionary in the required format
        Args:
            count: Number of movies

        Returns:

        """
        prompt = {
            "role": "system",
            "content": self.game_helper_content
        }
        movie_emojis_message = {
            "role": "user",
            "content": str(count)
        }
        messages = [
            prompt,
            movie_emojis_message
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        if choices := response.choices:
            content = choices[0].message.content
            content = content.strip()
            json_start_index = content.find("[")
            json_end_index = content.find("]")
            content = content[json_start_index:json_end_index + 1]
            content = json.loads(content)
            movies = []
            for item in content:
                emoji = list(item.keys())[0]
                movie = {
                    "emoji": emoji,
                    "movie_name": item[emoji]
                }
                movies.append(movie)
            print(movies)
            return movies
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
        prompt = {
            "role": "system",
            "content": self.result_helper_content
        }
        question = f"The list of movies and their emoji representations is \n {movie_list}, the emoji is `" \
                   f"{emoji}` and the guessed movie name is `{guessed_name}`. Is this guess correct?"
        question_message = {
            "role": "user",
            "content": question
        }
        messages = [
            prompt,
            question_message
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        if choices := response.choices:
            message_content = choices[0].message
            message = message_content.content
            content = message.strip().lower()
            if content.startswith("yes"):
                return True
            else:
                return False
