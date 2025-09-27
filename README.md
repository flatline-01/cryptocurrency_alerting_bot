
---

Telegram bot for receiving notifications about cryptocurrency price changes. Uses the [BingX API](https://bingx-api.github.io/docs/#/en-us/swapV2/introduce) to obtain cryptocurrency price information. You can use the bot by following the [link](https://t.me/cryptocurrency_alerting_bot).

### Using Example

![[using_example.mp4]]

**Bot notification:**


### Getting started

1. Clone the project using this command.  

```bash
git clone https://github.com/I-am-Craz/weather_app.git`
```

2. Install the libraries.

```bash
pip install -r requirements.txt
```

3. Import postgres database.

```bash
psql -U username -h host -p port -W -f db_dump.sql
```

4. Create .env file in root project directory and specify these variables with your values:

```bash
API_KEY=...

API_SECRET=...

BOT_TOKEN=...

DB_NAME=...

DB_USER=...

DB_PASSWORD=...

DB_HOST=...
```

5. Start the bot.