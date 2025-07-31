# Music Player Playlist in Python

# Overview:

This project is a command-line music playlist manager programmed in Python. It allows users to create, manage, and interact with a playlist of songs through a variety of features such as adding, deleting, searching, playing, and sorting songs. The playlist is stored persistently in a text file, “playlist.txt”, to ensure data retention between sessions. The program utilizes a doubly linked list structure to manage the playlist dynamically, enabling efficient insertion, deletion, and traversal of songs. Additionally, users can view recently played songs, sort their playlist alphabetically, and load a playlist from a file.

Designed for music enthusiasts or anyone interested in building a simple yet functional playlist management tool, this application combines data structures, file handling, and user interaction allowing for interactive menus to provide a seamless experience for managing your favorite songs.

# Features:
•	Add songs to the playlist (manually or from file)
•	Delete songs by name or position in the playlist
•	Search for songs within the playlist
•	Play songs (simulated with messages) and maintain a recently played list
•	View the current playlist
•	View recently played songs
•	Sort the playlist alphabetically
•	Save the playlist to and load from a file, “playlist.txt”
•	Delete songs from both the playlist and file, allowing for management of the playlist with multiple options, including full control over songs

## Technologies Used:
•	Python 3.11
•	Standard Python libraries (os, sys)

# Usage Instructions:

## Installation & Setup:
1.	Clone this repository. Ensure that Python 3.11 is installed inside of a runnable IDE (Such as PyCharm).
2.	After that there are no additional libraries required; just run the “main.py” script directly.

## Running the Main Program:
1.	Launch the program: python main.py
2.	The program will display a menu with the following options:
o	Add a new song
o	Delete a song
o	Display the playlist
o	Count total songs
o	Search for a song
o	Play a song
o	View recently played songs
o	View last played song
o	Sort playlist alphabetically
o	Load playlist from a file
o	Exit
3.	Follow the prompts to manage your playlist as desired. The playlist will still be there and persist between sessions via the playlist.txt file.

## How It Works:
•	Adding songs: Entries are appended to the linked list and saved in playlist.txt.
•	Deleting songs: Remove songs by name from the list and update the text file.
•	Searching: Find if a song exists by name inside of the playlist file.
•	Playing: Simulate playing a song and update recently played list.
•	Sorting: Arranges songs in the playlist alphabetically.
•	Persistence: Load existing playlist on startup, save changes automatically.

# Contributing To the Codebase:
Contributions are welcome! Feel free to fork, modify, and submit pull requests to improve and expand upon functionality or fix bugs. Pull requests are appreciated.
