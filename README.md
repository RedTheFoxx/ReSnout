# ReSnout

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white) ![Database](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

ReSnout is a multi-tool bot, a rebirth of the original Snout, originally built in C#. It now features a plugin-oriented architecture for easy extensibility.

> **VERSION 1.0**

## Available plugins

### Music Player

| Command                  | Description                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| **/add [url]**     | Add a YouTube video or playlist to the queue.                                               |
| **/list**          | Display the current queue of videos.                                                        |
| **/clear [index]** | Clear the entire queue or remove a specific item.                                           |
| **/play [url]**    | Play the audio of a YouTube video. If no URL is provided, plays the next item in the queue. |
| **/stop**          | Stop the currently playing audio and disconnect from the voice channel.                     |
| **/pause**         | Pause the currently playing audio.                                                          |
| **/resume**        | Resume playing the paused audio.                                                            |
| **/skip**          | Skip the currently playing audio and play the next item in the queue.                       |

### Cemantix Game

| Command            | Description                                        |
| ------------------ | -------------------------------------------------- |
| **/cem**     | Start a new Cemantix game.                         |
| **/cemrank** | Display your Cemantix ranking and the leaderboard. |

#### Cemantix Game Ranking System

The Cemantix game uses a custom ranking system with ranks (Bronze, Silver, Gold, Platinum, Master) and tiers (I, II, III). Players earn points based on performance, calculated using a modified ELO system. The performance score (S) is derived from attempts and time taken to find the word:

$S = (0.9 * \frac{1}{attempts}) + (0.9 * \frac{1}{time})$

The ELO change is calculated as:

$delta\_elo = K * (S - MMR)$

Where:

- $K$ is a constant (20).
- $S$ is the performance score.
- $MMR$ is the player's average performance rating.

### Rich Notifier

| Command                        | Description                                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **/notifyall [message]** | Send a notification to everyone with a formatted embed. Optional parameters include title, color, and footer. |

### Simple Operations

| Command                    | Description                                                                        |
| -------------------------- | ---------------------------------------------------------------------------------- |
| **/dice [dice_str]** | Roll some dice using RPG notation (modifiers accepted) (e.g.,`/dice 2d6+3d4+5`). |
| **/gw**              | Check the Discord API response time.                                               |
| **/sys**             | Retrieve some information about mem and disk usage (Raspberry PI only)             |
