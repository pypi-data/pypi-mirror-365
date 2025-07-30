import time
import sys
import ctypes
import colorama
from colorama import Fore, Back, Style
import pystyle
from datetime import datetime
import os
import platform

# Initialize colorama
colorama.init(autoreset=True)

class BeamLogger:
    # ANSI color codes for different log levels with bright colors
    COLORS = {
        "info": Fore.CYAN + Style.BRIGHT,
        "debug": Fore.BLUE + Style.BRIGHT,
        "log": Fore.WHITE + Style.BRIGHT,  # Changed from green to white
        "success": Fore.GREEN + Style.BRIGHT,  # Only success remains green
        "input": Fore.MAGENTA + Style.BRIGHT,
        "output": Fore.WHITE + Style.BRIGHT,
        "error": Fore.RED + Style.BRIGHT,
        "critical": Fore.RED + Style.BRIGHT,
        "warn": Fore.YELLOW + Style.BRIGHT,
        "timestamp": Fore.LIGHTMAGENTA_EX + Style.BRIGHT  # Changed to a more unique color
    }
    
    # Symbol colors
    SYMBOL_COLOR = Fore.CYAN + Style.BRIGHT
    
    def __init__(self):
        """
        Initialize the BeamLogger
        """
        pass
    
    def clear_console(self):
        """
        Clear the console screen
        """
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Unix/Linux/MacOS
        else:
            os.system('clear')
    
    def _get_timestamp(self):
        """
        Get the current time in 12-hour format
        
        Returns:
            str: Formatted timestamp string
        """
        return datetime.now().strftime("%I:%M:%S %p")
    
    def _log(self, level, message):
        """
        Internal logging method
        
        Args:
            level (str): The log level
            message (str): The message to log
        """
        timestamp = self._get_timestamp()
        color = self.COLORS.get(level.lower(), Fore.WHITE + Style.BRIGHT)
        timestamp_color = self.COLORS.get("timestamp")
        
        # Format: [Time stamp in 12hrs] ❆ [Prefix] ➔ TEXT
        # Now with colored timestamp
        formatted_message = f"{timestamp_color}[{timestamp}] {self.SYMBOL_COLOR}❆ {color}[{level.upper()}] {self.SYMBOL_COLOR}➔ {color}{message}"
        print(formatted_message)
    
    def info(self, message):
        """Log an info message"""
        self._log("info", message)
    
    def debug(self, message):
        """Log a debug message"""
        self._log("debug", message)
    
    def log(self, message):
        """Log a regular message"""
        self._log("log", message)
    
    def success(self, message):
        """Log a success message"""
        self._log("success", message)
    
    def input(self, message, prompt=""):
        """
        Get input from the user with styled prompt
        
        Args:
            message (str): The message to display
            prompt (str): The input prompt
            
        Returns:
            str: User input
        """
        self._log("input", message)
        # Updated input style with a more distinctive prompt
        result = input(f"{self.COLORS.get('input')}                ❯❯ {prompt} {Fore.WHITE + Style.BRIGHT}")
        return result
    
    def output(self, message):
        """Log an output message"""
        self._log("output", message)
    
    def error(self, message):
        """Log an error message"""
        self._log("error", message)
    
    def critical(self, message):
        """Log a critical message"""
        self._log("critical", message)
    
    def warn(self, message):
        """Log a warning message"""
        self._log("warn", message)
    
    def banner(self, text, color=pystyle.Colors.blue_to_cyan, spacing=15):
        """
        Display a styled banner using pystyle
        
        Args:
            text (str): The banner text (ASCII art)
            color: The color gradient to use
            spacing (int): Number of spaces for centering
        """
        styled_banner = pystyle.Center.XCenter(pystyle.Colorate.Vertical(text=text, color=color), spaces=spacing)
        print(styled_banner)
        print()  # Add an empty line after the banner

# Crafted With <3 By Bhaskar