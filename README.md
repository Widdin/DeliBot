![DeliBot-Banner](https://github.com/OfficialWiddin/DeliBot/blob/master/images/DBanner.png)

# DeliBot
A Discord bot that helps Pokémon GO communities to organize raids in Discord.  
DeliBot is a Discord bot written in Python 3.6.

## Discord
Join the server to get help, make a suggestion or just chat!  
Invite - https://discord.gg/f2mkW8g  

## How to run DeliBot on your server:
1. Invite DeliBot - https://discordapp.com/oauth2/authorize?client_id=354229190666616844&scope=bot&permissions=1342532672
2. Go to a channel in your server and run `!install` one time.


## Information:
- Everyone are able to use the ``!raid``-command.  
- DeliBot updates the raid-message every 20 sec.
- DeliBot will remove his own reactions after 45 minutes (even thought they don't count, visual effect).
- DeliBot will remove his own raid-message after 2 hours (to save performance).
- DeliBot will remove your command-message (when you type e.g `!raid`).
- Only one team reaction will count and be displayed on the embed-message per user BUT if they are coming with multiple others they can react and combine 'One', 'Two' and 'Three' up to six extra players. Note that those 'extra' players will only count towards 'Total :' as they have no name.



## Commands:
- `!install` - Imports necessary emojis to the server (server-owner only) 

- `!help` - Displays available commands and other info.  

- `!raid {boss} {time} {location*}` - Starts a raid-message with the given information.  
  | `{boss}` - Needs to be one connected name, e.g. "*Entei*".  
  | `{time}` - Needs to be one connected time, e.g. "*12:00*".  
  | `{location*}` - Can be multiple lines, e.g. "*Center of town*".  

- `!exraid {boss} {time} {day} {location*}` - Just like "`!raid`" but it lasts for 10 days and updates every 30min.  
  | `{day}` - Needs to be one connected day, e.g. "*Monday*" or "*Monday-(01/01/2017)*"  
  
- `!edit boss {id} {boss}` - Change the boss on a raid-message.  
  | `{id}` - The number in the footer of the raid (1-500), e.g. "*89*".  
  | `{boss}` - Needs to be one connected name, e.g. "*Mewtwo*".  

- `!edit time {id} {time}` - Change the time on a raid-message.  
  | `{id}` - The number in the footer of the raid (1-500), e.g. "*89*".  
  | `{time}` - Needs to be one connected time, e.g. "*12:00*".  

- `!edit location {id} {location*}` - Change the location on a raid-message.  
  | `{id}` - The number in the footer of the raid (1-500), e.g. "*89*".  
  | `{location*}` - Can be multiple lines, e.g. "*Center of town*".  
  
- `!trade {pokémon have*} , {pokémon want*}` - Text & Image of what you want to trade in a clean Embed.  
  | `{pokémon have*}` - The pokémon you want to trade away, e.g. "*shiny aron*".  
  | `{pokémon want*}` - The pokémon you want to have, e.g. "*shiny ash pichu*".  

- `!want {pokémon want*}` - Text & Image of what you want to have in a clean Embed.  
  | `{pokémon want*}` - The pokémon you want to have, e.g. "*shiny ash pichu*".  

- `!offer {pokémon have*}` - Text & Image of what you want to offer in a clean Embed.  
  | `{pokémon have*}` - The pokémon you want to trade away, e.g. "*shiny aron*".  
  
- `!community_day {region} {GMT}` - Information window about the next Community-day.  
  | `{region}` - Needs to be one region, e.g. "*asia*", "*europe*", or "*america*".  
  | `{GMT}` - Your timezone from GMT+0, e.g. If you live in GMT+2 you type "*+2*".  
  
- `!research {quest*} , {reward*} , {pokestop*}` - Clean embed dislaying the quest.  
  | `{quest*}` - Can be multiple lines, e.g. "*Catch 10 pokémon*".  
  | `{reward*}` - Can be multiple lines, e.g. "*1 rare candy*".  
  | `{pokestop*}` - Can be multiple lines, e.g. "*The gitstop*".  

Arguments marked with `*` can contain more than one word.  
Do not include the `{` `}` brackets.

For e.g. "`!raid entei 19:30 on github`" will display:  
![Raid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/Raid.PNG)


For e.g. "`!exraid mewtwo 19:30 sunday on github`" will display:  
![ExRaid-message](https://github.com/OfficialWiddin/DeliBot/blob/master/images/ExRaid.png)

## Aliases:
`!raid`   = `!Raid` / `!r` / `!R`  
`!exraid` = `!Exraid` / `!xr` / `!Xr`  
`!edit`   = `!e`  
`!trade`  = `!Trade` / `!t` / `!T`  
`!want`   = `!Want` / `!w` / `!W`  
`!offer`  = `!Offer` / `!o` / `!O`  
`!community_day` = `!community` / `!cday` / `!cd`  
`!research` = `!rs`  


## Contribute:
If you want to contribute with something / contact me, then hit me up on:  
**Discord** - Widdin#6289
