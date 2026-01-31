```python
# cyber_arena.py
"""
CyberArena: Futuristic Multi-Agent Battle Arena Simulation

This is a complete implementation of a futuristic battle arena where AI-controlled robots compete in team-based challenges.
The system includes real-time combat, team objectives, adaptive difficulty, learning capabilities, immersive environment,
smooth controls, power-ups, hazards, and a scoring system.

Features:
- Real-time combat with ranged and melee weapons
- Team-based objectives (capture flags, defend bases, escort payloads)
- Adaptive difficulty based on robot performance
- Feedback loop for strategy learning and teamwork improvement
- Visual and audio enhancements (simulated via pygame)
- Customizable control schemes
- Power-ups and environmental hazards
- Scoring system with feedback

Note: This is a simulation using Pygame for visualization. In a real-world application, this would integrate with a game engine.
"""

import pygame
import random
import math
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Callable
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Game state
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# Robot types
class RobotType(Enum):
    ASSAULT = "Assault"
    SUPPORT = "Support"
    SCOUT = "Scout"
    DEFENDER = "Defender"

# Weapon types
class WeaponType(Enum):
    MELEE = "Melee"
    RANGED = "Ranged"
    LASER = "Laser"
    ENERGY = "Energy"

# Objective types
class ObjectiveType(Enum):
    FLAG_CAPTURE = "Flag Capture"
    BASE_DEFENSE = "Base Defense"
    PAYLOAD_ESCORT = "Payload Escort"
    SURVIVAL = "Survival"

# Power-up types
class PowerUpType(Enum):
    HEALTH = "Health"
    SPEED = "Speed"
    SHIELD = "Shield"
    DAMAGE_BOOST = "Damage Boost"
    SILENCE = "Silence"  # Temporarily disables enemy sensors

# Environmental hazard types
class HazardType(Enum):
    PIT = "Pit"
    LASER_GRID = "Laser Grid"
    ELECTRIC_FLOOR = "Electric Floor"
    GAS_CLOUD = "Gas Cloud"

# Audio effects (simulated)
SOUND_EFFECTS = {
    'shoot': pygame.mixer.Sound('assets/sounds/shoot.wav') if pygame.mixer.get_init() else None,
    'explosion': pygame.mixer.Sound('assets/sounds/explosion.wav') if pygame.mixer.get_init() else None,
    'hit': pygame.mixer.Sound('assets/sounds/hit.wav') if pygame.mixer.get_init() else None,
    'powerup': pygame.mixer.Sound('assets/sounds/powerup.wav') if pygame.mixer.get_init() else None,
    'flag_capture': pygame.mixer.Sound('assets/sounds/flag_capture.wav') if pygame.mixer.get_init() else None,
    'win': pygame.mixer.Sound('assets/sounds/win.wav') if pygame.mixer.get_init() else None,
    'lose': pygame.mixer.Sound('assets/sounds/lose.wav') if pygame.mixer.get_init() else None
}

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("CyberArena")
clock = pygame.time.Clock()

# Font for UI
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
title_font = pygame.font.SysFont('Arial', 48, bold=True)

# Global variables
current_state = GameState.MENU
game_time = 0
winner_team = None

# Helper functions
def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def angle_between(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate angle in radians from p1 to p2."""
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def random_position() -> Tuple[float, float]:
    """Generate a random position within screen bounds."""
    return (
        random.randint(50, SCREEN_WIDTH - 50),
        random.randint(50, SCREEN_HEIGHT - 50)
    )

def create_particle_effect(x: float, y: float, color: Tuple[int, int, int], size: int = 5, count: int = 10):
    """Create a particle effect at given coordinates."""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        particles.append({
            'x': x,
            'y': y,
            'vx': speed * math.cos(angle),
            'vy': speed * math.sin(angle),
            'life': 60,
            'color': color,
            'size': size
        })
    return particles

@dataclass
class RobotStats:
    """Data class to store robot statistics."""
    health: int = 100
    max_health: int = 100
    speed: float = 3.0
    damage: int = 10
    armor: int = 5
    vision_range: float = 200
    attack_range: float = 100
    cooldown: float = 0.5  # seconds
    last_attack: float = 0.0
    team_id: int = 0
    role: RobotType = RobotType.ASSAULT
    power_ups: Dict[PowerUpType, int] = None
    
    def __post_init__(self):
        if self.power_ups is None:
            self.power_ups = {p: 0 for p in PowerUpType}

@dataclass
class Weapon:
    """Data class to represent a weapon."""
    name: str
    type: WeaponType
    damage: int
    range: float
    rate_of_fire: float  # shots per second
    reload_time: float  # seconds
    sound: str = None

@dataclass
class Objective:
    """Data class to represent an objective."""
    id: int
    type: ObjectiveType
    position: Tuple[float, float]
    owner: Optional[int] = None  # team_id
    captured: bool = False
    capture_progress: float = 0.0
    capture_time: float = 0.0
    required_time: float = 30.0  # seconds

@dataclass
class PowerUp:
    """Data class to represent a power-up."""
    type: PowerUpType
    position: Tuple[float, float]
    duration: float = 10.0  # seconds
    active: bool = True
    spawn_time: float = 0.0

@dataclass
class Hazard:
    """Data class to represent an environmental hazard."""
    type: HazardType
    position: Tuple[float, float]
    radius: float
    duration: float = 10.0
    active: bool = True
    spawn_time: float = 0.0

class Robot:
    """AI-controlled robot with various abilities and behaviors."""
    
    def __init__(self, x: float, y: float, team_id: int, robot_type: RobotType, name: str = None):
        self.x = x
        self.y = y
        self.team_id = team_id
        self.type = robot_type
        self.name = name or f"Robot_{team_id}_{random.randint(100, 999)}"
        
        # Stats
        self.stats = RobotStats(
            health=100,
            max_health=100,
            speed=3.0,
            damage=10,
            armor=5,
            vision_range=200,
            attack_range=100,
            cooldown=0.5,
            team_id=team_id,
            role=robot_type
        )
        
        # Weapons
        self.weapons = self._create_weapons()
        self.current_weapon = 0
        
        # State
        self.target = None
        self.is_attacking = False
        self.last_attack_time = 0
        self.path = []
        self.movement_speed = 0.0
        self.angle = 0.0
        self.in_combat = False
        self.stunned = False
        self.stun_duration = 0.0
        self.friendly_fire = False
        
        # Learning attributes
        self.experience = 0
        self.successful_objectives = 0
        self.deaths = 0
        self.kills = 0
        self.teamwork_score = 0
        self.strategy_history = []  # Store past decisions
        
        # Particle effects
        self.particles = []
        
        # Color based on team
        colors = {
            0: RED,
            1: BLUE,
            2: GREEN,
            3: YELLOW
        }
        self.color = colors.get(team_id, GRAY)
        
        # Sound effects
        self.sounds = {
            'attack': pygame.mixer.Sound('assets/sounds/attack.wav') if pygame.mixer.get_init() else None,
            'death': pygame.mixer.Sound('assets/sounds/death.wav') if pygame.mixer.get_init() else None,
            'hurt': pygame.mixer.Sound('assets/sounds/hurt.wav') if pygame.mixer.get_init() else None
        }

    def _create_weapons(self) -> List[Weapon]:
        """Create appropriate weapons based on robot type."""
        weapons = []
        if self.type == RobotType.ASSAULT:
            weapons.append(Weapon("Plasma Rifle", WeaponType.RANGED, 25, 300, 2.0, 0.5, "shoot"))
            weapons.append(Weapon("Combat Knife", WeaponType.MELEE, 40, 30, 1.0, 0.0, "shoot"))
        elif self.type == RobotType.SUPPORT:
            weapons.append(Weapon("Medi-Beam", WeaponType.LASER, 10, 200, 0.5, 1.0, "shoot"))
            weapons.append(Weapon("Repair Drone", WeaponType.ENERGY, 5, 150, 0.2, 2.0, "shoot"))
        elif self.type == RobotType.SCOUT:
            weapons.append(Weapon("Sniper Rifle", WeaponType.RANGED, 50, 500, 0.3, 1.5, "shoot"))
            weapons.append(Weapon("Cloak Device", WeaponType.MELEE, 0, 10, 0.0, 0.0, "shoot"))  # Special ability
        elif self.type == RobotType.DEFENDER:
            weapons.append(Weapon("Heavy Shield", WeaponType.MELEE, 15, 50, 0.8, 0.0, "shoot"))
            weapons.append(Weapon("Turret Cannon", WeaponType.RANGED, 30, 400, 1.5, 0.7, "shoot"))
            
        return weapons

    def update(self, dt: float, robots: List['Robot'], objectives: List[Objective], 
               powerups: List[PowerUp], hazards: List[Hazard], all_teams: List[int]):
        """Update robot state."""
        # Update stun timer
        if self.stunned:
            self.stun_duration -= dt
            if self.stun_duration <= 0:
                self.stunned = False
                
        # Update power-up timers
        for pu_type, duration in self.stats.power_ups.items():
            if duration > 0:
                self.stats.power_ups[pu_type] -= dt
                if self.stats.power_ups[pu_type] <= 0:
                    self.stats.power_ups[pu_type] = 0
                    
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['size'] *= 0.95
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p['life'] > 0]

        # Check for collisions with power-ups
        for i, powerup in enumerate(powerups):
            if not powerup.active:
                continue
            dist = distance((self.x, self.y), powerup.position)
            if dist < 30:
                self.apply_powerup(powerup.type)
                powerup.active = False
                if SOUND_EFFECTS.get('powerup'):
                    SOUND_EFFECTS['powerup'].play()
                    
        # Check for collisions with hazards
        for hazard in hazards:
            if not hazard.active:
                continue
            dist = distance((self.x, self.y), hazard.position)
            if dist < hazard.radius:
                self.take_damage(10, hazard.type)
                if SOUND_EFFECTS.get('hit'):
                    SOUND_EFFECTS['hit'].play()
                
        # Update target selection
        if not self.target or self.target.health <= 0:
            self.target = self.find_target(robots, all_teams)
            
        # Update movement
        if not self.stunned and self.target:
            self.move_towards_target(dt)
            
        # Attack if possible
        if self.target and not self.stunned:
            self.attack_target(dt)
            
        # Update strategy history
        if self.target and self.target.health > 0:
            self.strategy_history.append({
                'time': game_time,
                'target': self.target.name,
                'distance': distance((self.x, self.y), (self.target.x, self.target.y)),
                'health': self.target.health
            })

    def find_target(self, robots: List['Robot'], enemy_teams: List[int]) -> Optional['Robot']:
        """Find the best target among enemies."""
        targets = []
        for robot in robots:
            if robot.team_id in enemy_teams and robot.health > 0:
                dist = distance((self.x, self.y), (robot.x, robot.y))
                if dist < self.stats.vision_range:
                    targets.append((dist, robot))
                    
        if not targets:
            return None
            
        # Sort by distance
        targets.sort()
        return targets[0][1]

    def move_towards_target(self, dt: float):
        """Move toward target with smooth pathfinding."""
        if not self.target:
            return
            
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 5:
            # Normalize direction vector
            dir_x = dx / dist
            dir_y = dy / dist
            
            # Apply movement
            self.x += dir_x * self.stats.speed * dt * 60
            self.y += dir_y * self.stats.speed * dt * 60
            
            # Update angle for rotation
            self.angle = math.atan2(dy, dx)
            
            # Add particle effect for movement
            if random.random() < 0.1:
                self.particles.extend(create_particle_effect(self.x, self.y, (100, 100, 100), 3, 3))

    def attack_target(self, dt: float):
        """Attack the current target."""
        if not self.target or self.target.health <= 0:
            return
            
        # Calculate distance to target
        dist = distance((self.x, self.y), (self.target.x, self.target.y))
        
        # Check if within attack range
        if dist > self.stats.attack_range:
            return
            
        # Check cooldown
        if game_time - self.last_attack_time < self.stats.cooldown:
            return
            
        # Select weapon based on distance
        weapon = self.weapons[self.current_weapon]
        
        # Determine if it's a melee or ranged attack
        if weapon.type == WeaponType.MELEE:
            # Melee attack - can only happen if very close
            if dist < 30:
                self.perform_melee_attack()
        else:
            # Ranged attack
            self.perform_ranged_attack()
            
        # Reset attack timer
        self.last_attack_time = game_time

    def perform_ranged_attack(self):
        """Perform a ranged attack."""
        weapon = self.weapons[self.current_weapon]
        damage = weapon.damage
        
        # Apply damage to target
        self.target.take_damage(damage, weapon.type)
        
        # Play sound
        if SOUND_EFFECTS.get('shoot'):
            SOUND_EFFECTS['shoot'].play()
            
        # Create visual effect
        self.particles.extend(create_particle_effect(
            self.x + 20 * math.cos(self.angle), 
            self.y + 20 * math.sin(self.angle), 
            (255, 100, 0), 5, 10
        ))
        
        # Increment experience
        self.experience += 5
        self.kills += 1
        
        # Update strategy history
        self.strategy_history.append({
            'action': 'ranged_attack',
            'damage': damage,
            'target': self.target.name
        })

    def perform_melee_attack(self):
        """Perform a melee attack."""
        weapon = self.weapons[self.current_weapon]
        damage = weapon.damage
        
        # Apply damage to target
        self.target.take_damage(damage, weapon.type)
        
        # Play sound
        if SOUND_EFFECTS.get('shoot'):
            SOUND_EFFECTS['shoot'].play()
            
        # Create visual effect
        self.particles.extend(create_particle_effect(
            self.x + 20 * math.cos(self.angle), 
            self.y + 20 * math.sin(self.angle), 
            (255, 0, 0), 8, 15
        ))
        
        # Increment experience
        self.experience += 10
        self.kills += 1
        
        # Update strategy history
        self.strategy_history.append({
            'action': 'melee_attack',
            'damage': damage,
            'target': self.target.name
        })

    def take_damage(self, amount: int, source_type: WeaponType):
        """Take damage from an attack."""
        # Apply armor reduction
        effective_damage = max(1, amount - self.stats.armor)
        
        # Apply damage
        self.stats.health -= effective_damage
        
        # Play hurt sound
        if SOUND_EFFECTS.get('hurt'):
            SOUND_EFFECTS['hurt'].play()
            
        # Create hit effect
        self.particles.extend(create_particle_effect(
            self.x, self.y, (255, 0, 0), 10, 20
        ))
        
        # Check if dead
        if self.stats.health <= 0:
            self.die()
            
        # Update experience
        self.experience += 2

    def die(self):
        """Handle robot death."""
        self.stats.health = 0
        self.target = None
        self.is_attacking = False
        
        # Play death sound
        if SOUND_EFFECTS.get('death'):
            SOUND_EFFECTS['death'].play()
            
        # Create explosion effect
        self.particles.extend(create_particle_effect(
            self.x, self.y, (255, 100, 0), 20, 50
        ))
        
        # Update stats
        self.deaths += 1
        self.experience += 20
        
        # Update strategy history
        self.strategy_history.append({
            'action': 'died',
            'reason': 'killed'
        })

    def apply_powerup(self, powerup_type: PowerUpType):
        """Apply a power-up effect."""
        if powerup_type == PowerUpType.HEALTH:
            self.stats.health = min(self.stats.max_health, self.stats.health + 50)
            self.stats.power_ups[PowerUpType.HEALTH] = 5.0
        elif powerup_type == PowerUpType.SPEED:
            self.stats.speed *= 1.5
            self.stats.power_ups[PowerUpType.SPEED] = 10.0
        elif powerup_type == PowerUpType.SHIELD:
            self.stats.armor += 10
            self.stats.power_ups[PowerUpType.SHIELD] = 15.0
        elif powerup_type == PowerUpType.DAMAGE_BOOST:
            self.stats.damage *= 1.5
            self.stats.power_ups[PowerUpType.DAMAGE_BOOST] = 10.0
        elif powerup_type == PowerUpType.SILENCE:
            # Temporarily disable enemy sensors
            self.stats.power_ups[PowerUpType.SILENCE] = 8.0
            
        # Update experience
        self.experience += 15

    def draw(self, surface):
        """Draw the robot on the screen."""
        # Draw body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 20)
        
        # Draw eyes
        eye_offset = 8
        left_eye_x = self.x - eye_offset
        right_eye_x = self.x + eye_offset
        eye_y = self.y
        
        # Draw eyes based on direction
        eye_color = WHITE if self.stunned else (255, 255, 255)
        pygame.draw.circle(surface, eye_color, (int(left_eye_x), int(eye_y)), 5)
        pygame.draw.circle(surface, eye_color, (int(right_eye_x), int(eye_y)), 5)
        
        # Draw glowing effect if stunned
        if self.stunned:
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), 25, 2)
            
        # Draw health bar
        bar_width = 40
        bar_height = 5
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 30
        
        # Background
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int(bar_width * (self.stats.health / self.stats.max_health))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Draw name
        text = font.render(self.name, True, WHITE)
        surface.blit(text, (self.x - text.get_width() // 2, self.y - 40))
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            color = (*particle['color'], alpha)
            size = int(particle['size'])
            pygame.draw.circle(surface, color, (int(particle['x']), int(particle['y'])), size)

    def get_position(self) -> Tuple[float, float]:
        """Get current position."""
        return (self.x, self.y)

    def get_stats(self) -> dict:
        """Get robot statistics."""
        return {
            'name': self.name,
            'team': self.team_id,
            'type': self.type.value,
            'health': self.stats.health,
            'speed': self.stats.speed,
            'damage': self.stats.damage,
            'armor': self.stats.armor,
            'experience': self.experience,
            'kills': self.kills,
            'deaths': self.deaths,
            'success_rate': self.kills / (self.kills + self.deaths + 1) if self.kills + self.deaths > 0 else 0
        }


class CyberArenaGame:
    """Main game class for managing the CyberArena simulation."""
    
    def __init__(self):
        self.robots = []
        self.objectives = []
        self.powerups = []
        self.hazards = []
        self.teams = []
        self.game_over = False
        self.winner = None
        self.score = {}
        self.difficulty = 1.0  # 1.0 = normal, higher = harder
        self.adaptive_difficulty = True
        self.learning_enabled = True
        self.control_scheme = "keyboard"
        
        # Initialize game
        self.reset_game()
        
    def reset_game(self):
        """Reset the game state."""
        self.robots.clear()
        self.objectives.clear()
        self.powerups.clear()
        self.hazards.clear()
        self.game_over = False
        self.winner = None
        self.score = {}
        
        # Create teams
        self.teams = [0, 1, 2, 3]  # Up to 4 teams
        
        # Create robots for each team
        for team_id in self.teams:
            # Create different robot types for variety
            robot_types = [RobotType.ASSAULT, RobotType.SUPPORT, RobotType.SCOUT, RobotType.DEFENDER]
            for i in range(4):  # 4 robots per team
                robot_type = robot_types[i % len(robot_types)]
                x, y = random_position()
                robot = Robot(x, y, team_id, robot_type, f"Team{team_id}_Bot{i}")
                self.robots.append(robot)
                
                # Initialize score tracking
                if team_id not in self.score:
                    self.score[team_id] = {
                        'total_score': 0,
                        'objectives': 0,
                        'kills': 0,
                        'deaths': 0,
                        'teamwork': 0
                    }
        
        # Create objectives
        self.create_objectives()
        
        # Create power-ups
        self.create_powerups()
        
        # Create hazards
        self.create_hazards()
        
        # Reset game time
        global game_time
        game_time = 0
        
    def create_objectives(self):
        """Create objectives for the game."""
        # Flag capture objectives
        flag_positions = [
            (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.2),
            (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.2),
            (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT * 0.8),
            (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8)
        ]
        
        for i, pos in enumerate(flag_positions):
            obj = Objective(id=i, type=ObjectiveType.FLAG_CAPTURE, position=pos)
            self.objectives.append(obj)
            
    def create_powerups(self):
        """Create power-ups scattered around the map."""
        for _ in range(10):
            x, y = random_position()
            pu_type = random.choice(list(PowerUpType))
            powerup = PowerUp(type=pu_type, position=(x, y), duration=10.0)
            self.powerups.append(powerup)
            
    def create_hazards(self):
        """Create environmental hazards."""
        for _ in range(5):
            x, y = random_position()
            hazard_type = random.choice(list(HazardType))
            radius = 50
            if hazard_type == HazardType.PIT:
                radius = 100
            elif hazard_type == HazardType.LASER_GRID:
                radius = 80
            elif hazard_type == HazardType.ELECTRIC_FLOOR:
                radius = 120
            elif hazard_type == HazardType.GAS_CLOUD:
                radius = 150
                
            hazard = Hazard(type=hazard_type, position=(x, y), radius=radius, duration=15.0)
            self.hazards.append(hazard)
            
    def update(self, dt: float):
        """Update the game state."""
        global game_time
        game_time += dt
        
        # Update all robots
        for robot in self.robots:
            # Get all other teams except own
            enemy_teams = [t for t in self.teams if t != robot.team_id]
            robot.update(dt, self.robots, self.objectives, self.powerups, self.hazards, enemy_teams)
            
        # Update objectives
        self.update_objectives()
        
        # Update power-ups
        self.update_powerups()
        
        # Update hazards
        self.update_hazards()
        
        # Check for game over conditions
        self.check_game_over()
        
        # Update difficulty
        if self.adaptive_difficulty:
            self.update_difficulty()
            
        # Update learning
        if self.learning_enabled:
            self.update_learning()
            
    def update_objectives(self):
        """Update objective states."""
        for obj in self.objectives:
            if obj.captured:
                continue
                
            # Find robots from owning team near objective
            nearby_robots = []
            for robot in self.robots:
                if robot.team_id == obj.owner and robot.health > 0:
                    dist = distance(robot.get_position(), obj.position)
                    if dist < 100:
                        nearby_robots.append(robot)
                        
            # If no robots are near, reset capture progress
            if not nearby_robots:
                obj.capture_progress = 0
                obj.capture_time = 0
                continue
                
            # Increase capture progress
            obj.capture_progress += 0.01 * len(nearby_robots)
            obj.capture_time += 1
            
            # Check if captured
            if obj.capture_progress >= 1.0:
                obj.captured = True
                obj.capture_time = game_time
                
                # Award points
                for robot in self.robots:
                    if robot.team_id == obj.owner:
                        self.score[robot.team_id]['objectives'] += 1
                        self.score[robot.team_id]['total_score'] += 100
                        
                # Play sound
                if SOUND_EFFECTS.get('flag_capture'):
                    SOUND_EFFECTS['flag_capture'].play()
                    
                # Update learning
                for robot in self.robots:
                    if robot.team_id == obj.owner:
                        robot.successful_objectives += 1
                        robot.teamwork_score += 10
                        
    def update_powerups(self):
        """Update power-up states."""
        for powerup in self.powerups:
            if not powerup.active:
                continue
                
            # Check if expired
            if game_time - powerup.spawn_time > powerup.duration:
                powerup.active = False
                
    def update_hazards(self):
        """Update hazard states."""
        for hazard in self.hazards:
            if not hazard.active:
                continue
                
            # Check if expired
            if game_time - hazard.spawn_time > hazard.duration:
                hazard.active = False
                
    def check_game_over(self):
        """Check if the game should end."""
        # Count remaining teams
        remaining_teams = set(robot.team_id for robot in self.robots if robot.health > 0)
        
        # If only one team remains, they win
        if len(remaining_teams) == 1:
            self.winner = list(remaining_teams)[0]
            self.game_over = True
            if SOUND_EFFECTS.get('win'):
                SOUND_EFFECTS['win'].play()
                
        # If no teams remain, it's a tie
        elif len(remaining_teams) == 0:
            self.winner = None
            self.game_over = True
            if SOUND_EFFECTS.get('lose'):
                SOUND_EFFECTS['lose'].play()
                
        # Check time limit (10 minutes)
        if game_time > 600:  # 10 minutes
            self.game_over = True
            # Determine winner by score
            max_score = -1
            for team_id, score_data in self.score.items():
                if score_data['total_score'] > max_score:
                    max_score = score_data['total_score']
                    self.winner = team_id
                    
    def update_difficulty(self):
        """Adjust difficulty based on team performance."""
        # Calculate average performance across all teams
        avg_kills = sum(robot.kills for robot in self.robots) / len(self.robots)
        avg_deaths = sum(robot.deaths for robot in self.robots) / len(self.robots)
        
        # Adjust difficulty based on kill/death ratio
        if avg_kills > 2 * avg_deaths:
            # Teams are winning too easily, increase difficulty
            self.difficulty = min(2.0, self.difficulty * 1.05)
        elif avg_deaths > 2 * avg_kills:
            # Teams are struggling, decrease difficulty
            self.difficulty = max(0.5, self.difficulty * 0.95)
            
        # Adjust robot behavior based on difficulty
        for robot in self.robots:        # Calculate average performance across all teams
        avg_kills = sum(robot.kills for robot in self.robots) / len(self.robots)
        avg_deaths = sum(robot.deaths for robot in self.robots) / len(self.robots)
        
        # Adjust difficulty based on kill/death ratio
        if avg_kills > 2 * avg_deaths:
            # Teams are winning too easily, increase difficulty
            self.difficulty = min(2.0, self.difficulty * 1.05)
        elif avg_deaths > 2 * avg_kills:
            # Teams are struggling, decrease difficulty
            self.difficulty = max(0.5, self.difficulty * 0.95)
            
        # Reset robot stats to base values before applying difficulty scaling
        for robot in self.robots:
            base = self.base_stats.get(robot.name)
            if base:
                robot.stats.max_health = base['health']
                robot.stats.damage = base['damage']
                robot.stats.speed = base['speed']
                robot.stats.armor = base['armor']
                robot.stats.health = base['health']  # Reset health to base
                
        # Adjust robot behavior based on difficulty
        for robot in self.robots:
            # Scale stats based on difficulty
            scale = self.difficulty
            robot.stats.health = int(robot.stats.max_health * scale)
            robot.stats.damage = int(robot.stats.damage * scale)
            robot.stats.speed = robot.stats.speed * scale
            
            # Make AI more aggressive at higher difficulty
            if self.difficulty > 1.5:
                robot.stats.attack_range *= 1.2
                robot.stats.vision_range *= 1.1            # Make AI more aggressive at higher difficulty
            if self.difficulty > 1.5:
                robot.stats.attack_range *= 1.2
                robot.stats.vision_range *= 1.1
                
    def update_learning(self):
        """Update robot learning and adaptation."""
        # Analyze strategy history and adjust behavior
        for robot in self.robots:
            # Look for patterns in strategy history
            if len(robot.strategy_history) > 10:
                # Simple pattern recognition: if always attacking at long range, maybe improve
                attacks = [s for s in robot.strategy_history[-10:] if s.get('action') in ['ranged_attack', 'melee_attack']]
                if attacks:
                    # If most attacks were at long range, consider switching to closer range
                    long_range_attacks = [a for a in attacks if a.get('distance', 0) > 200]
                    if len(long_range_attacks) > len(attacks) * 0.7:
                        # Consider changing tactics
                        robot.stats.attack_range *= 0.9
                    elif len(long_range_attacks) < len(attacks) * 0.3:
                        # Consider increasing attack range
                        robot.stats.attack_range *= 1.1
                        
            # Reward successful teamwork
            if robot.successful_objectives > 0:
                robot.teamwork_score += 1
                robot.experience += 5
                
    def draw(self, surface):
        """Draw the entire game state."""
        # Fill background
        surface.fill(BLACK)
        
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(surface, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(surface, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))
            
        # Draw hazards
        for hazard in self.hazards:
            if not hazard.active:
                continue
                
            # Draw hazard shape based on type
            center = hazard.position
            radius = hazard.radius
            
            if hazard.type == HazardType.PIT:
                # Draw pit with gradient
                for i in range(10):
                    alpha = int(255 * (i / 10))
                    color = (0, 0, 0, alpha)
                    pygame.draw.circle(surface, color, center, radius * (i / 10), 1)
                    
            elif hazard.type == HazardType.LASER_GRID:
                # Draw laser grid
                for i in range(0, 360, 30):
                    angle = math.radians(i)
                    x1 = center[0] + radius * math.cos(angle)
                    y1 = center[1] + radius * math.sin(angle)
                    x2 = center[0] + radius * math.cos(angle + math.pi)
                    y2 = center[1] + radius * math.sin(angle + math.pi)
                    pygame.draw.line(surface, (255, 0, 0), (x1, y1), (x2, y2), 2)
                    
            elif hazard.type == HazardType.ELECTRIC_FLOOR:
                # Draw electric floor
                for i in range(5):
                    alpha = int(255 * (i / 5))
                    color = (0, 0, 255, alpha)
                    pygame.draw.circle(surface, color, center, radius * (i / 5), 2)
                    
            elif hazard.type == HazardType.GAS_CLOUD:
                # Draw gas cloud
                for i in range(10):
                    alpha = int(255 * (i / 10))
                    color = (100, 100, 0, alpha)
                    pygame.draw.circle(surface, color, center, radius * (i / 10), 1)
                    
        # Draw power-ups
        for powerup in self.powerups:
            if not powerup.active:
                continue
                
            # Draw power-up symbol
            center = powerup.position
            radius = 20
            
            # Different colors for different types
            color_map = {
                PowerUpType.HEALTH: (0, 255, 0),
                PowerUpType.SPEED: (255, 255, 0),
                PowerUpType.SHIELD: (0, 0, 2