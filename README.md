![DeliBot-Banner](https://github.com/OfficialWiddin/DeliBot/blob/master/images/DBanner.png)

# DeliBot
A Discord bot that helps Pokémon GO communities to organize raids in Discord.  
DeliBot is a Discord bot written in Python 3.6.

## Discord
Join the server to get help, make a suggestion or just chat!  
Invite - https://discord.gg/f2mkW8g  

## How to run DeliBot on your server:
1. Invite DeliBot - https://discordapp.com/oauth2/authorize?client_id=354229190666616844&scope=bot&permissions=1342532672
2. Run `!install` once.


## Information:
- Everyone are able to use the ``!raid``-command.  
- DeliBot updates the raid-message every 15 sec.
- DeliBot will remove his own reactions after 45 minutes (even thought they don't count, visual effect).
- DeliBot will remove his own raid-message after 2 hours (to save performance).
- DeliBot will remove your command-message (when you type e.g `!raid`).
- Only one team reaction will count and be displayed on the embed-message per user BUT if they are coming with multiple others they can react and combine 'One', 'Two' and 'Three' up to six extra players. Note that those 'extra' players will only count towards 'Total :' as they have no name.



## Commands:
- `!install` - Imports necessary emojis to the server (server-owner only) 

- `!help` - Displays available commands and other info.  

- `!raid <boss> <time> <place*>` - Starts a raid-message with the given information. Alias is `!r` instead of `!raid`  
  | `<boss>` - Needs to be one connected name, e.g. *Entei*.  
  | `<time>` - Needs to be one connected time, e.g. *12:00*.  
  | `<place>` - Can be multiple lines, e.g. *Center of town*.  

- `!exraid <boss> <time> <day> <place*>` - Just like "`!raid`" but it lasts for 10 days and updates every 30min. Alias is `!xr` instead of `!exraid`  
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
