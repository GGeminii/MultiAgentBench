# team_treasure_hunt.py

"""
Team Treasure Hunt - Multiplayer Action Game

This game is designed for teams of up to 4 players who collaborate to navigate through challenging environments,
collect treasures, solve puzzles, and reach the final treasure chamber. Each player has unique abilities that are
essential for overcoming obstacles and solving puzzles.

Features:
- Multiplayer support (up to 4 players per team)
- Three distinct environments: Forest, Cave, Ancient Ruins
- Four character abilities: Strength, Agility, Intelligence, Stealth
- Puzzle-solving requiring collaboration
- Scoring system based on treasures collected and time taken
- Robust error handling and edge case management
- Comprehensive testing framework

Author: AI Developer
Date: 2024
"""

import random
import time
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue


class Ability(Enum):
    STRENGTH = "Strength"
    AGILITY = "Agility"
    INTELLIGENCE = "Intelligence"
    STEALTH = "Stealth"


@dataclass
class Player:
    name: str
    ability: Ability
    current_location: str = "Start"
    treasures_collected: int = 0
    is_active: bool = True

    def __str__(self) -> str:
        return f"{self.name} ({self.ability.value})"


class Environment:
    """Base class for game environments with specific challenges and puzzles."""

    def __init__(self, name: str, difficulty: int, description: str):
        self.name = name
        self.difficulty = difficulty
        self.description = description
        self.puzzles = []
        self.treasures = []
        self.exits = []

    def add_puzzle(self, puzzle: 'Puzzle') -> None:
        self.puzzles.append(puzzle)

    def add_treasure(self, treasure: str) -> None:
        self.treasures.append(treasure)

    def add_exit(self, destination: str) -> None:
        self.exits.append(destination)


class Puzzle:
    """Represents a puzzle that requires specific abilities to solve."""

    def __init__(self, title: str, description: str, required_abilities: List[Ability], 
                 solution: str, reward: str = "Treasure"):
        self.title = title
        self.description = description
        self.required_abilities = required_abilities
        self.solution = solution
        self.reward = reward
        self.is_solved = False

    def can_solve(self, players: List[Player]) -> bool:
        """Check if any player in the team has the required abilities."""
        available_abilities = {p.ability for p in players if p.is_active}
        return all(ability in available_abilities for ability in self.required_abilities)

    def solve(self, solution_input: str, players: List[Player]) -> bool:
        """Attempt to solve the puzzle."""
        if not self.can_solve(players):
            return False
        if solution_input.lower() == self.solution.lower():
            self.is_solved = True
            return True
        return False

    def get_hint(self) -> str:
        """Provide a hint based on required abilities."""
        hints = {
            Ability.STRENGTH: "You need someone strong to move this object.",
            Ability.AGILITY: "You need someone agile to squeeze through tight spaces.",
            Ability.INTELLIGENCE: "You need someone smart to figure out the pattern.",
            Ability.STEALTH: "You need someone quiet to avoid triggering traps."
        }
        return " ".join([hints[ability] for ability in self.required_abilities])


