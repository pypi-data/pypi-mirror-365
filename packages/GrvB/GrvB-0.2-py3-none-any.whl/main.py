import sys, os
sys.stderr = open(os.devnull, 'w')
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from os import getcwd 
import speech_recognition as sr
from mtranslate import translate
from colorama import Fore, init

init(autoreset=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
# chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
website = "https://jarvis-speech-to-text.netlify.app"
driver.get(website)

def listen():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 34000
    recognizer.dynamic_energy_adjustment_damping = 0.010 
    recognizer.dynamic_energy_ratio = 1.0
    recognizer.pause_threshold = 0.2
    recognizer.non_speaking_duration = 0.2

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        previous_result = None
        while True:
            try:
                print(Fore.GREEN + "I am listening... ", end="", flush=True)
                audio = recognizer.listen(source)
                print("\r" + Fore.LIGHTBLACK_EX + "Recognizing...", end="", flush=True)
                recognizer_text = recognizer.recognize_google(audio, language="hi-IN").lower()

                if recognizer_text and recognizer_text != previous_result:
                    trans_text = translate(recognizer_text, "en", "auto")
                    print("\r" + Fore.BLUE + "Grv.B : " + trans_text)
                    previous_result = recognizer_text
                    try:
                        output_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "output")))
                        driver.execute_script("arguments[0].textContent = arguments[1];", output_element, trans_text)
                    except Exception as e:
                        print(Fore.RED + f"[Browser update error]: {e}")
                elif recognizer_text == previous_result:
                    print("\r" + Fore.YELLOW + "Repeated input detected. Skipping output.")
                else:
                    print("\r" + Fore.YELLOW + "Didn't catch that.")
            except sr.UnknownValueError:
                print("\r" + Fore.RED + "Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("\r" + Fore.RED + f"Could not request results; {e}")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(Fore.RED + f"Unexpected error: {e}")
            print()  

if __name__ == "__main__":
    listen()