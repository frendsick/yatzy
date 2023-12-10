import random
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto
from statistics import mode
from typing import Callable

DICE_SIDES = 6
DICES = 5
MAX_THROWS = 3
YATZY_SCORE = 50


class ScoreBox(Enum):
    ONES = auto()
    TWOS = auto()
    THREES = auto()
    FOURS = auto()
    FIVES = auto()
    SIXES = auto()
    PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    FOUR_OF_A_KIND = auto()
    SMALL_STRAIGHT = auto()
    LARGE_STRAIGHT = auto()
    FULL_HOUSE = auto()
    CHANCE = auto()
    YATZY = auto()


def throw_dices(dices: list[int], held_dices: list[int] | None = None) -> list[int]:
    # Only throw the dices that were not held
    for i, _ in enumerate(dices):
        if not held_dices or i not in held_dices:
            dices[i] = random.randint(1, DICE_SIDES)
    return dices


def number_sum(dices: list[int], number: int) -> int:
    return dices.count(number) * number


def ones(dices: list[int]) -> int:
    return number_sum(dices, 1)


def twos(dices: list[int]) -> int:
    return number_sum(dices, 2)


def threes(dices: list[int]) -> int:
    return number_sum(dices, 3)


def fours(dices: list[int]) -> int:
    return number_sum(dices, 4)


def fives(dices: list[int]) -> int:
    return number_sum(dices, 5)


def sixes(dices: list[int]) -> int:
    return number_sum(dices, 6)


def pair(dices: list[int]) -> int:
    counts = Counter(dices)
    pairs = [value * 2 for value, count in counts.items() if count >= 2]
    return max(pairs) if pairs else 0


def two_pair(dices: list[int]) -> int:
    counts = Counter(dices)
    pairs = [value * 2 for value, count in counts.items() if count >= 2]
    return sum(pairs) if len(pairs) >= 2 else 0


def n_of_a_kind(dices: list[int], n: int) -> int:
    most_common = mode(dices)
    count = dices.count(most_common)
    return most_common * n if count >= n else 0


def three_of_a_kind(dices: list[int]) -> int:
    return n_of_a_kind(dices, 3)


def four_of_a_kind(dices: list[int]) -> int:
    return n_of_a_kind(dices, 4)


def small_straight(dices: list[int]) -> int:
    return 15 if sorted(dices) == [1, 2, 3, 4, 5] else 0


def large_straight(dices: list[int]) -> int:
    return 20 if sorted(dices) == [2, 3, 4, 5, 6] else 0


def full_house(dices: list[int]) -> int:
    if len(set(dices)) == 2 and dices.count(dices[0]) in {2, 3}:
        return sum(dices)
    return 0


def chance(dices: list[int]) -> int:
    return sum(dices)


def yatzy(dices: list[int]) -> int:
    return YATZY_SCORE if len(set(dices)) == 1 else 0


SCORE_BOXES: dict[int, Callable] = {
    ScoreBox.ONES.value: ones,
    ScoreBox.TWOS.value: twos,
    ScoreBox.THREES.value: threes,
    ScoreBox.FOURS.value: fours,
    ScoreBox.FIVES.value: fives,
    ScoreBox.SIXES.value: sixes,
    ScoreBox.PAIR.value: pair,
    ScoreBox.TWO_PAIR.value: two_pair,
    ScoreBox.THREE_OF_A_KIND.value: three_of_a_kind,
    ScoreBox.FOUR_OF_A_KIND.value: four_of_a_kind,
    ScoreBox.SMALL_STRAIGHT.value: small_straight,
    ScoreBox.LARGE_STRAIGHT.value: large_straight,
    ScoreBox.FULL_HOUSE.value: full_house,
    ScoreBox.CHANCE.value: chance,
    ScoreBox.YATZY.value: yatzy,
}


def readable_score_box(score_box: ScoreBox) -> str:
    return " ".join(word.capitalize() for word in score_box.name.split("_"))


@dataclass(slots=True)
class Player:
    name: str
    score: int = 0
    upper_score: int = 0
    available_score_boxes: dict[int, Callable] = field(
        default_factory=lambda: deepcopy(SCORE_BOXES)
    )

    def print_available_score_boxes(self):
        for index in self.available_score_boxes.keys():
            score_box_name = readable_score_box(ScoreBox(index))
            print(f"{index}: {score_box_name}")


def choose_held_dices(dices: list[int]) -> list[int]:
    held_dices = []
    valid_input: bool = False
    while not valid_input:
        print(f"\nDices: {dices}")
        valid_input = True  # Changes to False if wrong input is inserted
        kept_dices: str = input("Dices to keep: ")
        for character in kept_dices:
            try:
                dice_index = int(character) - 1
                if dice_index > DICES:
                    valid_input = False
                    break
                held_dices.append(dice_index)
            except ValueError:
                valid_input = False
                break
        if not valid_input:
            print("Invalid input")
            print(
                "Insert numbers for dices. F.ex. '1235' will throw again dices 1, 2, 3, and 5"
            )
    return held_dices


def output_player_score(player: Player) -> None:
    print(
        f"{player.name} has {player.score} points in total (upper total: {player.upper_score})"
    )


def update_player_score(player: Player, dices: list[int]) -> None:
    while True:
        try:
            chosen_score_box = int(input("Choose: "))
            score_box_function = player.available_score_boxes.pop(chosen_score_box)
            break
        except (ValueError, KeyError):
            print("Invalid selection, try again")

    # Calculate points for the score box
    score: int = score_box_function(dices)
    player.score += score
    if 1 <= chosen_score_box <= 6:
        player.upper_score += score

    # Output score information
    score_box_name = readable_score_box(ScoreBox(chosen_score_box))
    print(f"\n{player.name} added {score} points to {score_box_name.lower()}")
    output_player_score(player)


def take_turn(player: Player):
    print(f"\n{player.name}'s turn")
    dices = [1] * 5
    held_dices: list[int] | None = None
    for throw in range(0, MAX_THROWS):
        dices = throw_dices(dices, held_dices)

        if throw + 1 >= MAX_THROWS:
            break

        # What dices to keep?
        held_dices = choose_held_dices(dices)

        if len(held_dices) >= DICES:
            break

    # Choose what score box to put points to
    print(f"\nDices: {dices}")
    print("Available score boxes:")
    player.print_available_score_boxes()
    update_player_score(player, dices)


def define_winner(players: list[Player]) -> Player:
    assert len(players) > 0, "Defining winner requires at least one player"
    return max(players, key=lambda player: player.score)


def output_scoreboard(players: list[Player]) -> None:
    print("\nSCOREBOARD:")
    for player in players:
        output_player_score(player)


def add_players() -> list[Player]:
    players: list[Player] = []

    while True:
        player_name: str = input("Player name: ")
        players.append(Player(player_name))
        print(f"{player_name} added to the game")
        if not player_wants_to_add_another_player():
            break

    players.append(Player("Iina"))
    return players


def player_wants_to_add_another_player() -> bool:
    while True:
        answer: str = input("Add another player? (Y/N) ")
        if answer.upper() == "N":
            return False
        if answer.upper() == "Y":
            return True
        print(f"Invalid option '{answer}'")


def main():
    players: list[Player] = add_players()

    while True:
        # Players take turns unti the game is over
        for player in players:
            if not player.available_score_boxes:
                # Output the scores and who won the game
                output_scoreboard(players)
                winner = define_winner(players)
                print(f"{winner.name} won with {winner.score} points!")
                return
            take_turn(player)


if __name__ == "__main__":
    main()