class GameEngine:
    """Main game engine managing the state, players, environments, and gameplay logic."""

    def __init__(self, max_players_per_team: int = 4):
        self.max_players_per_team = max_players_per_team
        self.players: List[Player] = []
        self.current_team: List[Player] = []
        self.environments: Dict[str, Environment] = {}
        self.current_environment: str = "Start"
        self.game_started = False
        self.game_over = False
        self.start_time = None
        self.end_time = None
        self.score_board: Dict[str, int] = {}
        self.lock = threading.Lock()
        self.action_queue = queue.Queue()

    def create_environments(self) -> None:
        """Initialize the three main environments with puzzles and treasures."""
        # Forest Environment
        forest = Environment("Forest", 1, "A dense, mysterious forest filled with ancient trees.")
        
        # Puzzle: Tree Bridge
        tree_bridge = Puzzle(
            "Tree Bridge",
            "A broken bridge made of vines and wood spans a deep ravine. You need to reweave the vines.",
            [Ability.STRENGTH, Ability.AGILITY],
            "Weave the vines together",
            "Ancient Coin"
        )
        forest.add_puzzle(tree_bridge)
        
        # Treasure: Hidden Chest
        forest.add_treasure("Ancient Coin")
        forest.add_treasure("Mystic Amulet")
        
        # Exit to Cave
        forest.add_exit("Cave")
        
        # Cave Environment
        cave = Environment("Cave", 2, "A dark, winding cave system with glowing crystals.")
        
        # Puzzle: Crystal Pattern
        crystal_pattern = Puzzle(
            "Crystal Pattern",
            "The wall is covered in glowing crystals. Find the correct sequence to open the door.",
            [Ability.INTELLIGENCE],
            "Red-Green-Blue-Red",
            "Golden Key"
        )
        cave.add_puzzle(crystal_pattern)
        
        # Treasure: Crystal Shard
        cave.add_treasure("Crystal Shard")
        cave.add_treasure("Dragon Scale")
        
        # Exit to Ruins
        cave.add_exit("Ancient Ruins")
        
        # Ancient Ruins Environment
        ruins = Environment("Ancient Ruins", 3, "Decaying temples and forgotten tombs with intricate mechanisms.")
        
        # Puzzle: Trap Door
        trap_door = Puzzle(
            "Trap Door",
            "A pressure plate triggers a trap. You must disable it without setting off alarms.",
            [Ability.STEALTH],
            "Step quietly",
            "Final Treasure Chamber Key"
        )
        ruins.add_puzzle(trap_door)
        
        # Final Treasure Chamber
        ruins.add_treasure("Final Treasure")
        
        # Add all environments
        self.environments["Forest"] = forest
        self.environments["Cave"] = cave
        self.environments["Ancient Ruins"] = ruins
        self.environments["Start"] = Environment("Start", 0, "Starting point of your journey.")

    def add_player(self, name: str, ability: Ability) -> bool:
        """Add a player to the current team."""
        if len(self.current_team) >= self.max_players_per_team:
            print(f"Cannot add {name}. Team already has {self.max_players_per_team} players.")
            return False
        
        if any(p.name == name for p in self.current_team):
            print(f"Player {name} already exists in the team.")
            return False
        
        new_player = Player(name=name, ability=ability)
        self.current_team.append(new_player)
        print(f"Player {name} ({ability.value}) added to the team.")
        return True

    def start_game(self) -> bool:
        """Start the game and initialize the timer."""
        if len(self.current_team) < 1:
            print("Cannot start game: Team must have at least one player.")
            return False
        
        if self.game_started:
            print("Game is already running.")
            return False
        
        self.game_started = True
        self.start_time = time.time()
        self.score_board = {p.name: 0 for p in self.current_team}
        self.current_environment = "Start"
        print(f"Game started! Team: {[p.name for p in self.current_team]}")
        print(f"Current location: {self.current_environment}")
        return True

    def move_to_environment(self, target_env: str) -> bool:
        """Move the team to a new environment."""
        if not self.game_started or self.game_over:
            print("Game must be started to move between environments.")
            return False
        
        if target_env not in self.environments:
            print(f"Environment '{target_env}' does not exist.")
            return False
        
        current_env = self.environments[self.current_environment]
        if target_env not in current_env.exits:
            print(f"You cannot go directly from {self.current_environment} to {target_env}.")
            return False
        
        # Check if all puzzles in current environment are solved before leaving
        if self.current_environment != "Start":
            current_env = self.environments[self.current_environment]
            unsolved_puzzles = [p for p in current_env.puzzles if not p.is_solved]
            if unsolved_puzzles:
                print(f"Warning: There are unsolved puzzles in {self.current_environment}:")
                for puzzle in unsolved_puzzles:
                    print(f"  - {puzzle.title}")
                confirm = input("Are you sure you want to leave? (y/n): ")
                if confirm.lower() != 'y':
                    return False
        
        self.current_environment = target_env
        print(f"Team moved to {target_env}.")
        return True

    def solve_puzzle(self, puzzle_title: str, solution: str) -> bool:
        """Attempt to solve a puzzle in the current environment."""
        if not self.game_started or self.game_over:
            print("Game must be started to solve puzzles.")
            return False
        
        env = self.environments[self.current_environment]
        puzzle = None
        for p in env.puzzles:
            if p.title.lower() == puzzle_title.lower():
                puzzle = p
                break
        if puzzle and puzzle.is_solved:
            print(f"Puzzle '{puzzle_title}' has already been solved.")
            return False
        if not puzzle:
            print(f"Puzzle '{puzzle_title}' not found in {self.current_environment}.")
            return False
        
        if not puzzle:
            print(f"Puzzle '{puzzle_title}' not found in {self.current_environment}.")
            return False
        
        success = puzzle.solve(solution, self.current_team)
        if success:
            print(f"Success! Puzzle '{puzzle_title}' solved.")
            # Award treasure
            if puzzle.reward == "Treasure":
                treasure = random.choice(env.treasures)
                env.treasures.remove(treasure)
                for player in self.current_team:
                    if player.is_active:
                        player.treasures_collected += 1
                        self.score_board[player.name] += 1
                print(f"Treasure obtained: {treasure}!")
            elif puzzle.reward == "Final Treasure Chamber Key":
                print("You've obtained the key to the final treasure chamber!")
            return True
        else:
            print(f"Failed to solve puzzle '{puzzle_title}'. Try again.")
            return False

    def collect_treasure(self) -> bool:
        """Collect a treasure from the current environment."""
        if not self.game_started or self.game_over:
            print("Game must be started to collect treasures.")
            return False
        
        env = self.environments[self.current_environment]
        if not env.treasures:
            print(f"No treasures left in {self.current_environment}.")
            return False
        
        treasure = env.treasures.pop()
        for player in self.current_team:
            if player.is_active:
                player.treasures_collected += 1
                self.score_board[player.name] += 1
        print(f"Treasure collected: {treasure}!")
        return True

    def check_victory(self) -> bool:
        """Check if the team has reached the final treasure chamber."""
        if self.current_environment == "Ancient Ruins":
            # Check if the final puzzle is solved
            ruins = self.environments["Ancient Ruins"]
            final_puzzle = None
            for p in ruins.puzzles:
                if p.title == "Trap Door":
                    final_puzzle = p
                    break
            
            if final_puzzle and final_puzzle.is_solved:
                self.game_over = True
                self.end_time = time.time()
                print("\n🎉 CONGRATULATIONS! 🎉")
                print("You've successfully reached the final treasure chamber!")
                return True
        return False

    def get_game_status(self) -> Dict:
        """Return the current game state."""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        return {
            "game_started": self.game_started,
            "game_over": self.game_over,
            "current_environment": self.current_environment,
            "elapsed_time": round(elapsed_time, 2),
            "team": [p.__dict__ for p in self.current_team],
            "score_board": self.score_board,
            "total_treasures": sum(self.score_board.values())
        }

    def end_game(self) -> Dict:
        """End the game and calculate final scores."""
        if not self.game_over:
            print("Game is not over yet. Cannot end prematurely.")
            return {}
        
        total_time = self.end_time - self.start_time
        final_scores = {}
        for name, score in self.score_board.items():
            # Score = treasures collected + bonus for speed
            speed_bonus = max(0, 600 - total_time)  # Bonus up to 600 seconds
            final_scores[name] = score + int(speed_bonus / 10)
        
        winner = max(final_scores, key=final_scores.get)
        print(f"\n🏆 FINAL RESULTS 🏆")
        print(f"Total Time: {round(total_time, 2)} seconds")
        print(f"Treasures Collected: {sum(self.score_board.values())}")
        print(f"Final Scores:")
        for name, score in final_scores.items():
            print(f"  {name}: {score} points")
        print(f"Winner: {winner} with {final_scores[winner]} points!")
        
        return final_scores

    def reset_game(self) -> None:
        """Reset the game state."""
        self.current_team = []
        self.game_started = False
        self.game_over = False
        self.start_time = None
        self.end_time = None
        self.score_board = {}
        self.current_environment = "Start"
        print("Game reset.")


