#!/usr/bin/env python3
"""
Mining By The Numbers - Terminal UI Framework
ASCII-based mine management simulator set in 1970s Nevada
"""

import curses
import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional

class TerminalColors:
    """IBM terminal color scheme - amber/red/grey/blue"""
    AMBER = 3    # Yellow/Brown
    RED = 1      # Red for heat/danger
    BLUE = 4     # Blue for water/info
    WHITE = 7    # White for normal text
    GREY = 8     # Grey/black for background/borders

class MiningGame:
    def __init__(self):
        self.game_state = {
            'day': 1,
            'cash': 50000,
            'mob_debt': 200000,
            'tons_surface': 0,
            'heat_levels': {
                'mob': 25,
                'fed': 10,
                'crew': 15
            },
            'mine_conditions': {
                'temp': 20,
                'ground': 15,
                'ventilation': 10
            },
            'nightshift_coins': 3,
            'current_level': 1000,
            'is_pdr_day': True,  # Monday is PDR day
            'foremen': {},
            'equipment': {},
            'mine_map': {},
            'day_of_week': 1  # 1=Monday, 7=Sunday
        }
        
        self.initialize_foremen()
        self.initialize_equipment()
        self.initialize_mine_map()
        
    def initialize_foremen(self):
        """Initialize starting foremen with random stats"""
        foreman_types = [
            {
                'name': 'Jake "Big Jake" Morrison',
                'type': 'development',
                'production': 75,
                'reliability': 45,
                'crew_moral': 55,
                'secret_traits': ['cuts_corners'],
                'weeks_employed': 0,
                'grace_period': 3
            },
            {
                'name': 'Tommy Vasquez',
                'type': 'production',
                'production': 65,
                'reliability': 55,
                'crew_moral': 60,
                'secret_traits': ['bbq_enthusiast'],
                'weeks_employed': 0,
                'grace_period': 3
            },
            {
                'name': 'Earl Peters',
                'type': 'maintenance',
                'production': 50,
                'reliability': 80,
                'crew_moral': 65,
                'secret_traits': ['safety_first'],
                'weeks_employed': 0,
                'grace_period': 3
            }
        ]
        
        for f in foreman_types:
            self.game_state['foremen'][f['type']] = f
            
    def initialize_equipment(self):
        """Initialize starting equipment"""
        starting_equipment = [
            {
                'id': 'LOA01',
                'type': 'loader',
                'size': 'small',
                'availability': 60,
                'condition': 'used',
                'value': 45000,
                'purchase_price': 90000,
                'assigned_to': None,
                'status': 'manned'
            },
            {
                'id': 'HTK01',
                'type': 'truck',
                'size': 'medium',
                'availability': 75,
                'condition': 'used',
                'value': 35000,
                'purchase_price': 70000,
                'assigned_to': None,
                'status': 'manned'
            },
            {
                'id': 'DRL01',
                'type': 'drill',
                'size': 'jackleg',
                'availability': 55,
                'condition': 'used',
                'value': 25000,
                'purchase_price': 50000,
                'assigned_to': None,
                'status': 'manned'
            }
        ]
        
        for eq in starting_equipment:
            self.game_state['equipment'][eq['id']] = eq
            
    def initialize_mine_map(self):
        """Initialize basic mine layout"""
        self.game_state['mine_map'] = {
            'levels': {
                1000: {
                    'developed': True,
                    'headings': ['main_drift'],
                    'stopes': {
                        'lucky_7': {
                            'status': 'active',
                            'ore_grade': 0.15,
                            'tons_remaining': 500
                        }
                    }
                },
                1300: {
                    'developed': True,
                    'headings': [],
                    'stopes': {}
                }
            },
            'shaft_bottom': 1300
        }
        
    def init_colors(self, stdscr):
        """Initialize curses color pairs for terminal"""
        curses.start_color()
        curses.use_default_colors()
        
        # Color pairs: (foreground, background)
        curses.init_pair(1, TerminalColors.AMBER, -1)     # Main text
        curses.init_pair(2, TerminalColors.RED, -1)       # Heat/danger
        curses.init_pair(3, TerminalColors.BLUE, -1)      # Water/info
        curses.init_pair(4, TerminalColors.WHITE, -1)     # Normal text
        
    def draw_header(self, stdscr):
        """Draw the top status bar with heat sliders and metrics"""
        height, width = stdscr.getmaxyx()
        
        # Heat sliders (left side)
        heat_y = 1
        stdscr.addstr(heat_y, 2, "MOB", curses.color_pair(2))
        stdscr.addstr(heat_y + 1, 2, "FED", curses.color_pair(2)) 
        stdscr.addstr(heat_y + 2, 2, "CREW", curses.color_pair(2))
        
        # Heat slider bars
        for i, (heat_type, value) in enumerate(self.game_state['heat_levels'].items()):
            bar_length = 20
            filled = int((value / 100) * bar_length)
            empty = bar_length - filled
            
            bar = "█" * filled + "░" * empty
            color = curses.color_pair(2) if value > 75 else curses.color_pair(1)
            stdscr.addstr(heat_y + i, 8, f"[{bar}] {value}%", color)
            
        # Mine condition sliders (right side)
        conditions_x = width // 2 + 5
        stdscr.addstr(heat_y, conditions_x, "TEMP", curses.color_pair(1))
        stdscr.addstr(heat_y + 1, conditions_x, "GROUND", curses.color_pair(1))
        stdscr.addstr(heat_y + 2, conditions_x, "VENT", curses.color_pair(1))
        
        for i, (condition, value) in enumerate(self.game_state['mine_conditions'].items()):
            bar_length = 20
            filled = int((value / 100) * bar_length)
            empty = bar_length - filled
            
            bar = "█" * filled + "░" * empty
            stdscr.addstr(heat_y + i, conditions_x + 8, f"[{bar}] {value}%", curses.color_pair(1))
            
    def draw_resources(self, stdscr):
        """Draw resource counters"""
        height, width = stdscr.getmaxyx()
        y = 5
        
        # Resources in amber/white
        stdscr.addstr(y, 2, f"CASH: ${self.game_state['cash']:,}", curses.color_pair(1))
        stdscr.addstr(y, 25, f"MOB DEBT: ${self.game_state['mob_debt']:,}", curses.color_pair(2))
        stdscr.addstr(y, 50, f"SURFACE TONS: {self.game_state['tons_surface']}", curses.color_pair(4))
        
    def draw_mine_map(self, stdscr):
        """Draw the ASCII mine map"""
        height, width = stdscr.getmaxyx()
        map_start_y = 8
        map_start_x = 2
        
        # Surface line
        surface_text = "SURFACE"
        surface_line = "▓" * (width - map_start_x - 2)
        stdscr.addstr(map_start_y, map_start_x, surface_text, curses.color_pair(1))
        stdscr.addstr(map_start_y + 1, map_start_x, surface_line, curses.color_pair(1))
        
        # Shaft - double vertical lines
        shaft_x = width // 4
        current_y = map_start_y + 3
        
        # Draw levels
        levels = [1000, 1300, 1600, 1900]
        for level in levels:
            # Level line
            level_text = f"LEVEL {level}"
            level_line = "█" * (width - shaft_x - 10)
            
            stdscr.addstr(current_y, map_start_x, level_text, curses.color_pair(1))
            
            if level == self.game_state['current_level']:
                # Active level - show some development
                stdscr.addstr(current_y, shaft_x, "║║", curses.color_pair(1))
                stdscr.addstr(current_y, shaft_x + 3, level_line, curses.color_pair(1))
                
                # Add some stope indicators
                if level == 1000:
                    stdscr.addstr(current_y, shaft_x + 10, "├─ LUCKY 7 [X]", curses.color_pair(1))
                    stdscr.addstr(current_y + 1, shaft_x + 10, "└─ MAIN DRIFT ───►", curses.color_pair(1))
            else:
                stdscr.addstr(current_y, shaft_x, "║║", curses.color_pair(1))
                
            current_y += 3
            
    def draw_equipment(self, stdscr):
        """Draw equipment status panel"""
        height, width = stdscr.getmaxyx()
        panel_x = width - 40
        panel_y = 8
        
        stdscr.addstr(panel_y, panel_x, "EQUIPMENT STATUS", curses.color_pair(1))
        stdscr.addstr(panel_y + 1, panel_x, "─" * 20, curses.color_pair(1))
        
        # Sample equipment
        equipment = [
            ("LOA01", 60, "Manned"),
            ("LOA02", 45, "Down"),
            ("HTK01", 75, "Manned"),
            ("HTK02", 80, "Standby"),
            ("DRL01", 55, "Manned"),
            ("DRL02", 30, "Down")
        ]
        
        for i, (name, avail, status) in enumerate(equipment):
            y = panel_y + 2 + i
            
            # Equipment name
            stdscr.addstr(y, panel_x, name, curses.color_pair(1))
            
            # Availability bar
            bar_length = 10
            filled = int((avail / 100) * bar_length)
            empty = bar_length - filled
            bar = "█" * filled + "░" * empty
            
            # Color based on availability
            color = curses.color_pair(2) if avail < 50 else curses.color_pair(1)
            stdscr.addstr(y, panel_x + 6, f"[{bar}]", color)
            stdscr.addstr(y, panel_x + 19, f"{avail}%", color)
            stdscr.addstr(y, panel_x + 25, status, curses.color_pair(4))
            
    def draw_footer(self, stdscr):
        """Draw footer with controls"""
        height, width = stdscr.getmaxyx()
        footer_y = height - 3
        
        controls = [
            "[S]tart Shift  [M]ine Map  [E]quipment  [P]DR Meeting  [H]elp  [Q]uit"
        ]
        
        for i, text in enumerate(controls):
            stdscr.addstr(footer_y + i, 2, text, curses.color_pair(4))
            
    def save_game(self):
        """Save game state to file"""
        save_data = {
            'timestamp': datetime.now().isoformat(),
            'game_state': self.game_state,
            'version': '0.1.0'
        }
        
        try:
            os.makedirs('saves', exist_ok=True)
            with open('saves/game_save.json', 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            return False
            
    def load_game(self) -> bool:
        """Load game state from file"""
        try:
            with open('saves/game_save.json', 'r') as f:
                save_data = json.load(f)
                self.game_state = save_data['game_state']
            return True
        except Exception as e:
            return False
            
    def handle_pdr_meeting(self, stdscr):
        """Handle Monday PDR (Production, Development, Resources) meeting"""
        height, width = stdscr.getmaxyx()
        
        # Clear screen for PDR interface
        stdscr.erase()
        
        # Header
        stdscr.addstr(2, width//2 - 10, "MONDAY PDR MEETING", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(3, 2, "=" * (width - 4), curses.color_pair(1))
        
        y = 5
        
        # Show each foreman's report
        for foreman_type, foreman in self.game_state['foremen'].items():
            # Foreman header
            stdscr.addstr(y, 4, f"{foreman['name']} - {foreman_type.title()} Foreman", 
                         curses.color_pair(1) | cursive.A_BOLD)
            y += 1
            
            # Show stats with rule of 3 sliders
            total = foreman['production'] + foreman['reliability'] + foreman['crew_moral']
            if total != 100:  # Balance if needed
                foreman['crew_moral'] = 100 - foreman['production'] - foreman['reliability']
            
        # Draw foreman skill bars
        self.draw_foreman_bar(stdscr, y, start_x + 8, "PROD", foreman['production'])
        self.draw_foreman_bar(stdscr, y + 1, start_x + 8, "RELY", foreman['reliability'])
        self.draw_foreman_bar(stdscr, y + 2, start_x + 8, "CREW", foreman['crew_moral'])
        
        y += 4
        
        # Foreman asks their question
        if foreman_type == 'development':
            question = "Which heading should we advance this week, boss?"
            options = ["Left drift", "Right drift", "Continue main drift"]
        elif foreman_type == 'production':
            question = "Which stopes should we muck out this week?"
            options = ["Lucky 7 (Grade: 0.15 oz/ton)", "Explore new area", "Focus on development"]
        else:  # maintenance
            question = "What's the maintenance scope for this week?"
            options = ["Planned maintenance on all equipment", "Basic PM/Oil changes", "Clean shop - reactive only"]
        
        stdscr.addstr(y, 6, question, curses.color_pair(4))
        y += 1
        
        # Show options (rule of 3!)
        for i, option in enumerate(options, 1):
            stdscr.addstr(y, 8, f"[{i}] {option}", curses.color_pair(4))
            y += 1
            
            # Show options (rule of 3!)
            for i, option in enumerate(options, 1):
                stdscr.addstr(y, 8, f"[{i}] {option}", curses.color_pair(4))
                y += 1
            
            y += 1
        
        # Show hire/fire options
        stdscr.addstr(y, 2, "HIRE/FIRE EMPLOYEES", curses.color_pair(1) | curses.A_BOLD)
        y += 2
        for foreman_type in ['development', 'production', 'maintenance']:
            foreman = self.game_state['foremen'][foreman_type]
            if foreman['grace_period'] == 0:
                stdscr.addstr(y, 4, f"[F] Fire {foreman['name']} ({foreman_type})", curses.color_pair(2))
            y += 1
        
        stdscr.addstr(y, 4, "[ENTER] Accept current crew", curses.color_pair(1))
        
        # Controls
        stdscr.addstr(height - 2, 2, "[1-3] Choose for each foreman  [F] Fire  [ENTER] Continue", 
                     curses.color_pair(4))
        
        stdscr.refresh()
        
        # Wait for player input - this is simplified for now
        # In full version, we'd handle individual foreman choices
        key = stdscr.getch()
        
        # For now, just accept current crew
        if key == ord('\n'):
            self.game_state['is_pdr_day'] = False
            
    def draw_foreman_bar(self, stdscr, y, start_x, label, value, color_pair=4):
        """Draw a single foreman skill bar"""
        stdscr.addstr(y, start_x, label, curses.color_pair(1))
        bar_length = 15
        filled = int((value / 100) * bar_length)
        empty = bar_length - filled
        bar = "█" * filled + "░" * empty
        stdscr.addstr(y, start_x + 6, f"[{bar}] {value}%", curses.color_pair(4))
        
    def resolve_daily_shift(self, stdscr):
        """Resolve a daily shift - generate events, update equipment, calculate production"""
        height, width = stdscr.getmaxyx()
        
        # Clear screen for shift resolution
        stdscr.erase()
        
        # Show slot machine style event reveal
        stdscr.addstr(height//2 - 2, width//2 - 10, "SPINNING THE REELS...", curses.color_pair(1) | curses.A_BOLD)
        
        # Generate 3 events (rule of 3!)
        events = self.generate_daily_events()
        
        # Show events with slot machine animation
        y = height//2
        symbols = ['[X]', '[💰]', '[⛏️]', '[☠️]', '[🔧]']
        
        for i, event in enumerate(events):
            # Animate the symbol reveal
            for _ in range(3):
                symbol = symbols[i % len(symbols)]
                stdscr.addstr(y + i, width//2 - 5, f"{symbol} {event['title']}", curses.color_pair(1))
                stdscr.refresh()
                # No sleep in terminal, just show final
            
            stdscr.addstr(y + i, width//2 - 5, f"{event['symbol']} {event['title']}", curses.color_pair(event['color']))
        
        stdscr.addstr(y + 4, width//2 - 15, "[Press any key to proceed with shift]", curses.color_pair(4))
        stdscr.refresh()
        stdscr.getch()
        
        # Process each event
        for event in events:
            self.process_event(event, stdscr)
        
        # Update equipment availability
        self.update_equipment_condition()
        
        # Calculate production
        daily_production = self.calculate_daily_production()
        
        # Update game state
        self.game_state['tons_surface'] += daily_production
        
    def generate_daily_events(self):
        """Generate 3 random daily events"""
        event_pool = [
            {
                'title': 'Hydraulic leak on LOA01',
                'type': 'equipment_failure',
                'symbol': '[🔧]',
                'color': 2,
                'equipment': 'LOA01'
            },
            {
                'title': 'Gold price up $15/oz',
                'type': 'price_change',
                'symbol': '[💰]',
                'color': 4,
                'change': 15
            },
            {
                'title': 'MSHA inspector spotted',
                'type': 'heat_increase',
                'symbol': '[☠️]',
                'color': 2,
                'heat_type': 'fed',
                'amount': 10
            },
            {
                'title': 'Crew morale boost',
                'type': 'crew_event',
                'symbol': '[⛏️]',
                'color': 1,
                'heat_type': 'crew',
                'amount': -5
            },
            {
                'title': 'Mob collections this week',
                'type': 'mob_pressure',
                'symbol': '[X]',
                'color': 2,
                'heat_type': 'mob',
                'amount': 5
            }
        ]
        
        # Randomly select 3 events based on current heat levels
        selected_events = []
        
        # Always include at least one equipment event if any equipment has <70% availability
        low_avail_equipment = [eq_id for eq_id, eq in self.game_state['equipment'].items() 
                              if eq['availability'] < 70]
        
        if low_avail_equipment and len(selected_events) < 3:
            # Add equipment failure event
            event = event_pool[0].copy()
            event['equipment'] = low_avail_equipment[0]
            selected_events.append(event)
        
        # Fill remaining slots with random events
        while len(selected_events) < 3:
            event = random.choice(event_pool)
            if event not in selected_events:
                selected_events.append(event)
        
        return selected_events
        
    def process_event(self, event, stdscr):
        """Process a single event and update game state"""
        if event['type'] == 'equipment_failure':
            equipment_id = event['equipment']
            if equipment_id in self.game_state['equipment']:
                self.game_state['equipment'][equipment_id]['status'] = 'down'
                self.game_state['equipment'][equipment_id]['availability'] -= 10
                
        elif event['type'] == 'heat_increase':
            self.game_state['heat_levels'][event['heat_type']] += event['amount']
            self.game_state['heat_levels'][event['heat_type']] = min(100, self.game_state['heat_levels'][event['heat_type']])
            
        elif event['type'] == 'crew_event':
            self.game_state['heat_levels']['crew'] += event['amount']
            self.game_state['heat_levels']['crew'] = max(0, self.game_state['heat_levels']['crew'])
            
        elif event['type'] == 'mob_pressure':
            self.game_state['heat_levels']['mob'] += event['amount']
            self.game_state['heat_levels']['mob'] = min(100, self.game_state['heat_levels']['mob'])
            
    def update_equipment_condition(self):
        """Update equipment availability based on age and condition"""
        for eq_id, equipment in self.game_state['equipment'].items():
            if equipment['status'] == 'down':
                continue
                
            # Equipment loses availability daily
            daily_loss = 1
            if equipment['availability'] < 50:
                daily_loss = 2  # Worn equipment degrades faster
                
            equipment['availability'] -= daily_loss
            equipment['availability'] = max(0, equipment['availability'])
            
            # Update equipment status
            if equipment['availability'] == 0:
                equipment['status'] = 'down'
            elif equipment['availability'] < 30:
                equipment['status'] = 'critical'
            elif equipment['availability'] < 60:
                equipment['status'] = 'poor'
            elif equipment['availability'] < 80:
                equipment['status'] = 'fair'
            else:
                equipment['status'] = 'good'
                
    def calculate_daily_production(self):
        """Calculate tons produced this shift"""
        total_tons = 0
        
        # Check active loaders
        for eq_id, equipment in self.game_state['equipment'].items():
            if equipment['type'] == 'loader' and equipment['status'] == 'manned':
                # Base production based on loader size and availability
                if equipment['size'] == 'small':
                    base_tons = 50
                elif equipment['size'] == 'medium':
                    base_tons = 100
                else:  # large
                    base_tons = 200
                    
                # Modify by availability
                tons = int(base_tons * (equipment['availability'] / 100))
                total_tons += tons
                
        return total_tons
        
    def update_day_of_week(self):
        """Update day of week and check for PDR day (Monday)"""
        self.game_state['day_of_week'] = (self.game_state['day_of_week'] % 7) + 1
        self.game_state['is_pdr_day'] = (self.game_state['day_of_week'] == 1)
            
    def show_splash_screen(self, stdscr):
        """Show splash screen before main game"""
        height, width = stdscr.getmaxyx()
        
        # Clear screen
        stdscr.erase()
        
        # Center the splash text
        title_y = height // 2 - 3
        title_x = width // 2 - 15
        
        stdscr.addstr(title_y, title_x, "MINING BY THE NUMBERS", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(title_y + 2, title_x, "A mining game by", curses.color_pair(4))
        stdscr.addstr(title_y + 3, title_x, "Shawn and his AI buddy Doug", curses.color_pair(1))
        
        stdscr.addstr(title_y + 5, title_x - 5, "[Press any key to continue]", curses.color_pair(4))
        
        stdscr.refresh()
        stdscr.getch()  # Wait for key press
        
    def main_loop(self, stdscr):
        """Main game loop"""
        curses.curs_set(0)  # Hide cursor
        self.init_colors(stdscr)
        
        # Show splash screen
        self.show_splash_screen(stdscr)
        
        # Set terminal title
        stdscr.erase()
        stdscr.refresh()
        
        running = True
        
        while running:
            stdscr.erase()
            
            # Draw all UI components
            self.draw_header(stdscr)
            self.draw_resources(stdscr)
            self.draw_mine_map(stdscr)
            self.draw_equipment(stdscr)
            self.draw_footer(stdscr)
            
            # Status line
            stdscr.addstr(0, 2, f"DAY {self.game_state['day']} - Mining By The Numbers", curses.color_pair(1))
            
            stdscr.refresh()
            
            # Handle input
            try:
                key = stdscr.getch()
                if not self.handle_input(stdscr, key):
                    running = False
            except KeyboardInterrupt:
                running = False
                
        # Save on exit
        self.save_game()
        
def main():
    """Entry point"""
    game = MiningGame()
    
    try:
        curses.wrapper(game.main_loop)
    except Exception as e:
        print(f"Error starting game: {e}")
        
if __name__ == "__main__":
    main()