# 🦇 Robin: The Ultimate Sidekick — AI Personal Assistant Protocol

Turn your AI (Gemini, Claude, or ChatGPT) into **Robin**, your tactical sidekick and operations manager. Instead of just giving passive advice, Robin actively manages your tasks, calendar, email, energy levels (via a **Story Point Load Meter**), and weekly reflections.

---

## ⚡ Features

- **Direct Action Over Advice**: Designed for AI assistants with tool/app integrations so tasks are actually checked off, events are scheduled, and drafts are prepared.
- **Dynamic Relationship & Habit Tracking**: Smart interval calculation that resets recurring check-ins based on when you *actually* spoke to someone, rather than rigid calendar dates.
- **The Load Meter (Story Points)**: Protects your schedule from burnout by calculating weekly capacity across meetings and tasks, complete with Green/Orange/Red thresholds.
- **Guided Weekly Review (`"weekly review"`)**: A structured Sunday evening protocol that evaluates your rest, personal time, upcoming bottlenecks, and free evenings.
- **Subtle Gotham Humor**: Clear, decisive, and practical support with occasional dry Batcave references—never getting in the way of actual productivity.

---

## 🔌 Supported Platforms & App Ecosystem

**Default Configuration:**  
Out of the box, this `SKILL.md` is configured for the **Google Workspace ecosystem** (**Google Tasks**, **Google Calendar**, **Gmail**, and **Google Docs/Keep**), making it ideal for **Google Gemini** (via Gemini Skills, Saved Info, or Gemini in Workspace).

**Using Todoist, Notion, Outlook, or Linear instead?**  
Because this protocol is modular, you can use it in **Claude** (via MCP connectors/Projects), **ChatGPT** (via Custom GPT Actions/Connectors), or any other AI agent that connects to your tools. See the section **"🔄 Switching to Todoist or Other Apps"** below for a 10-second AI prompt to convert this file to your stack.

---

## 🛠️ Step 1: How to Personalize Your Setup

Before activating Robin, customize the bracketed placeholders in `SKILL.md` to match your personal workflow:

| Placeholder | Description | Example |
| :--- | :--- | :--- |
| `[USER_NAME]` | Your name or hero alias | `Bruce` or `Alex` |
| `[PRIMARY_EMAIL]` | Your default email for sending new messages | `alex@domain.com` |
| `[SECONDARY_EMAIL]` | Secondary email address (optional) | `alex.old@gmail.com` |
| `[IGNORED_CALENDAR_ITEMS]` | Informational events that don't drain your energy | `"Partner's gym", "Kids school hours"` |
| `[MIN_FREE_EVENINGS]` | Minimum evenings (19:00–23:00) with zero plans | `3` |
| `[BENCHMARK_MAX_POINTS]` | Your historical "way too busy" week score | `38.5` |
| `[THRESHOLD_GREEN]` | Upper limit for a healthy, balanced week | `27` |
| `[THRESHOLD_RED]` | Point where your week is officially overloaded | `33` |

### 💡 How to find your Story Point Thresholds
Not sure what numbers to put for `[THRESHOLD_GREEN]` and `[THRESHOLD_RED]`? 
Start with the defaults (`27` for Green, `33` for Red). Use Robin for two weeks and run the `"weekly review"`. Once you experience a week that feels noticeably too hectic, ask Robin: *"Calculate my story points for this week."* Set that number as your `[BENCHMARK_MAX_POINTS]`, and set your Red threshold at **85–90%** of that score.

---

## 🔄 Step 2: Switching to Todoist or Other Apps (Optional)

If your AI has a connector/plugin for **Todoist**, **TickTick**, **Notion**, **Apple Reminders**, or **Outlook**, you don't need to rewrite `SKILL.md` manually. 

Just paste the contents of `SKILL.md` into your AI with this prompt:

> *"Rewrite this `SKILL.md` file so that instead of Google Tasks, it uses **Todoist** (including Todoist's native `every!` dynamic recurring syntax and task comments for logging weekly review scores). Keep all other sections, the Robin persona, the Load Meter, and the Weekly Review intact."*

*(Note: Todoist actually handles dynamic recurring intervals natively via `every! 2 weeks` and supports per-task comment threads, making it a great fit with Claude MCP or ChatGPT connectors!)*

---

## 🚀 Step 3: Installation

### Option A: Google Gemini (Main App — Skills / Saved Info)
1. Open Gemini and either create a new **Skill** (`robin-sidekick-assistant`) using `SKILL.md`, or paste the customized sections into **Settings > Saved Info**.
2. Make sure the **Google Workspace extension** is enabled in your Gemini settings.

### Option B: Gemini in Google Workspace (Gmail / Docs Side Panel)
If your Workspace instruction settings have a character limit (e.g., 1,024 characters per block), split the `Steps` in `SKILL.md` into 5 separate instruction blocks (1: Identity, 2: Apps & Gmail, 3: Tasks & Intervals, 4: Weekly Review, 5: Load Meter).

### Option C: Claude Projects / ChatGPT Custom Instructions
1. Create a new **Project** in Claude (or a Custom GPT in ChatGPT).
2. Connect your calendar, task manager, and email tools via integrations/MCP.
3. Paste the customized `SKILL.md` into the **Project Instructions**.

---

## 🎮 How to Use Robin (Daily Commands)

Once installed, you don't need complex prompts. Just talk to Robin like a real operations partner:

- **Log relationship check-ins & tasks:**  
  *"Hey Robin, I spoke to Sarah today."*  
  *(Robin finds the recurring "Sarah" task, checks the interval, and sets the next reminder starting from today's date).*
- **Schedule with Load Meter protection:**  
  *"Schedule a 2-hour strategy session with Harvey on Thursday afternoon."*  
  *(Robin checks your calendar availability, schedules the block, and immediately reports your updated weekly Story Points—warning you if you hit Orange or Red).*
- **Turn emails into tasks:**  
  *"Check my latest emails from Lucius and turn any action items into tasks for this week."*
- **Run your Sunday Weekly Review:**  
  Simply type: `weekly review`  
  *(Robin will walk you through your energy reflection questions one by one, calculate last week's and next week's load, check if you have enough free evenings, suggest what to drop or reschedule, and log your scores).*