class GameUI:
    """User interface for interacting with the game engine."""

    def __init__(self, game_engine: GameEngine):
        self.game = game_engine
        self.running = True

    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "="*50)
        print("         TEAM TREASURE HUNT")
        print("="*50)
        print("1. Create Team")
        print("2. Start Game")
        print("3. View Current Status")
        print("4. Move to Environment")
        print("5. Solve Puzzle")
        print("6. Collect Treasure")
        print("7. Check Victory")
        print("8. End Game")
        print("9. Reset Game")
        print("0. Quit")
        print("="*50)

    def run(self) -> None:
        """Run the game loop."""
        self.game.create_environments()
        
        while self.running:
            self.display_menu()
            choice = input("Enter your choice (0-9): ").strip()
            
            try:
                if choice == "0":
                    print("Thanks for playing Team Treasure Hunt!")
                    self.running = False
                
                elif choice == "1":
                    self.create_team()
                
                elif choice == "2":
                    self.start_game()
                
                elif choice == "3":
                    self.view_status()
                
                elif choice == "4":
                    self.move_environment()
                
                elif choice == "5":
                    self.solve_puzzle()
                
                elif choice == "6":
                    self.collect_treasure()
                
                elif choice == "7":
                    self.check_victory()
                
                elif choice == "8":
                    self.end_game()
                
                elif choice == "9":
                    self.reset_game()
                
                else:
                    print("Invalid choice. Please select a number from 0 to 9.")
                    
            except Exception as e:
                print(f"An error occurred: {e}")

    def create_team(self) -> None:
        """Handle team creation."""
        print("\n--- CREATE TEAM ---")
        if len(self.game.current_team) >= self.game.max_players_per_team:
            print(f"Team is full ({self.game.max_players_per_team} players).")
            return
        
        while len(self.game.current_team) < self.game.max_players_per_team:
            name = input(f"Enter name for player {len(self.game.current_team) + 1}: ").strip()
            if not name:
                print("Name cannot be empty.")
                continue
            
            print("Choose ability:")
            for i, ability in enumerate(Ability, 1):
                print(f"{i}. {ability.value}")
            
            try:
                choice = int(input("Enter choice (1-4): "))
                if 1 <= choice <= 4:
                    ability = list(Ability)[choice - 1]
                    self.game.add_player(name, ability)
                else:
                    print("Invalid choice. Please choose 1-4.")
            except ValueError:
                print("Please enter a valid number.")
            
            if len(self.game.current_team) >= self.game.max_players_per_team:
                break
        
        print(f"Team created: {[p.name for p in self.game.current_team]}")

    def start_game(self) -> None:
        """Start the game."""
        if not self.game.current_team:
            print("No team created. Create a team first.")
            return
        if self.game.game_started:
            print("Game is already running.")
            return
        
        self.game.start_game()
        print(f"Welcome to {self.game.current_environment}!")

    def view_status(self) -> None:
        """Display current game status."""
        status = self.game.get_game_status()
        print("\n--- GAME STATUS ---")
        print(f"Game Started: {'Yes' if status['game_started'] else 'No'}")
        print(f"Game Over: {'Yes' if status['game_over'] else 'No'}")
        print(f"Current Location: {status['current_environment']}")
        print(f"Elapsed Time: {status['elapsed_time']} seconds")
        print(f"Total Treasures Collected: {status['total_treasures']}")
        print(f"Team Members:")
        for player in status['team']:
            print(f"  {player['name']} ({player['ability'].value}) - "
                   f"Treasures: {player['treasures_collected']}")
        print(f"Score Board:")
        for name, score in status['score_board'].items():
            print(f"  {name}: {score}")

    def move_environment(self) -> None:
        """Move to a different environment."""
        if not self.game.game_started:
            print("Game must be started to move between environments.")
            return
        
        print(f"\nAvailable exits from {self.game.current_environment}:")
        current_env = self.game.environments[self.game.current_environment]
        for exit_env in current_env.exits:
            print(f"  - {exit_env}")
        
        target = input(f"Enter destination from {self.game.current_environment}: ").strip()
        if self.game.move_to_environment(target):
            print(f"Moved to {target}!")
        else:
            print(f"Failed to move to {target}.")

    def solve_puzzle(self) -> None:
        """Solve a puzzle in the current environment."""
        if not self.game.game_started:
            print("Game must be started to solve puzzles.")
            return
        
        env = self.game.environments[self.game.current_environment]
        if not env.puzzles:
            print(f"No puzzles in {self.game.current_environment}.")
            return
        
        print(f"\n--- PUZZLES IN {self.game.current_environment.upper()} ---")
        for i, puzzle in enumerate(env.puzzles, 1):
            print(f"{i}. {puzzle.title}")
            if not puzzle.is_solved:
                print(f"   Description: {puzzle.description}")
                print(f"   Required Abilities: {', '.join(a.value for a in puzzle.required_abilities)}")
                print(f"   Hint: {puzzle.get_hint()}")
        
        try:
            choice = int(input("Select puzzle number to solve: ")) - 1
            if 0 <= choice < len(env.puzzles):
                puzzle = env.puzzles[choice]
                if puzzle.is_solved:
                    print(f"Puzzle '{puzzle.title}' has already been solved.")
                    return
                
                solution = input(f"Enter solution for '{puzzle.title}': ").strip()
                if self.game.solve_puzzle(puzzle.title, solution):
                    if self.game.check_victory():
                        self.end_game()
            else:
                print("Invalid puzzle selection.")
        except ValueError:
            print("Please enter a valid number.")

    def collect_treasure(self) -> None:
        """Collect a treasure from the current environment."""
        if not self.game.game_started:
            print("Game must be started to collect treasures.")
            return
        
        env = self.game.environments[self.game.current_environment]
        if not env.treasures:
            print(f"No treasures left in {self.game.current_environment}.")
            return
        
        print(f"\nTreasures available in {self.game.current_environment}:")
        for i, treasure in enumerate(env.treasures, 1):
            print(f"{i}. {treasure}")
        
        try:
            choice = int(input("Select treasure to collect (1-{}): ".format(len(env.treasures))))
            if 1 <= choice <= len(env.treasures):
                selected_treasure = env.treasures[choice - 1]
                if self.game.collect_treasure():
                    print(f"Collected: {selected_treasure}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")

    def check_victory(self) -> None:
        """Check if the team has won."""
        if self.game.check_victory():
            print("Victory condition met! The final treasure chamber is accessible.")
        else:
            print("You haven't reached the final treasure chamber yet.")

    def end_game(self) -> None:
        """End the game and show results."""
        if not self.game.game_over:
            print("Game is not over yet. Cannot end prematurely.")
            return
        
        final_scores = self.game.end_game()
        self.running = False

    def reset_game(self) -> None:
        """Reset the game."""
        self.game.reset_game()


