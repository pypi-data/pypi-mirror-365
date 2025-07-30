"""
UI command implementation for claude-mpm.

WHY: This module provides terminal UI functionality for users who prefer a
visual interface over command-line interaction.
"""

from claude_mpm.utils.imports import safe_import

# Import logger using safe_import pattern
get_logger = safe_import('claude_mpm.core.logger', None, ['get_logger'])


def run_terminal_ui(args):
    """
    Run the terminal UI.
    
    WHY: Some users prefer a visual interface with multiple panes showing different
    aspects of the system. This command launches either a rich terminal UI or a
    basic curses UI depending on availability and user preference.
    
    DESIGN DECISION: We try the rich UI first as it provides a better experience,
    but fall back to curses if rich is not available. This ensures the UI works
    on all systems.
    
    Args:
        args: Parsed command line arguments with optional 'mode' attribute
    """
    logger = get_logger("cli")
    
    ui_mode = getattr(args, 'mode', 'terminal')
    
    try:
        if ui_mode == 'terminal':
            # Try rich UI first using safe_import
            run_rich_ui = safe_import(
                '...ui.rich_terminal_ui',
                'claude_mpm.ui.rich_terminal_ui',
                ['main']
            )
            
            if run_rich_ui:
                logger.info("Starting rich terminal UI...")
                run_rich_ui()
            else:
                # Fallback to curses UI
                logger.info("Rich not available, falling back to curses UI...")
                TerminalUI = safe_import(
                    '...ui.terminal_ui',
                    'claude_mpm.ui.terminal_ui',
                    ['TerminalUI']
                )
                if TerminalUI:
                    ui = TerminalUI()
                    ui.run()
                else:
                    logger.error("UI module not found")
                    print("Error: Terminal UI requires 'curses' (built-in) or 'rich' (pip install rich)")
                    return 1
        else:
            # Use curses UI explicitly
            TerminalUI = safe_import(
                '...ui.terminal_ui',
                'claude_mpm.ui.terminal_ui',
                ['TerminalUI']
            )
            if TerminalUI:
                ui = TerminalUI()
                ui.run()
            else:
                logger.error("UI module not found")
                print("Error: Terminal UI not available")
                return 1
    except Exception as e:
        logger.error(f"Error running terminal UI: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0