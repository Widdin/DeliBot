![DeliBot-Banner](https://github.com/OfficialWiddin/DeliBot/blob/master/images/DBanner.png)

# DeliBot
A Discord bot that helps Pokémon GO communities to organize raids in Discord.  
DeliBot is a Discord bot written in Python 3.6.

## Discord
Join the server to get help, make a suggestion or just chat!  
Invite - https://discord.gg/f2mkW8g  

## How to run DeliBot on your server
1. Invite DeliBot - https://discordapp.com/oauth2/authorize?client_id=354229190666616844&scope=bot&permissions=1342532672
2. Go to a channel in your server and run `!install` one time.

## Information
- Everyone are able to use the ``!raid``-command.  
- DeliBot updates the Raid on every reaction.
- DeliBot will delete the Raid 2 hours after creation.
- DeliBot will remove your command-message (when you type e.g `!raid`).
- Click on your team emoji and If you are coming with extra players, you can react and combine 'One', 'Two' and 'Three' up to six extra players (note that those extra players will only count towards 'Total :' as they have no name).  

## Commands
### Server-owner 
- `!install` - Uploads necessary emojis to the server in order to work correctly.

### Server-owner and administrators

### Server configuration

- `!set_raid_channel` - Any Raid that gets created will be automagically posted in this channel. You will be asked to tag a channel by using #. 
- `!unset_raid_channel` - The channel set with "set_raid_channel" will become none.
- `!set_ex_channel` - Any EX-Raid that gets created will be automagically posted in this channel. You will be asked to tag a channel by using #.
- `!unset_ex_channel` - The channel set with "set_ex_channel" will become none.
- `!set_profile_scan` - The channel will be continuously checked for Team images and give the player that posts an image a role based on their color. You will be asked to tag a channel by using #. 
- `!unset_profile_scan` - The channel set with "set_profile_scan" will become none.
- `!set_ex_scan` - Set where to scan for EX-Raid pass images.
- `!unset_ex_scan` - The channel set with "set_ex_scan" will become none.
- `!set_role_permission` - The role will be granted permissions to edit and delete any Raid and also use create/delete gym. You will be asked to tag a role by using @.
- `!unset_role_permission` - The role set with "set_role_permission" will become none.
- `!set_gmt` - Sets the GMT for your timezone so research-quests gets deleted on the correct time. You will be asked to enter a GMT, such as +1, 0, -1
- `!set_language` - Set the language for the server.
- `!set_log_channel` - Any Raid created / edited / deleted will be posted in this channel. You will be asked to tag a channel by using #.
- `!unset_log_channel` - The channel set with "set_log_channel" will become none.
- `!set_event_overview` - This will post a message that updates continuously with on-going / up-coming events. You will be asked to tag a channel by using #.
- `!set_raid_overview` - This will post a message that updates continuously with on-going Raids. You will be asked to tag a channel by using #.
- `!set_ex_overview` - This will post a message that updates continuously with on-going Raids. You will be asked to tag a channel by using #.

- `!set_role_permission` - Delibot will ask you to tag a role by using `@`. The role will be granted permission to edit and delete any Raid, also permission to use `add_gym`/`del_gym`. 
- `!unset_role_permission` - This will remove the role you had set.  
- `!set_overview` - Set where to show an overview-message of active raids, updates every 2nd minute.

### Server-owner, Administrators, Role Specific
- `!create gym  {gym name} {lat} {lon}` - Adds a Gym to the database so it will appear as a hyperlink on Raid-creations.  
*Example: !create gym "Some name" 60.450 -20.350*
- `!delete gym {gym name}` - Deletes a Gym from the database.  
- `!create pokestop  {gym name} {lat} {lon}` -  Adds a Pokestop to the database so it will appear as a hyperlink on Research-creations. 
- `!delete pokestop {pokestop name}` - Deletes a Pokestop from the database.  

### Everyone
- `!help` - Displays available commands and other info.  
- `!list quests` - List of todays Research tasks.
- `!list gyms` - List of the added Gyms.
- `!find {name}` - Get the Google Maps link to a location.
- `!valor` - Assigns the role Valor to you.
- `!mystic` - Assigns the role Mystic to you.
- `!instinct` - Assigns the role Instinct to you.
- `!pokebox` - Totally useless but fun command!
- `!raid` - Opens a private message dialog with Delibot, to create a Raid by answering questions.
- `!raid {boss} {time} {location*}` - Starts a Raid with the given information, lasts for 2 hours.  
  | `{boss}` - Needs to be one connected name, e.g. "*Entei*".  
  | `{time}` - Needs to be one connected time, e.g. "*12:00*".  
  | `{location*}` - Can be multiple lines, e.g. "*Center of town*".  

- `!exraid {boss} {time} {day} {location*}` - Just like "`!raid`" but it lasts for 14 days. 
  | `{day}` - Needs to be one connected day, e.g. "*Monday*" or "*Monday-(01/01/2017)*"  
    
- `!trade {pokémon have*} , {pokémon want*}` - Text & Image of what you want to trade in a clean message.  
  | `{pokémon have*}` - The pokémon you want to trade away, e.g. "*shiny aron*".  
  | `{pokémon want*}` - The pokémon you want to have, e.g. "*shiny ash pichu*".  

- `!want {pokémon want*}` - Text & Image of what you want to have in a clean message.  
  | `{pokémon want*}` - The pokémon you want to have, e.g. "*shiny ash pichu*".  

- `!offer {pokémon have*}` - Text & Image of what you want to offer in a clean message.  
  | `{pokémon have*}` - The pokémon you want to trade away, e.g. "*shiny aron*".  
  
- `!community_day` - Information message of the next Community-day.
  
- `!research {quest*} , {reward*} , {pokestop*}` - Clean message dislaying the quest.  
  | `{quest*}` - Can be multiple lines, e.g. "*Catch 10 pokémon*".  
  | `{reward*}` - Can be multiple lines, e.g. "*1 rare candy*".  
  | `{pokestop*}` - Can be multiple lines, e.g. "*The gitstop*".    

- `!counter {league} , {pokemon}, {limit}` - Shows detailed information with counters on a specific Pokémon.
  - Leagues: great (g), ultra (u), master (m), silph (s)
  - Match-ups: general (g), counters (c)
  - Limit: 1-24
  - *Example:!counter ultra snorlax* 
  
 - `!pokebattler {pokemon}` - Shows detailed information with counters on a specific Raid-boss.  

 - `!silphcard {name}` - Shows information of a players silphcard.
 
 - `!fusion {pokemon} {pokemon}` - Combines two Pokémon images and creates a single one. (Only works with Gen 1)
 
Get the stats of a user.
- `!stats` - Your own stats.
- `!stats @user` - Stats for a user.
- `!stats server` - Total stats for this server.
- `!stats overall` - Total stats for all servers.
- `!stats leaderboard` - Leaderboard for best stats on this server.

Arguments marked with `*` can contain more than one word.  
Do not include the `{` `}` brackets.

*(Names are censored on github)*  
For e.g. "`!raid entei 19:30 on github`" will display:  
![Raid-message](https://raw.githubusercontent.com/OfficialWiddin/DeliBot/master/images/Raid.PNG)


For e.g. "`!exraid mewtwo 19:30 sunday on github`" will display:  
![ExRaid-message](https://raw.githubusercontent.com/OfficialWiddin/DeliBot/master/images/ExRaid.PNG)  


For e.g "`!research hatch 5 eggs, chansey, on github`" will display:  
![Research](https://raw.githubusercontent.com/OfficialWiddin/DeliBot/master/images/research.PNG)


For e.g "`!stats`" will display:  
![Stats](https://raw.githubusercontent.com/OfficialWiddin/DeliBot/master/images/stats.PNG)


For e.g "`!list raids`" will display:  
![list-raids](https://raw.githubusercontent.com/OfficialWiddin/DeliBot/master/images/list_raids.PNG)

## Aliases:
`!raid`   = `!Raid` / `!r` / `!R`  
`!exraid` = `!Exraid` / `!xr` / `!Xr`  
`!trade`  = `!Trade` / `!t` / `!T`  
`!want`   = `!Want` / `!w` / `!W`  
`!offer`  = `!Offer` / `!o` / `!O`  
`!community_day` = `!community` / `!cday` / `!cd`  
`!research` = `!rs`  / `!Research` / `!Q` / `!Quest` / `!quest`  


## Contribute:
If you want to contribute with something / contact me, then hit me up on:  
**Discord** - Widdin#6289  / Dimios#0592

