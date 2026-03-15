# Mining By The Numbers

Terminal-based roguelike mining management simulator set in 1970s Nevada. Manage an underground gold mine with mob debt, federal heat, and equipment that breaks down more often than your crew.

![Build Status](https://github.com/shawn/mining-by-the-numbers/workflows/Build%20and%20Test/badge.svg)

## Quick Start

```bash
git clone https://github.com/shawn/mining-by-the-numbers.git
cd mining-by-the-numbers
python3 main.py
```

## Status

**Phase 1**: Core engine development - UI framework complete, implementing core mechanics

## Features (In Development)
- ASCII terminal interface with authentic 1970s amber color scheme
- Heat management: Mob, Federal, and Crew pressure systems
- Equipment management with realistic breakdown mechanics
- PDR meetings with unique foreman personalities
- Roguelike progression with permanent consequences
- IBM terminal-style interface perfect for Steam Deck

## Requirements
- Python 3.7+
- Linux/macOS/Windows terminal with color support

## Screenshot
```
DAY 1 - Mining By The Numbers

MOB    [███░░░░░░░░░░░░░░░░░] 25%
FED    [█░░░░░░░░░░░░░░░░░░░] 10%
CREW   [██░░░░░░░░░░░░░░░░░░] 15%

TEMP    [██░░░░░░░░░░░░░░░░░░] 20%
GROUND  [█░░░░░░░░░░░░░░░░░░░] 15%
VENT    [█░░░░░░░░░░░░░░░░░░░] 10%

CASH: $50,000  MOB DEBT: $200,000  SURFACE TONS: 0

SURFACE    ▓▓▓▓▓▓▓▓▓▓▓ HEADFRAME ▓▓▓▓▓▓▓▓▓▓▓
           ║║
LEVEL 1000 ║║██████████████████████████████
           ║║    ├─ LUCKY 7 [X] (Active)
           ║║    └─ MAIN DRIFT ───►

EQUIPMENT STATUS
────────────────────
LOA01 [████░░░░] 60% Manned
HTK01 [███████░] 75% Manned
DRL01 [███░░░░░] 55% Manned
```

## Development Roadmap
- [x] Terminal UI framework
- [ ] Core game mechanics
- [ ] PDR meeting system
- [ ] Equipment breakdown system
- [ ] Event card system
- [ ] Content generation (via AI)
- [ ] Balance testing (via AI simulation)

## License
MIT License - See LICENSE file for details