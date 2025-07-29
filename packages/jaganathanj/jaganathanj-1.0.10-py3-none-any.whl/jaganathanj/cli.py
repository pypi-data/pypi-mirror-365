# jaganathanj/cli.py

def main():
    import sys
    import jaganathanj

    # Show welcome message for CLI usage
    if len(sys.argv) < 2:
        jaganathanj._welcome_message()
        jaganathanj.help()
        return

    command = sys.argv[1].lower()

    # Only show welcome for help command or invalid commands
    if command in ("help", "--help", "-h"):
        jaganathanj.help()
        return

    # For all other commands, execute directly without welcome message
    match command:
        case "about":
            jaganathanj.about()
        case "resume":
            jaganathanj.resume()
        case "cv":
            jaganathanj.cv()
        case "linkedin":
            jaganathanj.linkedin()
        case "contact":
            jaganathanj.contact()
        case "portfolio":
            jaganathanj.portfolio()
        case "youtube": 
            jaganathanj.youtube()
        case "github":
            jaganathanj.github()
        case _:
            print(f"Unknown command: {command}")
            jaganathanj.help()