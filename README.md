<p align="center">
  <a href="https://discord.gg/b6zyJyCQUu">
    <img src="https://cdn.discordapp.com/attachments/955216634522525746/1099813661943550002/logo-modified.png" alt="Logo" width="auto" height="256">
  </a>
  
  <h3 align="center">Sole Retriever Raffle Monitor</h3>

  <p align="center">
    A Web Monitor that Notifies you through Discord Webhook when a New Raffle is Added to Sole Retriever
    <br />
    <a href="https://github.com/Sufyan123o/SufRetriever">Report Bug</a>
    ·
    <a href="https://github.com/Sufyan123o/SufRetriever">Request Feature</a>
  </p>

  <p align="center">
    <a href="https://paypal.me/SufyanO?country.x=GB&locale.x=en_GB">
    <img src="https://pics.paypal.com/00/s/OGQwMWQ4YzQtN2QwZS00OTA0LWJjNzktZGI3OTE2NjRmYWIz/file.PNG" alt="Logo" width="auto" height="50" >
  </a>
  </p> 
</p>
<br />

Please **star** this repository to increase the awareness of the project for others to use or add to. 

Join the Discord Server YasCommunity for Code, Sneakers and Everything in-between! Join [here](https://discord.gg/b6zyJyCQUu)

<p align="center">
  <a href="https://github.com/Sufyan123o/SufRetriever">
    <img src="https://media.discordapp.net/attachments/597104422123995136/1099811349166575686/download_2-modified.png" alt="Logo" width="auto" height="256">
    <img src="https://cdn.discordapp.com/attachments/692518598241026139/1099801733884035134/image.png" alt="Logo" width="auto" height="256">
  </a>
</p>
<br />

<div align="center">

# Suf Retriever Discord Bot 🤖

</div>


Suf Retriever is a **Discord bot** that monitors and notifies users about new sneaker raffles on the [Sole Retriever](https://www.soleretriever.com/) website. It fetches the latest raffle data and sends a notification through a webhook with an embedded message, including the raffle details such as region, delivery method & raffle type.

## 🌟 Features

- Monitors New Sneaker Raffles on Sole Retriever
- Sends notifications with Embedded Messages through a Discord Webhook
- Supports a Test Command for Manual Testing `!test` .Type this in the Discord Channel

## 🛠 Setup and Installation

1. Make Sure you have Python Installed. Then Install the required Python packages in using Command Prompt or Terminal:  
    Python and PIP installation guides can be found in the Discord server [here](https://discord.gg/b6zyJyCQUu).
    ```
    pip install -r requirements.txt
    ```

2. Open the SufRetriever.py file in an IDE or a Text Editior such as NotePad and add your Discord Bot token:  

    A guide on How to get a Bot Token Can be found [here](https://discordgsm.com/guide/how-to-get-a-discord-bot-token).  
    
    LEAVE THE TOKEN WITHIN THE APOSTROPHES
    ```
    TOKEN=your_discord_bot_token_here
    ```

    Replace `your_discord_bot_token_here` with your actual Discord bot token.

3. Set the `WEBHOOK_URL` variable in the script to the webhook URL you created in your Discord server.  

    A guide on How to get a Webhook Can be found [here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).  

    LEAVE THE WEBHOOK WITHIN THE APOSTROPHES
    ```
    TOKEN=your_discord_webhook_here
    ```

4. Open a terminal or command prompt and navigate to the directory containing the bot script using the `cd` command:

    ```
    cd path/to/your/bot/script
    ```

    Replace `path/to/your/bot/script` with the actual path to the directory containing the bot script.

    For example, if the script is located in `C:\Users\YourUsername\Documents\DiscordBots\SufRetriever`, you would type:

    ```
    cd C:\Users\YourUsername\Documents\DiscordBots\SufRetriever
    ```

    Once you are in the correct directory, run the bot script:

    ```
    python SufRetriever.py
    ```
    or if on Mac:
    ```
    python3 SufRetriever.py
    ```


    Replace `bot_script.py` with the name of the Python script containing the bot code.



## 📚 Commands

- `!test`: Sends a test webhook notification with a pre-defined raffle URL. This command can be used to check if the webhook and embed formatting are working correctly.

## 📄 License

Distributed under the GNU General Public License v3.0 License. See [GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.en.html) for more information..
