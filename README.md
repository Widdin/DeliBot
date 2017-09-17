![DeliBot-Banner](https://github.com/OfficialWiddin/DeliBot/blob/master/images/Delibot_banner.png)

# DeliBot
A Discord bot which help Pokémon GO communities to organize raids in Discord.  
DeliBot is a Discord bot written in Python 3.6.


## How to run DeliBot on your server:
1. Invite DeliBot - https://discordapp.com/oauth2/authorize?client_id=354229190666616844&scope=bot&permissions=0
2. Create a new role named **Bot**
3. Keep all the default settings but also add **Manage messages** and **Manage Emojis**.
4. Assign the **Bot**-role to DeliBot.
5. Create a new role named **Admin** or/and **Moderator**
6. Assign the role to yourself.
7. Run `!install` once.


## Information:
- Only the ones who has the role 'Admin' or 'Moderator' are able to use the commands.
- DeliBot will remove his own reactions after 15 minutes (even thought they don't count, visual effect).
- DeliBot will remove his message after 2 hours (to save performance).
- DeliBot will remove your command-message.
- Only one team reaction will count and be displayed on the embed-message per user BUT if they are coming with multiple others they can react and combine 'One', 'Two' and 'Three' up to six extra players. Note that those 'extra' players will only count towards 'Total :' as they have no name.


## Commands:
- `!install` - Imports necessary emojis to the server and checks if they are valid. 
- `!help` - Displays available commands and other info.
- `!raid <boss> <time> <place*>` - Starts a raid-message with the given information.  
-- `<boss>` - Needs to be one connected name, e.g. *Entei*.  
-- `<time>` - Needs to be one connected time, e.g. *12:00*.  
-- `<place>` - Can be multiple lines, e.g. *Center of town*.
  
For e.g. `!raid entei 19:30 on github` will display:  
![raid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/Example.PNG)  


## Contribute:
If you want to contribute with something / contact me, then hit me up on:  
**Discord** - Widdin#6289