def run_tests():
    """Comprehensive test suite for the game engine."""
    print("Running comprehensive tests...")
    
    # Test 1: Initialize game engine
    game = GameEngine(max_players_per_team=4)
    assert game.max_players_per_team == 4, "Max players should be 4"
    assert len(game.current_team) == 0, "Team should be empty initially"
    
    # Test 2: Create environments
    game.create_environments()
    assert "Forest" in game.environments, "Forest environment should exist"
    assert "Cave" in game.environments, "Cave environment should exist"
    assert "Ancient Ruins" in game.environments, "Ancient Ruins environment should exist"
    
    # Test 3: Add players
    player1 = Player("Alice", Ability.STRENGTH)
    player2 = Player("Bob", Ability.AGILITY)
    game.current_team = [player1, player2]
    
    # Test 4: Solve puzzle with correct abilities
    forest = game.environments["Forest"]
    puzzle = forest.puzzles[0]  # Tree Bridge
    assert puzzle.can_solve(game.current_team), "Players should be able to solve Tree Bridge"
    assert puzzle.solve("Weave the vines together", game.current_team), "Should solve correctly"
    
    # Test 5: Attempt to solve with wrong solution
    assert not puzzle.solve("Wrong answer", game.current_team), "Should fail with wrong answer"
    
    # Test 6: Check victory condition
    game.current_environment = "Ancient Ruins"
    ruins = game.environments["Ancient Ruins"]
    trap_puzzle = None
    for p in ruins.puzzles:
        if p.title == "Trap Door":
            trap_puzzle = p
            break
    assert trap_puzzle is not None, "Trap Door puzzle should exist"
    trap_puzzle.is_solved = True
    assert game.check_victory(), "Should detect victory when puzzle is solved"
    
    # Test 7: Score calculation
    game.score_board = {"Alice": 5, "Bob": 3}
    game.start_time = time.time() - 300  # 5 minutes ago
    game.end_time = time.time()
    final_scores = game.end_game()
    assert "Alice" in final_scores, "Alice should be in final scores"
    assert final_scores["Alice"] > 5, "Alice should have bonus points for speed"
    
    # Test 8: Edge cases
    game.current_team = []
    assert not game.start_game(), "Should not start with no players"
    
    # Test 9: Multiple players with same name
    game.current_team = []
    game.add_player("Charlie", Ability.INTELLIGENCE)
    assert not game.add_player("Charlie", Ability.STEALTH), "Should not allow duplicate names"
    
    # Test 10: Moving between environments
    game.current_environment = "Forest"
    assert game.move_to_environment("Cave"), "Should be able to move from Forest to Cave"
    
    print("All tests passed! ✅")


def main():
    """Main entry point for the game."""
    print("Welcome to Team Treasure Hunt!")
    
    # Run tests before starting the game
    run_tests()
    
    # Create and start the game
    game_engine = GameEngine(max_players_per_team=4)
    ui = GameUI(game_engine)
    ui.run()


if __name__ == "__main__":
    main()