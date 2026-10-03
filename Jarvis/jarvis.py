import datetime
import os
import random
import sys
import webbrowser as wb

import pyautogui
import pyjokes
import pyttsx3
import speech_recognition as sr
import wikipedia


_engine = None


def speak(audio):
    """Speak a message, creating the speech engine only when it is needed."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        voices = _engine.getProperty("voices")
        if len(voices) > 1:
            _engine.setProperty("voice", voices[1].id)
        _engine.setProperty("rate", 150)
        _engine.setProperty("volume", 1)
    _engine.say(audio)
    _engine.runAndWait()


def _announce(message):
    speak(message)
    print(message)


def time():
    """Tell the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    message = "The current time is " + current_time
    _announce(message)
    return message


def date():
    """Tell the current date."""
    now = datetime.datetime.now()
    message = "The current date is {0} {1} {2}".format(
        now.day, now.strftime("%B"), now.year
    )
    _announce(message)
    return message


def wishme():
    """Greet the user based on the time of day."""
    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        greeting = "Good morning!"
    elif 12 <= hour < 16:
        greeting = "Good afternoon!"
    elif 16 <= hour < 24:
        greeting = "Good evening!"
    else:
        greeting = "Good night, see you tomorrow."

    message = "Welcome back, sir! {0} {1} at your service.".format(
        greeting, load_name()
    )
    _announce(message)
    return message


def screenshot():
    """Take a screenshot and save it in the user's Pictures directory."""
    img = pyautogui.screenshot()
    img_path = os.path.expanduser("~\\Pictures\\screenshot.png")
    img.save(img_path)
    message = "Screenshot saved as {0}.".format(img_path)
    _announce(message)
    return message


def takecommand(status_callback=None):
    """Listen for a voice command and return the recognized text."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            if status_callback:
                status_callback("Listening...")
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source, timeout=5)
    except sr.WaitTimeoutError:
        _announce("I didn't hear anything. Please try again.")
        return None
    except (OSError, AttributeError) as error:
        message = "The microphone is unavailable: {0}".format(error)
        print(message)
        _announce("The microphone is unavailable.")
        return None

    try:
        if status_callback:
            status_callback("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-in")
        print(query)
        return query.lower()
    except sr.UnknownValueError:
        _announce("Sorry, I did not understand that.")
    except sr.RequestError as error:
        print("Speech recognition service error: {0}".format(error))
        _announce("Speech recognition service is unavailable.")
    return None


def play_music(song_name=None):
    """Play a matching song from the user's Music directory."""
    song_dir = os.path.expanduser("~\\Music")
    try:
        songs = os.listdir(song_dir)
    except OSError as error:
        message = "I couldn't access your Music folder: {0}".format(error)
        print(message)
        _announce("I couldn't access your Music folder.")
        return message

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if not songs:
        message = "No matching song was found in your Music folder."
        _announce(message)
        return message

    song = random.choice(songs)
    try:
        os.startfile(os.path.join(song_dir, song))
    except (AttributeError, OSError) as error:
        message = "I couldn't open {0}: {1}".format(song, error)
        print(message)
        _announce("I couldn't open that song.")
        return message
    message = "Playing {0}.".format(song)
    _announce(message)
    return message


def set_assistant_name(name):
    """Save a new assistant name."""
    name = name.strip()
    if not name:
        return "Please enter a name before saving."
    with open("assistant_name.txt", "w", encoding="utf-8") as name_file:
        name_file.write(name)
    message = "Alright, I will be called {0} from now on.".format(name)
    _announce(message)
    return message


def set_name():
    """Change the assistant's name using voice input."""
    _announce("What would you like to name me?")
    name = takecommand()
    if name:
        set_assistant_name(name)
    else:
        _announce("Sorry, I couldn't catch that.")


def load_name():
    """Load the saved assistant name, or use the default."""
    try:
        with open("assistant_name.txt", "r", encoding="utf-8") as name_file:
            name = name_file.read().strip()
            return name or "Jarvis"
    except FileNotFoundError:
        return "Jarvis"


def search_wikipedia(query):
    """Search Wikipedia and return a short summary."""
    try:
        result = wikipedia.summary(query, sentences=2)
        _announce(result)
        return result
    except wikipedia.exceptions.DisambiguationError:
        message = "I found multiple results. Please be more specific."
    except wikipedia.exceptions.PageError:
        message = "I couldn't find a Wikipedia page for that topic."
    except Exception as error:
        message = "Wikipedia search failed: {0}".format(error)
        print(message)
        _announce("I couldn't complete that Wikipedia search.")
        return message
    _announce(message)
    return message


def handle_command(query):
    """Run one command and return its reply and whether the assistant stays online."""
    original_query = query.strip()
    query = original_query.lower()
    if not query:
        return "Type or say a command to get started.", True

    if "time" in query:
        return time(), True
    if "date" in query:
        return date(), True
    if "wikipedia" in query:
        position = query.index("wikipedia") + len("wikipedia")
        topic = original_query[position:].strip().lstrip(" :,-")
        if topic.lower().startswith("for "):
            topic = topic[4:].strip()
        elif topic.lower().startswith("about "):
            topic = topic[6:].strip()
        if not topic:
            message = "Tell me what you would like to look up on Wikipedia."
            _announce(message)
            return message, True
        return search_wikipedia(topic), True
    if "play music" in query:
        song_name = query.replace("play music", "", 1).strip()
        return play_music(song_name or None), True
    if "open youtube" in query:
        wb.open("https://www.youtube.com")
        message = "Opening YouTube."
        _announce(message)
        return message, True
    if "open google" in query:
        wb.open("https://www.google.com")
        message = "Opening Google."
        _announce(message)
        return message, True
    if "change your name" in query:
        position = query.index("change your name") + len("change your name")
        requested_name = original_query[position:].strip()
        if requested_name.lower().startswith("to "):
            requested_name = requested_name[3:].strip()
        if requested_name:
            return set_assistant_name(requested_name), True
        set_name()
        return "Your assistant name has been updated.", True
    if "screenshot" in query:
        return screenshot(), True
    if "tell me a joke" in query or "joke" in query:
        joke = pyjokes.get_joke()
        _announce(joke)
        return joke, True
    if "shutdown" in query:
        message = "Shutting down the system."
        _announce(message)
        os.system("shutdown /s /f /t 1")
        return message, False
    if "restart" in query:
        message = "Restarting the system."
        _announce(message)
        os.system("shutdown /r /f /t 1")
        return message, False
    if "offline" in query or "exit" in query:
        message = "Going offline. Have a good day!"
        _announce(message)
        return message, False

    message = "I don't know how to help with that yet. Try one of the quick actions."
    _announce(message)
    return message, True


def run_cli():
    """Run the original command-line voice assistant."""
    wishme()
    while True:
        query = takecommand()
        if not query:
            continue
        _, keep_running = handle_command(query)
        if not keep_running:
            break


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        try:
            from gui import launch_gui
        except ImportError:
            from Jarvis.gui import launch_gui
        launch_gui()
