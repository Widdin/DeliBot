

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
#### Server-owner 
- `!install` - Imports necessary emojis to the server (server-owner only) 

#### Server-owner and administrators

Get the stats of a user.
- `!stats` - Your own stats.
- `!stats @user` - Stats for a user.
- `!stats server` - Total stats for this server.
- `!stats overall` - Total stats for all servers.
- `!stats leaderboard` - Leaderboard for best stats.

Server configuration
- `!set_gmt` - Set the GMT for the server.
- `!set_language` - Set the language for the server.
- `!set_ex_scan` - Set where to scan for ex-raid passes.
- `!set_profile_scan` - Set where to scan for team images.
- `!set_raid_channel` - Set where to post raids by default.
- `!set_ex_channel` - Set where to post ex-raids by default.
- `!unset_ex_scan` - Unset where to scan for ex-raid passes.
- `!unset_profile_scan` - Unset where to scan for team images.
- `!unset_raid_channel` - Unset where to post raids by default.
- `!unset_ex_channel` - Unset where to post ex-raids by default.
- `!set_role_permission` Run this command and Delibot will ask you to tag a role by using `@`. The chosen role will now be granted permission to edit & delete ANY raid. They will also have permission to use `add_gym` / `del_gym`. 
- `!unset_role_permission` Run this command and Delibot will remove the role you had set.

#### Role specific, administrators and server owner
- `!add_gym  awesome gym name , link to google map` - Add a Gym to the database so it will appear as a hyperlink on raids.
*Make sure to have , between the name and hyperlink*.

If you want the !find gym-name command to show an image like this 

![raid-with-link](https://cdn.discordapp.com/attachments/416342787240230917/488314774292135937/unknown.png)


Link NEEDS to be in this format: https://www.google.com/maps/place/longitude,latitude
e.g https://www.google.com/maps/place/23.28273,47.97334

BUT, If you use any other links the !find command and hyperlinks on locations will still work, the image just wont show up, thats all.
- `!del_gym {name}` - Delete any hyperlinked gym.


#### Everyone
- `!help` - Displays available commands and other info.  
- `!list raids`
- `!list quests`
- `!list gyms`
- `!find {name}` - Get the google maps link to a location
- `!valor` - Sets your role to Valor.
- `!mystic` - Sets your role to Mystic
- `!instinct` - Sets your role to Instinct
- `!pokebox` - Useless but fun feature!
- `!raid` - Opens a private message dialog to create a raid
- `!raid {boss} {time} {location*}` - Starts a raid-message with the given information.  
  | `{boss}` - Needs to be one connected name, e.g. "*Entei*".  
  | `{time}` - Needs to be one connected time, e.g. "*12:00*".  
  | `{location*}` - Can be multiple lines, e.g. "*Center of town*".  

- `!exraid {boss} {time} {day} {location*}` - Just like "`!raid`" but it lasts for 10 days and updates every 30min.  
  | `{day}` - Needs to be one connected day, e.g. "*Monday*" or "*Monday-(01/01/2017)*"  
    
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
