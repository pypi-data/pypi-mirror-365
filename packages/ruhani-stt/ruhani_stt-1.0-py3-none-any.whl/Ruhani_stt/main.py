from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# Setup paths
cwd = os.getcwd()
html_path = os.path.join(cwd, "index.html")
rec_file = os.path.join(cwd, "input.txt")

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")  # Headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")  # Silent console
chrome_options.add_argument("--window-size=1200,800")

# Launch browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("file://" + html_path)

def listen():
    print("🔊 Ruhani is Listening...")
    try:
        # Wait for button and click it
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "listenButton"))
        )
        start_button.click()

        last_text = ""

        while True:
            try:
                # Wait for new speech result
                output_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "output"))
                )
                current_text = output_element.text.strip()

                if current_text != last_text and "🤍 Ruhani heard you:" in current_text:
                    cleaned = current_text.replace("🤍 Ruhani heard you:", "").strip()
                    last_text = current_text

                    # Save to file
                    with open(rec_file, "w", encoding="utf-8") as f:
                        f.write(cleaned.lower())

                    print("🤍 Ruhani heard you, Farhan Raza:", cleaned)

                time.sleep(1)

            except Exception as loop_error:
                print("⚠️ Error in loop:", loop_error)
                break

    except KeyboardInterrupt:
        print("\n👋 Ruhani stopped listening. Allah Hafiz!")
    finally:
        driver.quit()

if __name__ == "__main__":
    listen()
