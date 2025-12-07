"""
Weather Dashboard CLI - Main Entry Point

A command-line weather application that fetches current conditions and forecasts
using the OpenWeatherMap API.
"""

import argparse
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize colorama for Windows terminal colors
from colorama import init, Fore, Back, Style
init(autoreset=True)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.text import Text
from rich.style import Style as RichStyle

from utils import (
    get_current_weather,
    get_forecast,
    load_favorites,
    save_favorite,
    remove_favorite,
    format_temperature,
    get_weather_emoji,
)

console = Console()

# Weather-themed color styles
SUNNY_STYLE = "bold yellow"
RAINY_STYLE = "bold blue"
CLOUDY_STYLE = "dim white"
COLD_STYLE = "bold cyan"
HOT_STYLE = "bold red"


def get_temp_style(temp: float) -> str:
    """Get a color style based on temperature."""
    if temp <= 0:
        return COLD_STYLE
    elif temp <= 10:
        return "cyan"
    elif temp <= 20:
        return "green"
    elif temp <= 30:
        return "yellow"
    else:
        return HOT_STYLE


def show_welcome_banner():
    """Display a colorful welcome banner."""
    banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]☀️  [/bold yellow][bold white]W E A T H E R   D A S H B O A R D[/bold white][bold yellow]  🌧️[/bold yellow]   [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]  [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [italic]Your personal weather companion in the terminal[/italic]    [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/bold cyan]
"""
    console.print(banner)


def show_main_menu() -> str:
    """Display the main menu and get user choice."""
    console.print()
    console.print(Panel(
        "[bold yellow]☀️[/bold yellow] [bold cyan]Weather Dashboard[/bold cyan] [bold blue]🌧️[/bold blue]\n\n"
        "[bold white]What would you like to do?[/bold white]\n\n"
        "[bold green][1][/bold green] 🌡️  [white]Get current weather for a city[/white]\n"
        "[bold green][2][/bold green] 📅 [white]Get 5-day forecast for a city[/white]\n"
        "[bold green][3][/bold green] ⭐ [white]Manage favorite cities[/white]\n"
        "[bold green][4][/bold green] 🌍 [white]Get weather for all favorites[/white]\n"
        "[bold red][5][/bold red] ❌ [white]Exit[/white]\n",
        title="[bold yellow]☀️[/bold yellow] [bold white]Main Menu[/bold white] [bold blue]🌧️[/bold blue]",
        border_style="cyan",
        box=box.ROUNDED,
    ))
    
    choice = Prompt.ask(
        "[bold yellow]Enter your choice[/bold yellow]",
        choices=["1", "2", "3", "4", "5"],
        default="1"
    )
    return choice


def show_favorites_menu() -> str:
    """Display the favorites management menu."""
    console.print()
    console.print(Panel(
        "[bold magenta]⭐ Favorites Management[/bold magenta]\n\n"
        "[bold green][1][/bold green] 📋 [white]List all favorite cities[/white]\n"
        "[bold green][2][/bold green] ➕ [white]Add a city to favorites[/white]\n"
        "[bold green][3][/bold green] ➖ [white]Remove a city from favorites[/white]\n"
        "[bold yellow][4][/bold yellow] 🔙 [white]Back to main menu[/white]\n",
        title="[bold magenta]⭐[/bold magenta] [bold white]Favorites Menu[/bold white] [bold magenta]⭐[/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED,
    ))
    
    choice = Prompt.ask(
        "[bold yellow]Enter your choice[/bold yellow]",
        choices=["1", "2", "3", "4"],
        default="1"
    )
    return choice


def interactive_mode() -> int:
    """
    Run the CLI in interactive mode with prompts.
    
    Returns:
        Exit code (0 for success)
    """
    show_welcome_banner()
    
    while True:
        choice = show_main_menu()
        
        if choice == "1":
            # Get current weather
            city = Prompt.ask("\n[bold cyan]🏙️  Enter city name[/bold cyan]", default="London")
            console.print()
            display_current_weather(city)
            
            # Offer to save as favorite
            if Confirm.ask("\n[yellow]⭐ Add this city to favorites?[/yellow]", default=False):
                if save_favorite(city):
                    console.print(f"[bold green]✓[/bold green] Added '[cyan]{city}[/cyan]' to favorites!")
                else:
                    console.print(f"[yellow]'{city}' is already in favorites.[/yellow]")
        
        elif choice == "2":
            # Get forecast
            city = Prompt.ask("\n[bold green]Enter city name[/bold green]", default="London")
            console.print()
            display_forecast(city)
        
        elif choice == "3":
            # Favorites management submenu
            while True:
                fav_choice = show_favorites_menu()
                
                if fav_choice == "1":
                    console.print()
                    display_favorites()
                
                elif fav_choice == "2":
                    city = Prompt.ask("\n[bold cyan]🏙️  Enter city name to add[/bold cyan]")
                    if save_favorite(city):
                        console.print(f"[bold green]✓[/bold green] Added '[cyan]{city}[/cyan]' to favorites!")
                    else:
                        console.print(f"[yellow]⚠️  '{city}' is already in favorites.[/yellow]")
                
                elif fav_choice == "3":
                    favorites = load_favorites()
                    if not favorites:
                        console.print("[yellow]⚠️  No favorites to remove.[/yellow]")
                    else:
                        console.print("\n[bold magenta]⭐ Your favorites:[/bold magenta]")
                        for i, fav in enumerate(favorites, 1):
                            console.print(f"  [cyan]{i}.[/cyan] {fav}")
                        city = Prompt.ask("\n[bold red]🗑️  Enter city name to remove[/bold red]")
                        if remove_favorite(city):
                            console.print(f"[bold green]✓[/bold green] Removed '[cyan]{city}[/cyan]' from favorites.")
                        else:
                            console.print(f"[bold red]✗[/bold red] '{city}' was not in favorites.")
                
                elif fav_choice == "4":
                    break  # Back to main menu
        
        elif choice == "4":
            # Weather for all favorites
            console.print()
            weather_for_favorites()
        
        elif choice == "5":
            # Exit
            console.print("\n[bold cyan]☀️  Thanks for using Weather Dashboard! Stay dry! ☔[/bold cyan]")
            console.print("[dim]Clear skies ahead! 🌤️[/dim]\n")
            return 0
        
        # Pause before showing menu again
        console.print()
        input("Press Enter to continue...")
    
    return 0


def display_current_weather(city: str) -> bool:
    """
    Display current weather for a given city.
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        True if successful, False otherwise
    """
    weather_data = get_current_weather(city)
    
    if weather_data is None:
        console.print(f"[bold red]❌ Error:[/bold red] Could not fetch weather for '[cyan]{city}[/cyan]'")
        return False
    
    # Extract weather information
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    description = weather_data["weather"][0]["description"].title()
    wind_speed = weather_data["wind"]["speed"]
    city_name = weather_data["name"]
    country = weather_data["sys"]["country"]
    
    # Get weather emoji
    weather_id = weather_data["weather"][0]["id"]
    emoji = get_weather_emoji(weather_id)
    
    # Determine temperature color based on value (Fahrenheit thresholds)
    if temp >= 86:  # Hot (86°F+)
        temp_color = "bold red"
    elif temp >= 68:  # Warm (68°F+)
        temp_color = "bold yellow"
    elif temp >= 50:  # Mild (50°F+)
        temp_color = "bold green"
    else:  # Cold
        temp_color = "bold cyan"
    
    # Create a beautiful panel with weather info
    weather_info = f"""
{emoji} [bold cyan]{description}[/bold cyan]

🌡️  Temperature: [{temp_color}]{format_temperature(temp)}[/{temp_color}]
🤔 Feels Like:  [yellow]{format_temperature(feels_like)}[/yellow]
💧 Humidity:    [blue]{humidity}%[/blue]
💨 Wind Speed:  [green]{wind_speed} mph[/green]
"""
    
    panel = Panel(
        weather_info,
        title=f"[bold white]☀️ Weather in {city_name}, {country}[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
    )
    
    console.print(panel)
    return True


def display_forecast(city: str) -> bool:
    """
    Display 5-day weather forecast for a given city.
    
    Args:
        city: Name of the city to get forecast for
        
    Returns:
        True if successful, False otherwise
    """
    forecast_data = get_forecast(city)
    
    if forecast_data is None:
        console.print(f"[bold red]❌ Error:[/bold red] Could not fetch forecast for '[cyan]{city}[/cyan]'")
        return False
    
    city_name = forecast_data["city"]["name"]
    country = forecast_data["city"]["country"]
    
    # Create a table for the forecast
    table = Table(
        title=f"📅 5-Day Forecast for {city_name}, {country}",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold white",
        border_style="blue",
    )
    
    table.add_column("📆 Date/Time", style="white", header_style="bold white")
    table.add_column("🌡️ Temp", style="yellow", header_style="bold yellow")
    table.add_column("🤔 Feels Like", style="yellow", header_style="bold yellow")
    table.add_column("☁️ Conditions", style="cyan", header_style="bold cyan")
    table.add_column("💧 Humidity", style="blue", header_style="bold blue")
    table.add_column("💨 Wind", style="green", header_style="bold green")
    
    # Get forecast entries (every 8th entry for daily forecast, or show all for detailed)
    forecast_list = forecast_data["list"]
    
    # Show one entry per day (every 8 entries = 24 hours since data is 3-hourly)
    for i in range(0, min(40, len(forecast_list)), 8):
        entry = forecast_list[i]
        
        dt_txt = entry["dt_txt"]
        temp = format_temperature(entry["main"]["temp"])
        feels_like = format_temperature(entry["main"]["feels_like"])
        description = entry["weather"][0]["description"].title()
        humidity = f"{entry['main']['humidity']}%"
        wind = f"{entry['wind']['speed']} mph"
        
        weather_id = entry["weather"][0]["id"]
        emoji = get_weather_emoji(weather_id)
        
        table.add_row(dt_txt, temp, feels_like, f"{emoji} {description}", humidity, wind)
    
    console.print(table)
    return True


def display_favorites() -> None:
    """Display all saved favorite cities."""
    favorites = load_favorites()
    
    if not favorites:
        console.print("[yellow]⚠️  No favorite cities saved yet.[/yellow]")
        console.print("Use [cyan]--add-favorite <city>[/cyan] or [cyan]-a <city>[/cyan] to add one!")
        return
    
    table = Table(
        title="⭐ Favorite Cities",
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold white",
        border_style="magenta",
    )
    
    table.add_column("#", style="dim cyan")
    table.add_column("🏙️  City", style="bold white")
    
    for i, city in enumerate(favorites, 1):
        table.add_row(str(i), city)
    
    console.print(table)


def weather_for_favorites() -> None:
    """Display current weather for all favorite cities."""
    favorites = load_favorites()
    
    if not favorites:
        console.print("[yellow]⚠️  No favorite cities saved yet.[/yellow]")
        return
    
    console.print("[bold magenta]⭐ Weather for your favorite cities:[/bold magenta]\n")
    
    for city in favorites:
        display_current_weather(city)
        console.print()  # Add spacing between cities


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="weather",
        description="🌤️  Weather Dashboard CLI - Get weather information from your terminal!",
        epilog="""
Examples:
  weather.py London              Get weather for London
  weather.py London -f           Get 5-day forecast
  weather.py -a Paris            Add Paris to favorites
  weather.py -l                  List favorite cities
  weather.py -s                  Show weather for all favorites
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Positional argument for city (optional, makes it easy to just type city name)
    parser.add_argument(
        "city_name",
        nargs="?",
        type=str,
        help="City name (e.g., 'London' or 'Tokyo')",
    )
    
    # Weather lookup options
    parser.add_argument(
        "-c", "--city",
        type=str,
        help="City name to get weather for (e.g., 'London' or 'New York,US')",
    )
    
    parser.add_argument(
        "-f", "--forecast",
        action="store_true",
        help="Show 5-day forecast instead of current weather",
    )
    
    # Favorites management - with short aliases!
    parser.add_argument(
        "-s", "--favorites", "--show",
        action="store_true",
        dest="favorites",
        help="Show weather for all favorite cities",
    )
    
    parser.add_argument(
        "-l", "--list", "--list-favorites",
        action="store_true",
        dest="list_favorites",
        help="List all saved favorite cities",
    )
    
    parser.add_argument(
        "-a", "--add", "--add-favorite",
        type=str,
        metavar="CITY",
        dest="add_favorite",
        help="Add a city to favorites",
    )
    
    parser.add_argument(
        "-r", "--remove", "--remove-favorite",
        type=str,
        metavar="CITY",
        dest="remove_favorite",
        help="Remove a city from favorites",
    )
    
    return parser


def main() -> int:
    """
    Main entry point for the Weather Dashboard CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        return interactive_mode()
    
    # Handle favorites management
    if args.add_favorite:
        if save_favorite(args.add_favorite):
            console.print(f"[green]✓[/green] Added '{args.add_favorite}' to favorites!")
        else:
            console.print(f"[yellow]'{args.add_favorite}' is already in favorites.[/yellow]")
        return 0
    
    if args.remove_favorite:
        if remove_favorite(args.remove_favorite):
            console.print(f"[green]✓[/green] Removed '{args.remove_favorite}' from favorites.")
        else:
            console.print(f"[red]'{args.remove_favorite}' was not in favorites.[/red]")
        return 0
    
    if args.list_favorites:
        display_favorites()
        return 0
    
    if args.favorites:
        weather_for_favorites()
        return 0
    
    # Handle weather lookup - check both positional and -c flag
    city = args.city_name or args.city
    
    if city:
        if args.forecast:
            success = display_forecast(city)
        else:
            success = display_current_weather(city)
        return 0 if success else 1
    
    # If we got here, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
