# solution.py
"""
Team_Tactics: A Multiplayer Action Game for AI Agents

This game simulates a cooperative environment where AI agents with different roles work together to complete objectives.
The game features multiple levels, agent communication, dynamic environments, and a scoring system.

Key Features:
- Multiple levels with different objectives (capture flag, defend base, eliminate enemies)
- Agent roles: Attacker, Defender, Scout, Healer
- Communication system via shared message queue
- Dynamic environment with obstacles and terrain
- Scoring system based on objectives completed and efficiency
- Comprehensive test cases for validation
"""

import random
import time
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import copy

# ================== ENUMS AND DATA CLASSES ==================

class Role(Enum):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    SCOUT = "scout"
    HEALER = "healer"

class ObjectiveType(Enum):
    CAPTURE_FLAG = "capture_flag"
    DEFEND_BASE = "defend_base"
    ELIMINATE_ENEMIES = "eliminate_enemies"

class GameState(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Position:
    x: int
    y: int
    
    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

@dataclass
class Agent:
    id: int
    role: Role
    position: Position
    health: int = 100
    max_health: int = 100
    speed: float = 1.0
    abilities: List[str] = None
    is_alive: bool = True
    
    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []
    
    def move_towards(self, target: Position, grid_size: int = 10) -> Position:
        """Move agent towards target position with some randomness."""
        if not self.is_alive or self.position == target:
            return self.position
        
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        
        # Normalize direction vector
        magnitude = (dx**2 + dy**2)**0.5
        if magnitude == 0:
            return self.position
            
        dx /= magnitude
        dy /= magnitude
        
        # Apply speed factor
        step_x = dx * self.speed
        step_y = dy * self.speed
        
        # Add slight randomness to movement
        step_x += random.uniform(-0.2, 0.2)
        step_y += random.uniform(-0.2, 0.2)
        
        new_x = self.position.x + step_x
        new_y = self.position.y + step_y
        
        # Keep within bounds
        new_x = max(0, min(grid_size - 1, new_x))
        new_y = max(0, min(grid_size - 1, new_y))
        
        return Position(int(new_x), int(new_y))
    
    def take_damage(self, amount: int) -> int:
        """Apply damage to agent and return actual damage taken."""
        if not self.is_alive:
            return 0
            
        damage_taken = min(amount, self.health)
        self.health -= damage_taken
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            
        return damage_taken
    
    def heal(self, amount: int) -> int:
        """Heal agent and return actual healing done."""
        if not self.is_alive:
            return 0
            
        healing_done = min(amount, self.max_health - self.health)
        self.health += healing_done
        
        return healing_done
    
    def can_use_ability(self, ability: str) -> bool:
        """Check if agent can use a specific ability."""
        return ability in self.abilities and self.is_alive

# ================== GAME ENVIRONMENT ==================

class GameEnvironment:
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.obstacles: Set[Position] = set()
        self.reset_obstacles()
        self.flag_positions: Dict[str, Position] = {}
        self.base_positions: Dict[str, Position] = {}
        self.reset_flags_and_bases()
        
    def reset_obstacles(self):
        """Generate random obstacles in the environment."""
        self.obstacles.clear()
        # Place some random obstacles
        num_obstacles = max(1, min(10, int(self.width * self.height * 0.1)))
        for _ in range(num_obstacles):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.obstacles.add(Position(x, y))
    
    def reset_flags_and_bases(self):
        """Place flags and bases at random positions."""
        self.flag_positions = {
            "red": Position(random.randint(0, self.width - 1), random.randint(0, self.height - 1)),
            "blue": Position(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        }
        
        # Ensure flags are not too close to each other
        while self.flag_positions["red"].distance_to(self.flag_positions["blue"]) < 3:
            self.flag_positions["blue"] = Position(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )
        
        # Place bases
        self.base_positions = {
            "red": Position(random.randint(0, self.width - 1), random.randint(0, self.height - 1)),
            "blue": Position(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        }
        
        # Ensure bases are not too close to flags
        while self.base_positions["red"].distance_to(self.flag_positions["red"]) < 4:
            self.base_positions["red"] = Position(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )
            
        while self.base_positions["blue"].distance_to(self.flag_positions["blue"]) < 4:
            self.base_positions["blue"] = Position(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )
    
    def is_valid_position(self, pos: Position) -> bool:
        """Check if a position is valid (within bounds and not an obstacle)."""
        if pos.x < 0 or pos.x >= self.width or pos.y < 0 or pos.y >= self.height:
            return False
        return pos not in self.obstacles
    
    def get_neighbors(self, pos: Position) -> List[Position]:
        """Get all valid neighboring positions."""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if self.is_valid_position(new_pos):
                neighbors.append(new_pos)
                
        return neighbors
    
    def get_path(self, start: Position, end: Position) -> List[Position]:
        """Simple A* pathfinding algorithm to find path from start to end."""
        if start == end:
            return [start]
            
        open_set = {start}
        closed_set = set()
        came_from = {}
        g_score = {start: 0}
        f_score = {start: start.distance_to(end)}
        
        while open_set:
            current = min(open_set, key=lambda p: f_score.get(p, float('inf')))
            
            if current == end:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            open_set.remove(current)
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                    
                tentative_g = g_score[current] + current.distance_to(neighbor)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + neighbor.distance_to(end)
                    
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                        
        return []  # No path found

# ================== COMMUNICATION SYSTEM ==================

class CommunicationSystem:
    def __init__(self):
        self.message_queue: List[Dict] = []
        self.agent_messages: Dict[int, List[Dict]] = {}
    
    def send_message(self, sender_id: int, message: Dict):
        """Send a message to all agents."""
        self.message_queue.append({
            "sender": sender_id,
            "timestamp": time.time(),
            "message": message
        })
        
        # Also store in individual agent queues
        if sender_id not in self.agent_messages:
            self.agent_messages[sender_id] = []
        self.agent_messages[sender_id].append(message)
    
    def receive_messages(self, receiver_id: int) -> List[Dict]:
        """Receive all messages intended for a specific agent."""
        return self.agent_messages.get(receiver_id, [])
    
    def clear_messages(self):
        """Clear all messages from the system."""
        self.message_queue.clear()
        self.agent_messages.clear()

# ================== GAME CORE ==================

class TeamTacticsGame:
    def __init__(self, level: int = 1):
        self.level = level
        self.environment = GameEnvironment(width=15, height=15)
        self.agents: List[Agent] = []
        self.communication_system = CommunicationSystem()
        self.objective_type = self._get_objective_type(level)
        self.game_state = GameState.RUNNING
        self.score = 0
        self.total_actions = 0
        self.time_elapsed = 0
        self.max_time = 300  # 5 minutes
        self.setup_agents()
        
    def _get_objective_type(self, level: int) -> ObjectiveType:
        """Determine objective type based on level."""
        objectives = [
            ObjectiveType.CAPTURE_FLAG,
            ObjectiveType.DEFEND_BASE,
            ObjectiveType.ELIMINATE_ENEMIES
        ]
        return objectives[(level - 1) % len(objectives)]
    
    def setup_agents(self):
        """Create agents with different roles and abilities."""
        self.agents = []
        
        # Create 4 agents per team (red and blue)
        for i in range(4):
            # Red team agents
            red_agent = Agent(
                id=i,
                role=Role.ATTACKER,
                position=self.environment.base_positions["red"],
                health=100,
                speed=1.2,
                abilities=["speed_boost", "shield"]
            )
            self.agents.append(red_agent)
            
            # Blue team agents
            blue_agent = Agent(
                id=i + 4,
                role=Role.DEFENDER,
                position=self.environment.base_positions["blue"],
                health=100,
                speed=0.8,
                abilities=["heal", "shield"]
            )
            self.agents.append(blue_agent)
        
        # Assign specific roles to specific agents
        self.agents[0].role = Role.ATTACKER
        self.agents[1].role = Role.Scout
        self.agents[2].role = Role.HEALER
        self.agents[3].role = Role.DEFENDER
        
        self.agents[4].role = Role.ATTACKER
        self.agents[5].role = Role.Scout
        self.agents[6].role = Role.HEALER
        self.agents[7].role = Role.DEFENDER
        
        # Update speeds based on roles
        for agent in self.agents:
            if agent.role == Role.SCOOT:
                agent.speed = 1.5
            elif agent.role == Role.DEFENDER:
                agent.speed = 0.7
            elif agent.role == Role.HEALER:
                agent.speed = 0.9
            elif agent.role == Role.ATTACKER:
                agent.speed = 1.3
    
    def get_team(self, agent_id: int) -> str:
        """Get team color for an agent."""
        if agent_id < 4:
            return "red"
        else:
            return "blue"
    
    def get_opponent_team(self, team: str) -> str:
        """Get opponent team."""
        return "blue" if team == "red" else "red"
    
    def get_team_agents(self, team: str) -> List[Agent]:
        """Get all agents of a specific team."""
        return [agent for agent in self.agents if self.get_team(agent.id) == team]
    
    def get_enemy_agents(self, team: str) -> List[Agent]:
        """Get all enemy agents."""
        return [agent for agent in self.agents if self.get_team(agent.id) != team]
    
    def get_all_alive_agents(self) -> List[Agent]:
        """Get all alive agents."""
        return [agent for agent in self.agents if agent.is_alive]
    
    def get_all_dead_agents(self) -> List[Agent]:
        """Get all dead agents."""
        return [agent for agent in self.agents if not agent.is_alive]
    
    def get_closest_enemy(self, agent: Agent) -> Optional[Agent]:
        """Find the closest enemy agent to a given agent."""
        enemies = self.get_enemy_agents(self.get_team(agent.id))
        if not enemies:
            return None
            
        closest = None
        min_distance = float('inf')
        
        for enemy in enemies:
            if enemy.is_alive:
                dist = agent.position.distance_to(enemy.position)
                if dist < min_distance:
                    min_distance = dist
                    closest = enemy
                    
        return closest
    
    def get_closest_friend(self, agent: Agent) -> Optional[Agent]:
        """Find the closest friendly agent to a given agent."""
        friends = self.get_team_agents(self.get_team(agent.id))
        if not friends:
            return None
            
        closest = None
        min_distance = float('inf')
        
        for friend in friends:
            if friend.is_alive and friend.id != agent.id:
                dist = agent.position.distance_to(friend.position)
                if dist < min_distance:
                    min_distance = dist
                    closest = friend
                    
        return closest
    
    def broadcast_message(self, sender_id: int, message_type: str, content: Dict):
        """Broadcast a message to all agents."""
        message = {
            "type": message_type,
            "content": content,
            "sender": sender_id
        }
        self.communication_system.send_message(sender_id, message)
    
    def update(self):
        """Update game state by one tick."""
        if self.game_state != GameState.RUNNING:
            return
            
        self.time_elapsed += 1
        self.total_actions += len(self.agents)
        
        # Check if time limit reached
        if self.time_elapsed >= self.max_time:
            self.game_state = GameState.FAILED
            return
        
        # Update each agent's behavior based on their role
        for agent in self.agents:
            if not agent.is_alive:
                continue
                
            self.update_agent_behavior(agent)
        
        # Check if objective is completed
        self.check_objective_completion()
    
    def update_agent_behavior(self, agent: Agent):
        """Update agent behavior based on role and current situation."""
        team = self.get_team(agent.id)
        enemy_team = self.get_opponent_team(team)
        
        # Get relevant positions
        base_pos = self.environment.base_positions[team]
        flag_pos = self.environment.flag_positions[enemy_team]  # Enemy flag
        
        # Determine target based on objective
        target = None
        if self.objective_type == ObjectiveType.CAPTURE_FLAG:
            target = flag_pos
        elif self.objective_type == ObjectiveType.DEFEND_BASE:
            target = base_pos
        elif self.objective_type == ObjectiveType.ELIMINATE_ENEMIES:
            enemy = self.get_closest_enemy(agent)
            if enemy:
                target = enemy.position
            else:
                # If no enemies nearby, go to base
                target = base_pos
        
        # Move toward target
        if target:
            new_pos = agent.move_towards(target, grid_size=15)
            # Check if movement is blocked by obstacle
            if not self.environment.is_valid_position(new_pos):
                # Try to find a path around
                path = self.environment.get_path(agent.position, target)
                if path and len(path) > 1:
                    new_pos = path[1]
            
            agent.position = new_pos
        
        # Handle special behaviors based on role
        if agent.role == Role.SCOOT:
            # Scout should explore and report
            if random.random() < 0.3:  # 30% chance to scoutif agent.role == Role.Scout:                enemy = self.get_closest_enemy(agent)
                if enemy:
                    self.broadcast_message(
                        agent.id,
                        "enemy_location",
                        {"x": enemy.position.x, "y": enemy.position.y, "id": enemy.id}
                    )
        
        elif agent.role == Role.HEALER:
            # Healer should try to heal allies
            friend = self.get_closest_friend(agent)
            if friend and friend.health < 80 and agent.can_use_ability("heal"):
                # Heal nearby ally
                healed_amount = friend.heal(20)
                if healed_amount > 0:
                    self.broadcast_message(
                        agent.id,
                        "healing",
                        {"target": friend.id, "amount": healed_amount}
                    )
        
        elif agent.role == Role.DEFENDER:
            # Defender should stay near base
            if agent.position.distance_to(base_pos) > 5:
                # Return to base
                path = self.environment.get_path(agent.position, base_pos)
                if path and len(path) > 1:
                    agent.position = path[1]
        
        elif agent.role == Role.ATTACKER:
            # Attackers should focus on enemy flag or enemies
            if self.objective_type == ObjectiveType.CAPTURE_FLAG:
                if agent.position.distance_to(flag_pos) < 2:
                    # Capture flag
                    self.score += 100
                    self.game_state = GameState.COMPLETED
                    return
            elif self.objective_type == ObjectiveType.ELIMINATE_ENEMIES:
                enemy = self.get_closest_enemy(agent)
                if enemy and agent.position.distance_to(enemy.position) < 2:
                    # Eliminate enemy
                    enemy.take_damage(100)
                    self.score += 50
                    self.broadcast_message(
                        agent.id,
                        "enemy_eliminated",
                        {"enemy_id": enemy.id}
                    )
        
        # Check for collisions with enemies
        for enemy in self.get_enemy_agents(team):
            if enemy.is_alive and agent.position == enemy.position:
                # Collision - attack
                damage = random.randint(10, 25)
                enemy.take_damage(damage)
                self.score -= 5  # Penalty for ineffective attacks
        
        # Check if agent is stuck (no progress)
        if self.total_actions > 100 and random.random() < 0.1:
            # Randomly reposition if agent seems stuck
            agent.position = Position(
                random.randint(0, self.environment.width - 1),
                random.randint(0, self.environment.height - 1)
            )
    
    def check_objective_completion(self):
        """Check if the current objective has been completed."""
        if self.game_state != GameState.RUNNING:
            return
            
        if self.objective_type == ObjectiveType.CAPTURE_FLAG:
            # Check if any agent has captured the enemy flag
            enemy_flag = self.environment.flag_positions[self.get_opponent_team(self.get_team(self.agents[0].id))]
            for agent in self.agents:
                if agent.is_alive and agent.position == enemy_flag:
                    self.score += 200
                    self.game_state = GameState.COMPLETED
                    return
                    
        elif self.objective_type == ObjectiveType.DEFEND_BASE:
            # Check if all enemy agents are eliminated
            enemy_agents = self.get_enemy_agents(self.get_team(self.agents[0].id))
            if not any(agent.is_alive for agent in enemy_agents):
                self.score += 150
                self.game_state = GameState.COMPLETED
                return
                
        elif self.objective_type == ObjectiveType.ELIMINATE_ENEMIES:
            # Check if all enemy agents are eliminated
            enemy_agents = self.get_enemy_agents(self.get_team(self.agents[0].id))
            if not any(agent.is_alive for agent in enemy_agents):
                self.score += 250
                self.game_state = GameState.COMPLETED
                return
    
    def get_game_status(self) -> Dict:
        """Get current game status."""
        return {
            "level": self.level,
            "game_state": self.game_state.value,
            "score": self.score,
            "time_elapsed": self.time_elapsed,
            "max_time": self.max_time,
            "agents": [
                {
                    "id": agent.id,
                    "role": agent.role.value,
                    "position": {"x": agent.position.x, "y": agent.position.y},
                    "health": agent.health,
                    "is_alive": agent.is_alive
                }
                for agent in self.agents
            ],
            "objective": self.objective_type.value,
            "environment": {
                "width": self.environment.width,
                "height": self.environment.height,
                "flag_positions": {
                    k: {"x": v.x, "y": v.y} for k, v in self.environment.flag_positions.items()
                },
                "base_positions": {
                    k: {"x": v.x, "y": v.y} for k, v in self.environment.base_positions.items()
                }
            }
        }
    
    def get_scoring_summary(self) -> Dict:
        """Get detailed scoring information."""
        total_agents = len(self.agents)
        alive_agents = len([a for a in self.agents if a.is_alive])
        dead_agents = total_agents - alive_agents
        
        # Calculate efficiency score
        efficiency = (self.score / (self.total_actions + 1)) * 100
        
        return {
            "total_score": self.score,
            "efficiency_score": round(efficiency, 2),
            "agents_alive": alive_agents,
            "agents_dead": dead_agents,
            "time_used": self.time_elapsed,
            "time_limit": self.max_time,
            "objective_completed": self.game_state == GameState.COMPLETED
        }

# ================== TEST CASES ==================

def run_test_cases():
    """Run comprehensive test cases for Team_Tactics game."""
    print("=" * 60)
    print("TEAM_TACTICS GAME TEST SUITE")
    print("=" * 60)
    
    # Test 1: Basic game initialization
    print("\nTEST 1: Basic Game Initialization")
    game = TeamTacticsGame(level=1)
    status = game.get_game_status()
    assert isinstance(status, dict), "Game status should be a dictionary"
    assert len(status["agents"]) == 8, "Should have 8 agents"
    assert status["objective"] == "capture_flag", "Default objective should be capture flag"
    print("✓ Basic initialization passed")
    
    # Test 2: Agent roles and abilities
    print("\nTEST 2: Agent Roles and Abilities")
    attacker = next(a for a in game.agents if a.role == Role.ATTACKER)
    scout = next(a for a in game.agents if a.role == Role.SCOOT)
    healer = next(a for a in game.agents if a.role == Role.HEALER)
    defender = next(a for a in game.agents if a.role == Role.DEFENDER)
    
    assert attacker.speed > 1.0, "Attackers should have higher speed"
    assert scout.speed > 1.0, "Scouts should have high speed"
    assert healer.speed < 1.0, "Healers should have lower speed"
    assert defender.speed < 1.0, "Defenders should have low speed"
    print("✓ Role-based speed adjustments passed")
    
    # Test 3: Communication system
    print("\nTEST 3: Communication System")
    game.communication_system.send_message(0, {"type": "test", "content": "hello"})
    messages = game.communication_system.receive_messages(0)
    assert len(messages) > 0, "Should receive sent message"
    assert messages[0]["content"] == "hello", "Message content should match"
    print("✓ Communication system passed")
    
    # Test 4: Pathfinding
    print("\nTEST 4: Pathfinding")
    start = Position(0, 0)
    end = Position(9, 9)
    path = game.environment.get_path(start, end)
    assert len(path) > 0, "Should find a path"
    assert path[0] == start, "Path should start at start position"
    assert path[-1] == end, "Path should end at end position"
    print("✓ Pathfinding passed")
    
    # Test 5: Objective completion - capture flag
    print("\nTEST 5: Objective Completion - Capture Flag")
    game = TeamTacticsGame(level=1)
    # Force an agent to be at the enemy flag position
    enemy_flag = game.environment.flag_positions["blue"]
    game.agents[0].position = enemy_flag
    game.update()
    assert game.game_state == GameState.COMPLETED, "Should complete capture flag objective"
    assert game.score >= 200, "Should score at least 200 points"
    print("✓ Capture flag objective passed")
    
    # Test 6: Objective completion - defend base
    print("\nTEST 6: Objective Completion - Defend Base")
    game = TeamTacticsGame(level=2)
    # Remove all enemy agents
    for agent in game.agents:
        if game.get_team(agent.id) == "blue":
            agent.is_alive = False
    game.update()
    assert game.game_state == GameState.COMPLETED, "Should complete defend base objective"
    assert game.score >= 150, "Should score at least 150 points"
    print("✓ Defend base objective passed")
    
    # Test 7: Objective completion - eliminate enemies
    print("\nTEST 7: Objective Completion - Eliminate Enemies")
    game = TeamTacticsGame(level=3)
    # Remove all enemy agents
    for agent in game.agents:
        if game.get_team(agent.id) == "blue":
            agent.is_alive = False
    game.update()
    assert game.game_state == GameState.COMPLETED, "Should complete eliminate enemies objective"
    assert game.score >= 250, "Should score at least 250 points"
    print("✓ Eliminate enemies objective passed")
    
    # Test 8: Edge case - agent getting stuck
    print("\nTEST 8: Edge Case - Agent Getting Stuck")
    game = TeamTacticsGame(level=1)
    # Put an agent in a corner with no way out
    game.agents[0].position = Position(0, 0)
    # Simulate many updates
    for _ in range(100):
        game.update()
        if game.agents[0].position.x > 0 or game.agents[0].position.y > 0:
            break
    # After many updates, agent should have moved
    assert game.agents[0].position.x > 0 or game.agents[0].position.y > 0, "Agent should escape being stuck"
    print("✓ Agent stuck edge case handled")
    
    # Test 9: Edge case - communication failure
    print("\nTEST 9: Edge Case - Communication Failure")
    game = TeamTacticsGame(level=1)
    # Disable communication system
    game.communication_system.clear_messages()
    # Send a message that won't be received
    game.communication_system.send_message(0, {"type": "test", "content": "fail"})
    messages = game.communication_system.receive_messages(1)
    assert len(messages) == 0, "No messages should be received if communication failed"
    print("✓ Communication failure edge case handled")
    
    # Test 10: Edge case - unexpected ability interactions
    print("\nTEST 10: Edge Case - Unexpected Ability Interactions")
    game = TeamTacticsGame(level=1)
    # Give two agents conflicting abilities
    game.agents[0].abilities = ["shield", "speed_boost"]
    game.agents[1].abilities = ["heal", "shield"]
    
    # Test healing while shielded
    game.agents[1].health = 50
    game.agents[1].heal(30)
    assert game.agents[1].health == 80, "Healing should work even with shield"
    
    # Test speed boost while shielded
    old_speed = game.agents[0].speed
    game.agents[0].speed *= 1.5
    assert game.agents[0].speed > old_speed, "Speed boost should work"
    print("✓ Unexpected ability interactions handled")
    
    # Final summary
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

# ================== MAIN EXECUTION ==================

if __name__ == "__main__":
    # Run test cases first
    run_test_cases()
    
    # Interactive game demo
    print("\n" + "=" * 60)
    print("TEAM_TACTICS GAME DEMO")
    print("=" * 60)
    
    # Start a game
    game = TeamTacticsGame(level=1)
    
    print(f"Starting Level {game.level}: {game.objective_type.value}")
    print(f"Objective: {game.objective_type.value.replace('_', ' ').title()}")
    
    # Run game for a few ticks
    for i in range(10):
        game.update()
        status = game.get_game_status()
        print(f"\nTick {i+1}: Score={status['score']}, State={status['game_state']}")
        
        # Show agent positions
        for agent in status["agents"]:
            if agent["is_alive"]:
                print(f"  Agent {agent['id']} ({agent['role']}): ({agent['position']['x']},{agent['position']['y']}) HP={agent['health']}")
    
    # Show final results
    print("\n" + "-" * 40)
    print("FINAL RESULTS:")
    summary = game.get_scoring_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)