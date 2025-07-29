COLORS = {
    "info": "\033[34m",
    "error": "\033[31m",
    "warning": "\033[33m",
    "success": "\033[32m",
}
EMOJI = {"error": "🚫", "warning": "⚠️", "info": "ℹ️", "success": "✅"}
RESET_COLOR = "\033[0m"


def log(message, type="info"):
    color = COLORS.get(type, "\033[92m")
    emoji = EMOJI.get(type, "😒")
    print(color + emoji+" "+message + RESET_COLOR)
