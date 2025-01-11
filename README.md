# ReSnout

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white) ![Database](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

ReSnout is a multi-tool bot. This is a rebirth of the original Snout, originaly built in C#, and now with a plugin oriented architecture.

> **VERSION 1.0**

## Features

- 🎛️ **Plugin Architecture**: Easily extend the bot's capabilities with plugins.
- 🎶 **Music Playback**: Play audio from YouTube links, manage playlists, and control playback.
- 📢 **Rich Notifications**: Send formatted notifications to users with customizable embeds.
- 🎲 **Simple Operations**: Perform lightweight operations like dice rolls and stats.

## Plugins Commands

### Music Player

- **/add [url]**: Add a YouTube video or playlist to the queue.
- **/list**: Display the current queue of videos.
- **/clear [index]**: Clear the entire queue or remove a specific item.
- **/play [url]**: Play the audio of a YouTube video. If no URL is provided, plays the next item in the queue.
- **/stop**: Stop the currently playing audio and disconnect from the voice channel.
- **/pause**: Pause the currently playing audio.
- **/resume**: Resume playing the paused audio.
- **/skip**: Skip the currently playing audio and play the next item in the queue.

### Cemantix Game

- **/cem**: Start a new Cemantix game.
- **/cemrank**: Display your Cemantix ranking and the leaderboard.

#### Cemantix Game Ranking System

The Cemantix game uses a custom ranking system to track player progress.

##### Ranks and Tiers

Players are ranked using a combination of **Ranks** and **Tiers**. The ranks are:

- Bronze
- Silver
- Gold
- Platinum
- Master

Each rank is further divided into three tiers:

- I (highest)
- II
- III (lowest)

For example, a player might be "Gold II".

##### Points

Players earn points based on their performance in each game. These points determine their rank and tier. The points are calculated using a modified ELO system.

##### Performance Score

A performance score (S) is calculated based on the following factors:

- **Attempts**: The number of tries it took to find the word. Fewer attempts result in a higher score.
- **Time**: The time taken to find the word. Less time results in a higher score.
- **Accuracy**: Always 1.0 when the word is found.
- **Difficulty**: Currently a fixed value.

The formula for the performance score is:

$S = (0.9 * \frac{1}{attempts}) + (0.9 * \frac{1}{time})$

*Note: The accuracy and difficulty weights are currently unused.*

##### ELO Calculation

The ELO system is used to adjust the player's points after each game. The change in ELO points (delta_elo) is calculated as follows:

$delta\_elo = K * (S - MMR)$

Where:

- $K$ is a constant (currently 20) that determines the impact of each game on the ELO score.
- $S$ is the player's performance score.
- $MMR$ is a hidden rating that represents the player's average performance.

### Rich Notifier

- **/notifyall [message]**: Send a notification to everyone with a formatted embed. Optional parameters include title, color, and footer.

### Simple Operations

- **/dice [dice_str]**: Roll some dices using RPG notation (modifiers accepted) (e.g., `/dice 2d6+3d4+5`).
- **/gw**: Check the Discord API response time.
