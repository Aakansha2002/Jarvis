import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser
import urllib.parse
from openai import OpenAI


# ==========================================
# INITIALIZATION
# ==========================================

recognizer = sr.Recognizer()

engine = pyttsx3.init("nsss")
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

client = OpenAI()

conversation = []


# ==========================================
# SPEAK
# ==========================================

def speak(text):
    print("Jarvis:", text)

    try:
        engine.stop()
        engine.say(str(text))
        engine.runAndWait()

    except Exception as e:
        print("TTS Error:", e)


# ==========================================
# LISTEN
# ==========================================

def listen(source):

    print("Listening...")

    try:
        audio = recognizer.listen(
            source,
            timeout=3,
            phrase_time_limit=5
        )

    except sr.WaitTimeoutError:
        return None

    try:
        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text.lower().strip()

    except sr.UnknownValueError:
        return None

    except sr.RequestError:
        speak(
            "I am having trouble connecting "
            "to speech recognition."
        )
        return None


# ==========================================
# ASK OPENAI
# ==========================================

def ask_ai(question):

    global conversation

    conversation.append({
        "role": "user",
        "content": question
    })

    # Keep conversation from becoming too large
    if len(conversation) > 10:
        conversation = conversation[-10:]

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",

            instructions=(
                "You are Jarvis, a helpful voice assistant. "
                "Answer clearly and naturally. "
                "Keep answers concise because your responses "
                "will be spoken aloud."
            ),

            input=conversation
        )

        answer = response.output_text

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:

        print("OpenAI error:", e)

        return (
            "Sorry, I am having trouble "
            "connecting to my AI system."
        )


# ==========================================
# GOOGLE SEARCH
# ==========================================

def google_search(command):

    query = command.replace("search for", "")
    query = query.replace("search", "")
    query = query.replace("on google", "")
    query = query.replace("in google", "")
    query = query.strip()

    if query:

        speak("Searching for " + query)

        url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote(query)
        )

        webbrowser.open(url)

    else:

        speak("What should I search for?")


# ==========================================
# PROCESS COMMAND
# ==========================================

def process_command(command):

    # --------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------

    if "search" in command:

        google_search(command)


    # --------------------------------------
    # OPEN CHROME
    # --------------------------------------

    elif "open chrome" in command:

        speak("Opening Google Chrome.")

        subprocess.Popen(
            ["open", "-a", "Google Chrome"]
        )


    # --------------------------------------
    # OPEN SAFARI
    # --------------------------------------

    elif "open safari" in command:

        speak("Opening Safari.")

        subprocess.Popen(
            ["open", "-a", "Safari"]
        )


    # --------------------------------------
    # OPEN GOOGLE
    # --------------------------------------

    elif "open google" in command:

        speak("Opening Google.")

        webbrowser.open(
            "https://www.google.com"
        )


    # --------------------------------------
    # OPEN YOUTUBE
    # --------------------------------------

    elif "open youtube" in command:

        speak("Opening YouTube.")

        webbrowser.open(
            "https://www.youtube.com"
        )


    # --------------------------------------
    # HELLO
    # --------------------------------------

    elif (
        "hello" in command
        or "hi" in command
        or "hey" in command
    ):

        speak("Hello. How can I help you?")


    # --------------------------------------
    # WHO ARE YOU
    # --------------------------------------

    elif "who are you" in command:

        speak(
            "I am Jarvis, your voice assistant."
        )


    # --------------------------------------
    # EVERYTHING ELSE → OPENAI
    # --------------------------------------

    else:

        answer = ask_ai(command)

        speak(answer)


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    # --------------------------------------
    # MICROPHONE SETUP
    # --------------------------------------

    with sr.Microphone() as source:

        print("Calibrating microphone...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        print("Microphone ready.")

        speak(
            "Hello. I am Jarvis. "
            "Say Jarvis when you want to talk to me."
        )


        # ==================================
        # MAIN LOOP
        # ==================================

        while True:

            # ----------------------------------
            # WAIT FOR JARVIS
            # ----------------------------------

            command = listen(source)

            if command is None:
                continue


            # ----------------------------------
            # WAKE WORD
            # ----------------------------------

            if "jarvis" in command:

                speak("Yes, I am listening.")


                # ==================================
                # CONTINUOUS CONVERSATION
                # ==================================

                while True:

                    command = listen(source)

                    if command is None:
                        continue


                    # ----------------------------------
                    # EXIT PROGRAM COMPLETELY
                    # ----------------------------------

                    if (
                        command == "exit"
                        or command == "quit"
                        or command == "shutdown"
                    ):

                        speak("Goodbye.")

                        raise SystemExit


                    # ----------------------------------
                    # STOP CURRENT CONVERSATION
                    # ----------------------------------

                    if (
                        "stop listening" in command
                        or command == "stop"
                        or "goodbye" in command
                    ):

                        speak(
                            "Okay. I will wait for you "
                            "to say Jarvis again."
                        )

                        break


                    # ----------------------------------
                    # PROCESS COMMAND
                    # ----------------------------------

                    process_command(command)