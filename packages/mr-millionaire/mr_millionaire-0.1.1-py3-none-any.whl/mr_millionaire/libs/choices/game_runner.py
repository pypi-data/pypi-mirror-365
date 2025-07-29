"""Game runner choice module."""
import sys
from dataclasses import dataclass

from mr_millionaire.libs import Choice
from mr_millionaire.libs.choices.history_manager import HistoryManager
from mr_millionaire.libs.config_handler import ConfigHandler
from mr_millionaire.libs.lib_constant import Breaks, GameValues, LLMPrompts, Messages
from mr_millionaire.libs.llm_handler import LLMHandler
from mr_millionaire.libs.memory_handler import MemoryHandler
from mr_millionaire.libs.schema import FiftyFiftyAnswer, PhoneFriendAnswer, PlayerName, QuestionSchema
from mr_millionaire.libs.utility import get_user_input, print_strikethrough


@dataclass
class Question:

    """Question dataclass."""

    question_no: int
    question: str
    choices: list[str]
    correct_answer: str


class GameRunner(Choice):

    """Game runner choice class."""

    def __init__(self) -> None:
        """Constructor for GameRunner."""
        self.llm_handler = LLMHandler()
        self.config = ConfigHandler()
        self.history = HistoryManager()
        self.mem = MemoryHandler()
        self.prize_won = 0
        self._current_question = None
        self._question_history = []
        self._question_history_prompt = ""
        self._question_no = 0
        self._life_lines_used = {}
        self._player_name = ""


    def ask_question(self) -> None:
        """Get the question to the user.

        Returns:
            Question: next question to be asked to the player.

        """
        self._question_no += 1
        self._current_question = self.generate_next_question()
        self.mem.add_to_memory(self._current_question.question)
        self.show_question(self._current_question)
        self._question_history.append(self._current_question)

    def continue_or_drop(self) -> None:
        """Ask the user to continue or drop."""
        user_input = input(f"Press any key to continue or 'q' to leave with ${self.prize_won} : ")
        if user_input == "q":
            print(Messages.player_quit.format(player=self._player_name, money=self.prize_won))
            self.history.write_to_history(self._player_name, self.prize_won)
            sys.exit(1)

    def fifty_fifty(self) -> list:
        """Reduce the choice to 2 from 4.

        Returns:
            list: list of possible option.

        """
        fifty_fifty_prompt = LLMPrompts.fifty_fifty_prompt.format(
            question=self._current_question.question,
            choices=", ".join(self._current_question.choices),
        )
        fifty_fifty_answers = self.llm_handler.request_llm(
            fifty_fifty_prompt, FiftyFiftyAnswer,
        )
        return fifty_fifty_answers[GameValues.choices]

    def generate_next_question(self, *add_prompt: str) -> Question:
        """Generate next question to be asked to the player."""
        question_prompt = self._construct_question_prompt(*add_prompt)
        next_question = Question(
            question_no=self._question_no, **self.llm_handler.request_llm(question_prompt, QuestionSchema),
        )

        if self.mem.already_seen(next_question.question):
            self.mem.found_in_memory.append(next_question.question)
            return self.generate_next_question(*self.mem.found_in_memory)
        return next_question


    def phone_a_friend(self) -> str:
        """AI friend who can help you with an answer.

        Return:
            str: Answer for the question.

        """
        phone_a_friend_prompt = LLMPrompts.phone_a_friend_prompt.format(
            question=self._current_question.question,
            choices=", ".join(self._current_question.choices),
        )

        friend_answer = self.llm_handler.request_llm(
            phone_a_friend_prompt, PhoneFriendAnswer,
        )
        return friend_answer[GameValues.answer]

    def process_lifeline(self, ll_choice: int) -> None:
        """Process lifeline choice.

        Args:
            ll_choice (int): Life line choice chosen by user.

        """
        if GameValues.lifeline_options[ll_choice] == "Phone a Friend":
            friend_answer = self.phone_a_friend()
            print(Messages.friend_response.format(question=self._current_question.question, answer=friend_answer))
        if GameValues.lifeline_options[ll_choice] == "50-50":
            fifty_fifty_answer = self.fifty_fifty()
            print(Messages.fifty_fifty_response.format(choice_1=fifty_fifty_answer[0], choice_2=fifty_fifty_answer[1]))

    def run(self) -> None:
        """Run the game runner."""
        self.config.set_initial_configuration()
        self.set_player_name()
        while self._question_no < GameValues.total_questions:
            self.ask_question()
            self.continue_or_drop()
        print(Messages.winning_message.format(player=self._player_name, money=self.prize_won))
        self.history.write_to_history(self._player_name, self.prize_won)

    def show_lifelines(self) -> None:
        """Show lifelines available."""
        print(f"{Breaks.newline}Lifeline choices:")
        for ll_choice, lifeline in GameValues.lifeline_options.items():
            if ll_choice in self._life_lines_used:
                print_strikethrough(f"[{ll_choice}] {lifeline}", end=f"{Breaks.tab_2}")
            else:
                print(f"[{ll_choice}] {lifeline}", end=f"{Breaks.tab_2}")
        print(Breaks.newline)
        ll_value = get_user_input(
            "Enter your lifeline choice : ",
            is_int=True,
            constrains=[option for option in GameValues.lifeline_options if option not in self._life_lines_used],
        )
        self.process_lifeline(ll_value)
        self._life_lines_used[ll_value] = GameValues.lifeline_options.get(ll_value)

    def show_question(self, question: Question) -> None:
        """Show question in terminal.

        Args:
            question (Question): question to be shown.

        """
        print(f"{Breaks.newline}[Q.No {question.question_no}] {question.question}{Breaks.newline}"
              f"1. {question.choices[0]}{Breaks.tab_2}3. {question.choices[2]}{Breaks.newline}"
              f"2. {question.choices[1]}{Breaks.tab_2}4. {question.choices[3]}")

        answer = int(self.answer_lifeline_loop())
        self.process_answer(answer)

    def answer_lifeline_loop(self) -> str:
        """Allow user to answer the question with multiple lifelines.

        Returns:
            str: Answer for the question.

        """
        user_answer = self.request_answer_from_user()
        if user_answer in GameValues.lifeline:
            self.show_lifelines()
            return self.answer_lifeline_loop()
        return user_answer

    def process_answer(self, user_answer: int) -> None:
        """Validate user answer."""
        user_answer = self._current_question.choices[user_answer - 1]
        if user_answer.lower() == self._current_question.correct_answer.lower():
            self.prize_won = GameValues.prize_money.get(self._question_no)
            print(Messages.correct_answer.format(player=self._player_name, money=self.prize_won))
        else:
            print(Messages.wrong_answer.format(player=self._player_name))
            sys.exit(1)

    def request_answer_from_user(self) -> str | int:
        """Request answer from user.

        Returns:
            str | int: Answer for the question.

        """
        user_entry_constrains = GameValues.possible_answers
        if not self._lifeline_available:
            user_entry_constrains = list(filter(
                lambda x: x not in list(GameValues.lifeline), user_entry_constrains))

        return get_user_input(
            "Enter your answer or 'L' for lifeline: ",
            constrains=user_entry_constrains,
        )

    def set_player_name(self) -> None:
        """Set player name."""
        custom_player_name = input("Enter player name: ")
        if custom_player_name:
            self._player_name = custom_player_name
        else:
            self._player_name = self.llm_handler.request_llm(
                LLMPrompts.player_name_prompt, PlayerName,
            )[GameValues.player_name]

    def _construct_question_prompt(self, *add_prompt: str) -> str:
        """Construct question prompt.

        Returns:
            str: Question prompt.

        """
        base_prompt = LLMPrompts.question_prompt.format(
            difficulty_level=self.config.configuration.difficulty,
        )
        if self._question_history:
            last_question = self._question_history[-1]
            self._question_history_prompt += f"{last_question.question_no}. {last_question.question}\n"
            base_prompt += LLMPrompts.question_history + self._question_history_prompt
        if add_prompt:
            in_memory_questions = "\n".join(add_prompt)
            base_prompt += LLMPrompts.in_memory_prompt + in_memory_questions
        return base_prompt

    @property
    def _lifeline_available(self) -> bool:
        """Check if lifeline is available.

        Returns:
            bool: True if lifeline is available else False.

        """
        return len(self._life_lines_used.keys()) != len(GameValues.lifeline_options.keys())
