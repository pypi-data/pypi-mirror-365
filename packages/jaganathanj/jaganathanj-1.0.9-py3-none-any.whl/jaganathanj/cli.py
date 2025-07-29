# jaganathanj/cli.py

def main():
    import sys
    import jaganathanj

    if len(sys.argv) < 2:
        jaganathanj.help()
        return

    command = sys.argv[1].lower()

    match command:
        case "help":
            jaganathanj.help()
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
