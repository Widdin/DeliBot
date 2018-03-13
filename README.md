![DeliBot-Banner](https://github.com/OfficialWiddin/DeliBot/blob/master/images/DBanner.png)

# DeliBot
A Discord bot that helps Pokémon GO communities to organize raids in Discord.  
DeliBot is a Discord bot written in Python 3.6.

## Discord
Join the server to get help, make a suggestion or just chat!  
Invite - https://discord.gg/f2mkW8g  

## How to run DeliBot on your server:
1. Invite DeliBot - https://discordapp.com/oauth2/authorize?client_id=354229190666616844&scope=bot&permissions=0
2. Create a new role named **Bot**
3. Keep all the default settings but also add **Manage messages**, **Manage emojis** and **Manage roles**.
4. Assign the **Bot**-role to DeliBot.
5. Create a new role named **Admin** or/and **Moderator** or/and **Delibot** (Not case-sensitive).
6. Assign the role to yourself.
7. Run `!install` once.


## Information:
- Only the ones who has the role '**Admin**' or '**Moderator**' are able to use the ``!raid``-command.  
- DeliBot updates the raid-message every 15 sec.
- DeliBot will remove his own reactions after 45 minutes (even thought they don't count, visual effect).
- DeliBot will remove his own raid-message after 2 hours (to save performance).
- DeliBot will remove your command-message (when you type e.g `!raid`).
- Only one team reaction will count and be displayed on the embed-message per user BUT if they are coming with multiple others they can react and combine 'One', 'Two' and 'Three' up to six extra players. Note that those 'extra' players will only count towards 'Total :' as they have no name.


## Commands:
- `!install` - Imports necessary emojis to the server and checks if they are valid. 

- `!permission_all` - Grants everyone on the server permission to use the raid commands.  

- `!delete <message_id>` - Deletes a message from Delibot by using the ID of the message.

- `!help` - Displays available commands and other info.  

- `!raid <boss> <time> <place*>` - Starts a raid-message with the given information.  
  | `<boss>` - Needs to be one connected name, e.g. *Entei*.  
  | `<time>` - Needs to be one connected time, e.g. *12:00*.  
  | `<place>` - Can be multiple lines, e.g. *Center of town*.  
  
- `!shortraid <boss> <time> <place*>` - Just like "`!raid`" but compressed.  

- `!exraid <boss> <time> <day> <place*>` - Just like "`!raid`" but it lasts for 10 days and updates every 30min.  
  | `<day>` - Needs to be one connected day, e.g. *Monday* or *Monday-(01/01/2017)*  
  
  
For e.g. "`!raid entei 19:30 on github`" will display:  
![Raid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/Raid.PNG)


For e.g. "`!shortraid entei 19:30 also on github`" will display:  
![ShortRaid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/ShortRaid.PNG)


For e.g. "`!exraid mewtwo 19:30 sunday on github`" will display:  
![ExRaid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/ExRaid.png)

## Contribute:
If you want to contribute with something / contact me, then hit me up on:  
**Discord** - Widdin#6289
