# The Poster Agent

A "Computer Use" agent that watches WhatsApp, reads event posters, and manages my macOS Calendar.

## The Context

On my sabbatical in Paris. I spend a lot of time walking around, seeing cool posters for pop up events, concerts, etc.

The Problem: I take a photo, it gets lost in my camera roll, and I forget to go.
The Fix: I built an agent that lives on my Mac. I simply WhatsApp the photo to myself, and the agent handles the rest.

Wanted to play around multi-device agents, purposefully decided for "how human use devices” rather than simply using APIs.

## How It Works

It is a Computer Use agent that interacts with the OS UI like a human would.

Visual Trigger: Monitors WhatsApp Web for new images in my "Saved Messages".

Vision & Reasoning: Uses GPT-4o to analyze the poster (handling messy fonts,  text in different languages, and relative dates like "Next Sunday").

## OS Control:

Opens macOS Calendar via Spotlight.

Uses Natural Language Input to draft the event (visual verification).

Injects precise details via AppleScript to ensure database consistency.

Feedback Loop: Switches back to Chrome and sends me a confirmation message.

## Tech Stack

GPT-4o (Vision + JSON Mode)

Playwright (Browser Automation)

PyAutoGUI (Mouse/Keyboard Control) & AppleScript (OS Events)

## Getting Started

### Installation

Clone the repo:

git clone [https://github.com/felixlorenzen/poster-agent.git](https://github.com/felixlorenzen/poster-agent.git)
cd poster-agent


### Install dependencies:

pip install -r requirements.txt
playwright install chromium


### Set up your environment:

Export your OpenAI Key: export OPENAI_KEY='sk-...'

Optional: Update the WHATSAPP_CHAT_NAME in the script if you don't talk to yourself.

Usage

### Run the agent:

python3 poster_agent.py


First run requires scanning the WhatsApp QR code. The session is saved locally for future runs.

## Notes

The "QWERTZ" Fix: Direct keystroke injection often fails on non-US keyboard layouts (like my German Mac). I implemented a Clipboard Injection method (pbcopy) to ensure date/time formatting remains accurate regardless of system language.

“Smart” Dates: The agent calculates year logic dynamically. If a poster says "Oct 3" (and today is Nov), it automatically bumps the event to 2026.

Race Conditions: Uses atomic AppleScript properties to prevent the common "Start Date > End Date" crash when modifying events programmatically.

 ### License

MIT License
