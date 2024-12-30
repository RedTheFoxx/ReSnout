# ReSnout

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white) ![Database](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

ReSnout is a multi-tool bot. This is a rebirth of the original Snout, originaly built in C#, and now with a plugin oriented architecture.

> **VERSION 0.1**

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

### Rich Notifier

- **/notifyall [message]**: Send a notification to everyone with a formatted embed. Optional parameters include title, color, and footer.

### Simple Operations

- **/dice [dice_str]**: Roll some dices using RPG notation (modifiers accepted) (e.g., `/dice 2d6+3d4+5`).
- **/gw**: Check the Discord API response time.
