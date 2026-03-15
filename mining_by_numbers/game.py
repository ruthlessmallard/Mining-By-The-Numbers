#!/usr/bin/env python3
"""
Mining By The Numbers - Terminal UI Framework
ASCII-based mine management simulator set in 1970s Nevada
"""

import curses
import json
import os
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
            'current_level': 1000
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
            
    def handle_input(self, stdscr, key):
        """Handle user input"""
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('s') or key == ord('S'):
            # Start shift - placeholder
            self.game_state['day'] += 1
            stdscr.addstr(0, 0, "Starting shift... (placeholder)", curses.color_pair(1))
        elif key == ord('m') or key == ord('M'):
            # Focus mine map - placeholder
            pass
        elif key == ord('e') or key == ord('E'):
            # Equipment management - placeholder
            pass
        elif key == ord('p') or key == ord('P'):
            # PDR Meeting - placeholder
            pass
        return True
            
    def main_loop(self, stdscr):
        """Main game loop"""
        curses.curs_set(0)  # Hide cursor
        self.init_colors(stdscr)
        
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