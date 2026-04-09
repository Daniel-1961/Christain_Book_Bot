# Christian Book Bot

![Python](https://img.shields.io/badge/language-python-blue)
![Deployed](https://img.shields.io/badge/deployed-PythonAnywhere-orange)
![Status](https://img.shields.io/badge/status-24/7-green)

## Overview

Christian Book Bot ([Telegram: @ChristianBooksHelperBot](https://t.me/ChristianBooksHelperBot)) is an intelligent chatbot designed to help users discover, explore, and learn more about Christian books—now supporting both **Amharic** and **English** titles. The bot provides personalized recommendations, detailed summaries, and additional resources for readers of all backgrounds and interests.

## Features
- Book recommendations based on user interests
- Summaries and key takeaways for a wide range of Christian literature
- Author and publication information
- Search functionality for books by title, author, or topic
- Supports both **Amharic and English books**
- Instant Telegram integration via [@ChristianBooksHelperBot](https://t.me/ChristianBooksHelperBot)
- Runs reliably 24/7 on [PythonAnywhere](https://www.pythonanywhere.com/)
- Webhook architecture for fast, scalable response (transitioned from polling)
- User-friendly and extensible codebase

## Future Feature Under Development
- Book recommendations based on user interests
- Summaries and key takeaways for a wide range of Christian literature
- Author and publication information

## Screenshots
<img width="1210" height="465" alt="Screenshot 2026-03-27 151632" src="https://github.com/user-attachments/assets/d64fb201-0869-4f30-803d-34b226c5bd73" />

<!-- ![screenshot](./screenshots/example.png) -->

## Getting Started

### Prerequisites

- Python 3.7 or higher
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package manager)
- [PythonAnywhere](https://www.pythonanywhere.com/) account (for deployment, optional)

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Daniel-1961/Christain_Book_Bot.git
    cd Christain_Book_Bot
    ```
2. **(Optional) Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

- Set your environment variables and API keys as needed (see `.env.example` if available).
- Set up your Telegram Bot by talking to [@BotFather](https://t.me/BotFather) and obtaining a bot token.
- Configure your webhook URL in Telegram to point to your [PythonAnywhere](https://www.pythonanywhere.com/) deployment or chosen production endpoint.

### Usage

To start the bot locally, run:

```bash
python main.py
```

For deployment, set the webhook in Telegram and ensure your web endpoint is live on PythonAnywhere.

### Project Structure

```
Christain_Book_Bot/
├── main.py
├── requirements.txt
├── README.md
├── ...
```
_Add explanations for important files and directories as needed._

## Architecture

- Uses a **webhook-based** architecture for real-time, efficient updates (no more polling).
- Designed for fast responses and scalable operation on PythonAnywhere.
- 24/7 reliability for uninterrupted user experience.

## Contributing

Contributions welcome! To get started:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request


## Contact

For questions, suggestions, or feedback, please [open an issue](https://github.com/Daniel-1961/Christain_Book_Bot/issues) or contact [@Daniel-1961](https://github.com/Daniel-1961).

---

_Christian Book Bot — Empowering readers in Amharic and English, 24/7._
