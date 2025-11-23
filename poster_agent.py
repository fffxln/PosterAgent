import os
import time
import json
import base64
import subprocess
import pyautogui
from datetime import datetime, timedelta
from dateutil import parser
from openai import OpenAI
from playwright.sync_api import sync_playwright
from PIL import Image 

# --- CONFIGURATION ---
OPENAI_KEY = "YOUR KEY"
MODEL_ID = "gpt-4o" 
WHATSAPP_CHAT_NAME = "YOUR NAME (You)"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, "whatsapp_session_bot")
DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "downloads")

def encode_image(image_path):
    print("📉 Agent: Optimizing image...")
    output_path = image_path.replace(".png", "_optimized.jpg")
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img.thumbnail((1024, 1024)) 
        img.save(output_path, "JPEG", quality=85)
    with open(output_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def copy_to_mac_clipboard(text):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE
    )
    process.communicate(text.encode('utf-8'))

def open_app_visually(app_name):
    """
    Opens/Switches to an app using Spotlight (Cmd+Space).
    This creates the 'Human Agent' visual effect.
    """
    print(f"🖥️  Visual Agent: Switching context to {app_name}...")
    
    # 1. Click Menu Bar (Invisible) to ensure focus isn't stuck
    pyautogui.click(100, 10) 
    time.sleep(0.5)
    
    # 2. Spotlight
    pyautogui.hotkey('command', 'space')
    time.sleep(0.8) 
    
    # 3. Type App Name
    pyautogui.write(app_name, interval=0.05)
    time.sleep(0.3)
    pyautogui.press('enter')
    
    # 4. Wait for Window Animation
    time.sleep(2.0)

def analyze_poster_gpt4o(image_path):
    base64_image = encode_image(image_path)
    print(f"🧠 Brain ({MODEL_ID}): Analyzing visual data...")
    
    client = OpenAI(api_key=OPENAI_KEY)
    
    system_prompt = """
    You are an event extraction agent. Extract details from the poster.
    
    Return a JSON object with these EXACT keys:
    1. "title": Name of event
    2. "date_str": A clean date string (e.g. "2025-10-03")
    3. "time_str": A clean time string (e.g. "18:00")
    4. "location": The address
    5. "calendar_sentence": A natural string for Apple Calendar Quick Entry.
       Format: "[Title] at [Location] on [date_str] at [time_str]"
    
    IMPORTANT: If the date is in the past (e.g. 2023), bump it to the NEXT future occurrence.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            response_format={ "type": "json_object" }, 
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Extract details."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        print(f"🔹 Brain output: {content}")
        data = json.loads(content)
        
        # Fix Date Logic (Future Proofing)
        try:
            raw_d = data.get("date_str", "")
            raw_t = data.get("time_str", "")
            dt = parser.parse(f"{raw_d} {raw_t}")
            
            if dt < datetime.now():
                print("⚠️ Detected past date. Bumping year automatically.")
                dt = dt.replace(year=datetime.now().year + 1)
                
                # Update the data object with the fixed date
                data["date_str"] = dt.strftime("%Y-%m-%d")
                # Regenerate the calendar string with the new year
                data["calendar_sentence"] = f"{data['title']} at {data['location']} on {data['date_str']} at {data['time_str']}"
        except:
            pass

        return data

    except Exception as e:
        print(f"❌ GPT error: {e}")
        return None

def add_to_calendar_via_paste(natural_string):
    print("🗓️  Agent: Creating Calendar Event...")
    
    # VISUAL STEP 1: Open Calendar via Spotlight
    open_app_visually("Calendar")
    
    print("⌨️  Agent: Opening Quick Entry...")
    time.sleep(1)
    pyautogui.hotkey('command', 'n')
    time.sleep(1.5) 
    
    print(f"📋 Agent: Pasting details...")
    copy_to_mac_clipboard(natural_string)
    time.sleep(0.5)
    pyautogui.hotkey('command', 'v')
    
    time.sleep(2.5) 
    print("✅ Agent: Saving Event...")
    pyautogui.press('enter') 
    time.sleep(2.0) 

def send_whatsapp_confirmation(page, data):
    print("💬 Agent: Sending confirmation...")
    
    # VISUAL STEP 2: Open Chrome via Spotlight (The Request)
    open_app_visually("Google Chrome")
    
    print("⌨️  Agent: Typing confirmation message...")
    try:
        # Target the input box
        msg_box = page.locator('footer div[contenteditable="true"]')
        msg_box.click()
        
        # Construct the message
        message = f"✅ *Event Created*\n\n📅 {data['title']}\n📍 {data['location']}\n⏰ {data['date_str']} @ {data['time_str']}"
        
        # Type and Send
        msg_box.fill(message)
        time.sleep(1.0) 
        msg_box.press("Enter")
        print("✅ Confirmation sent")
        
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    with sync_playwright() as p:
        print("🚀 Agent: Launching Browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="chrome",
            args=["--start-maximized"]
        )
        
        page = context.pages[0]
        page.goto("https://web.whatsapp.com")
        
        try:
            page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
            print("✅ WhatsApp loaded")
        except:
            print("⚠️ Waiting for login... (Scan QR if needed)")
            time.sleep(30)
            
        print(f"🔍 Agent: Searching for '{WHATSAPP_CHAT_NAME}'...")
        search_box = page.locator('div[contenteditable="true"]').first
        search_box.click()
        page.keyboard.type(WHATSAPP_CHAT_NAME)
        time.sleep(1.5)
        page.keyboard.press("Enter")
        
        print("📸 Agent: Looking for poster...")
        time.sleep(2) 

        main_chat = page.locator("#main")
        candidate_images = main_chat.locator("div[role='button'] img")
        
        count = candidate_images.count()
        if count > 0:
            last_img = candidate_images.nth(count - 1)
            last_img.highlight()
            time.sleep(0.5)
            
            print("👆 Clicking Image...")
            last_img.click()
            
            print("⏳ Capturing full screen...")
            time.sleep(2) 
            screenshot_path = os.path.join(DOWNLOAD_DIR, "poster_scan.png")
            page.screenshot(path=screenshot_path)
            print("✅ Captured.")
            
            page.keyboard.press("Escape")
            
            # --- 1. BRAIN ---
            event_data = analyze_poster_gpt4o(screenshot_path)
            
            if event_data:
                # --- 2. CALENDAR ACTION (Visual Switch) ---
                add_to_calendar_via_paste(event_data["calendar_sentence"])
                
                # --- 3. WHATSAPP CONFIRMATION (Visual Switch Back) ---
                send_whatsapp_confirmation(page, event_data)
                
            else:
                print("❌ Could not read the poster.")
        else:
            print("❌ No images found in chat.")
            
        print("🏁 Mission Complete. Closing in 5s.")
        time.sleep(5)
        context.close()

if __name__ == "__main__":
    main()
