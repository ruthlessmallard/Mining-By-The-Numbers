#!/usr/bin/env python3
"""
Test mode for Mining By The Numbers - runs without curses/terminal UI
"""

import sys
import os
sys.path.append('/home/ruthless/.openclaw/workspace/mining_by_numbers')

from mining_by_numbers.game import MiningGame

def test_game_loop():
    """Test the game mechanics without terminal UI"""
    print("=== MINING BY THE NUMBERS - TEST MODE ===")
    print("A mining game by Shawn and his AI buddy Doug")
    print()
    
    game = MiningGame()
    
    print("Initial State:")
    print(f"Day: {game.game_state['day']}")
    print(f"Cash: ${game.game_state['cash']:,}")
    print(f"Mob Debt: ${game.game_state['mob_debt']:,}")
    print(f"Day of Week: {game.game_state['day_of_week']} (1=Monday)")
    print(f"Is PDR Day: {game.game_state['is_pdr_day']}")
    print()
    
    print("Heat Levels:")
    for heat_type, value in game.game_state['heat_levels'].items():
        print(f"  {heat_type.upper()}: {value}%")
    print()
    
    print("Foremen:")
    for foreman_type, foreman in game.game_state['foremen'].items():
        print(f"  {foreman['name']} ({foreman_type})")
        print(f"    PROD: {foreman['production']} | RELY: {foreman['reliability']} | CREW: {foreman['crew_moral']}")
        if 'secret_traits' in foreman:
            print(f"    Traits: {', '.join(foreman['secret_traits'])}")
    print()
    
    print("Equipment:")
    for eq_id, equipment in game.game_state['equipment'].items():
        print(f"  {eq_id}: {equipment['type']} ({equipment['size']}) - {equipment['availability']}% - {equipment['status']}")
    print()
    
    print("Mine Map:")
    for level, data in game.game_state['mine_map']['levels'].items():
        print(f"  Level {level}: {'Developed' if data['developed'] else 'Undeveloped'}")
        if data['stopes']:
            for stope_name, stope_data in data['stopes'].items():
                print(f"    {stope_name.title()}: {stope_data['status']} - {stope_data['tons_remaining']} tons remaining")
    print()
    
    # Test daily events
    print("Testing daily event generation...")
    events = game.generate_daily_events()
    print(f"Generated {len(events)} events:")
    for i, event in enumerate(events, 1):
        print(f"  {i}. {event['symbol']} {event['title']} ({event['type']})")
    print()
    
    # Test equipment degradation
    print("Testing equipment condition update...")
    print("Before update:")
    for eq_id, equipment in game.game_state['equipment'].items():
        print(f"  {eq_id}: {equipment['availability']}% availability")
    
    game.update_equipment_condition()
    
    print("After update:")
    for eq_id, equipment in game.game_state['equipment'].items():
        print(f"  {eq_id}: {equipment['availability']}% availability - {equipment['status']}")
    print()
    
    # Test production calculation
    print("Testing daily production calculation...")
    daily_tons = game.calculate_daily_production()
    print(f"Daily production: {daily_tons} tons")
    
    # Test week progression
    print("\nTesting week progression...")
    for day in range(1, 15):
        print(f"\nDay {day} (Day of week: {game.game_state['day_of_week']}) - PDR: {game.game_state['is_pdr_day']}")
        game.update_day_of_week()
        game.game_state['day'] += 1

if __name__ == "__main__":
    test_game_loop()