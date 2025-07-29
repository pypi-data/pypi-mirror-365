import pyttsx3

class dropcheck:

    class check:

        def string(command: str, checker: str, out: str):
            key_input = input(command)

            if checker == key_input:
                return out

        def boolean(command: str, checker: str):
            key_input = input(command)

            if checker == key_input:
                return True

        def integer(command: str, checker: str, out: int):
            key_input = input(command)

            if checker == key_input:
                return str(out)
            
class speaker:

    def scream(text):
        return text + "!"
    
    def think(text):
        return text + "..."
    
    def say(text):
        return text + "."
    
    def author(author, text):
        return author + ": " + text

class ai:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    def speak(text):
        engine = pyttsx3.init()

        engine.say(text)
        engine.runAndWait()
