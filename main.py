# Name: Michael Pallwitz
# Class: CIS152 12742-13083
# Program Name: Data Structures Final Project, Music Player Playlist

# Imports in the os system used to fetch its contents and be able to access, create, and remove directory folders.
import os

# This class is used to call data types that will be used to store values
class Node:

    # This function is used to initialize song, next, and prev for use later in the program
    def __init__(self, song):
        self.song = song
        self.next = None
        self.prev = None

# This function makes the text file so we can begin the playlist
def tofile(a):
    with open("playlist.txt", "a") as f1:
        f1.write(a + "\n")

# This adds a piece of node data to the playlist in the form of a song name, storing it in the playlist text file,
# starting the additive of a song in a loop until the line is blank again in turn bringing you back to the start of the playlist menu options
def add_node(first):
    a = input("\nPlease enter Song name:  ")
    while first.next != None:
        first = first.next
    first.next = Node(a)
    first.prev = first
    first = first.next
    tofile(a)
    first.next = None

# This function adds the file for the node, or song name in this case for this programmed class
def add_node_file(first, a):
    while first.next != None:
        first = first.next
    first.next = Node(a)
    first.prev = first
    first = first.next
    first.next = None

# If this function gets called from the playlist options menu, the function sets up for deleting a song, while doing this,
# this function reads the lines of the playlist.txt file and deletes whatever song or the pos of the song that a user inputs
def delete_file(a):
    with open("playlist.txt", "r") as f1:
        lines = f1.readlines()
    with open("playlist.txt", "w") as f1:
        x = 0
        for line in lines:
            if a != line.strip():
                f1.write(line)
            else:
                x = 1
    if x == 0:
        print("The song with the name you entered unfortunately doesn't exist, please try again")
    else:
        print("The song has been deleted")

# This sets up the code to delete a node of data, importing in the first and using the next variables to accomplish this
def del_node(first):
    while first.next.next != None:
        first = first.next
    temp = first.next.next
    first.next = None
    del temp
    print("Deleted")

# This function imports in the first variable, and is used to set up and directly print the name of the playlist on a new line,
# setting the layout to display all the songs in the list, these both will be used for the third part of the playlist; which is displaying the playlist
def printlist(first):
    print("\nPlaylist Name: ")
    while first.next != None:
        print(first.song)
        first = first.next
    print(first.song)

# The function imports in the first variable, using it for a while in order to count how many songs are in the playlist upon calling the function within the program,
# or for the user side of the playlist menu, and pressing selection number 4
def count_nodes(first):
    i = 0
    while first.next != None:
        first = first.next
        i += 1
    i += 1
    print("\nThe total songs found within the playlist is:  ", i - 1)

# Imports both the pointer and pos variables, this function is alike with del_node and delete_file, this being the coded function to delete the pos,
# This uses if, else, and while loops to accomplish this. Making a print statement on each loop except the while loop
# in an effort to ensure to the user that the list was updated and to check the display in order to make sure it was working the way it was intended
def del_pos(pointer, pos):
    n1 = prev1 = temp = None
    i = 0
    if pos == 1:
        temp = pointer
        delete_file(temp.song)
        pointer = pointer.next
        pointer.prev = None
        del temp
        print("\nThe list has been updated\nPlease use the display function to check\n")
        return pointer
    while i < pos - 1:
        prev1 = pointer
        pointer = pointer.next
        i += 1
    if pointer.next == None:
        temp = pointer
        delete_file(temp.song)
        prev1.next.prev = None
        prev1.next = None
        del temp
        print("\nThe list has been updated\nPlease use the display function to check\n")
    else:
        temp = pointer
        delete_file(temp.song)
        prev1.next = temp.next
        temp.next.prev = prev1
        del temp
        print("\nThe list has been updated\nPlease use the display function to check\n")

# This function brings the fifth selection of the playlist menu to fruition, bringing the search song function alive through if/else's to check if the song inputted by the user is in their created playlist or not
def search1(first):
    song = input("\nPlease enter the song name you wish to search for: ")
    flag = 0
    while first != None:
        if first.song == song:
            print("\nWe found the song that you searched for!")
            flag += 1
            break
        else:
            first = first.next
    if flag == 0:
        print("\nUnfortunately we were unable to find that song")

# Creates the function for top making it global, so I can access the variable anywhere in the functions needed throughout the playlist
def create():
    global top
    top = None

# This function imports the data variable and the global top variable into the function in order to push the node or the data to the top of the program.
# This in turn is used for a portion of number six of the playlist menu playing a song, it is needed, so that we can skip between the songs thus the use of top and next.
def push(data):
    global top
    if top == None:
        top = Node(data)
        top.next = None
    elif top.song != data:
        temp = Node(data)
        temp.next = top
        top = temp

# This display function calls for the global top variable once again, so that we as a user could check to see which list was recently played, or the seventh playlist menu option
# This calls top1 or the top global variable of the song to the front so that we can display it to the user, using an if while statement to check if the top is empty and if so print a statement saying so and if not, then print the top song
def display():
    global top
    top1 = top
    if top1 == None:
        print("\n=>No tracks were recently played from this playlist")
        return
    print("\nThe recently played tracks are:")
    while top1 != None:
        print(top1.song)
        top1 = top1.next

# This is the calling and more client side of the sixth portion of the playlist menu, where we play the song from within the playlist.
# The print statements found within this function are employed so that the user knows what song is being played and making it so that the user has the ability to choose what song to play within the list.
# This is dome by if, else, and while loops, importing in the first variable, in order to play the song variable which is determined off of the users input
def play(first):
    printlist(first)
    song = input("\nPlease choose the song you wanted to play: ")
    flag = 0
    while first != None:
        if first.song == song:
            print("\n=>Now Playing:", song)
            flag += 1
            push(song)
            break
        else:
            first = first.next
    if flag == 0:
        print("\n#Unfortunately no songs were ever found, please try again")

# This is used to call the already made display function and using it to print specifically just the last played song from the playlist
def recent():
    display()

# This function pulls the top global element into the function, using it to complete the eighth playlist menu option, which is to call the last played element.
# Which is why there is two print statements both of which are based for the last played song, utilizing an if statement to check if the top is empty then printing that there are no played tracks,
# and the other printing the last played song to the console
def topelement():
    global top
    top1 = top
    if top1 == None:
        print("\n#NO last played tracks were available")
        return
    print("\n=>Last Played Song: ", top.song)

# This function is used for the ninth menu option of the playlist to sort the playlist. It uses many while, else and if loops to ensure that the songs get sorted in the correct order.
# This sorting process gets based on the songs name in order of their character letters.
def sort(pointer):
    a = b = c = e = tmp = None
    while e != pointer.next:
        c = a = pointer
        b = a.next
        while a != e:
            if a.song > b.song:
                if a == pointer:
                    tmp = b.next
                    b.next = a
                    a.next = tmp
                    pointer = b
                    c = b
                else:
                    tmp = b.next
                    b.next = a
                    a.next = tmp
                    c.next = b
                    c = b
            else:
                c = a
                a = a.next
            b = a.next
            if b == e:
                e = a
    return pointer

# This completes the final portion of the playlist menu other than exiting the program which is done in the main function. This function is for adding a file or the tenth option within the playlist menu options.
# The function imports in the start variable to open the current playlist file and uses a with for loop to add the playlist, giving confirmation to the user through the print of "playlist added" upon making a new playlist
def addplaylist(start):
    with open("playlist.txt", "r") as f1:
        lines = f1.readlines()
    for line in lines:
        add_node_file(start, line.strip())
    print("We added that playlist for you")

# This function is the search of a song and half of the display portion for the second option within the playlist menu, this function is used to search for the song inputted by the user in order to delete it from the playlist.
# It does this by asking the user to input the song they wish to delete from the playlist, then using while and if statements to find it and confirm with the user that it was found and deleted or not found and thus not deleted
def del_search(start):
    printlist(start)
    song = input("\nPlease choose the song you wish to delete from the playlist: ")
    flag = 0
    while start != None:
        if start.song == song:
            print("\nWe found the song and deleted it off your playlist for you")
            temp = start
            delete_file(temp.song)
            temp.prev.next = temp.next
            temp.next.prev = temp.prev
            del temp
            flag += 1
            break
        else:
            start = start.next
    if flag == 0:
       print("\nWe were not able to find the song that was input, please check the spelling of the song to ensure that the spelling was correct and attempt to delete it again ")

# This function is the search menu to delete and half of the display portion for the second option within the playlist menu, this function is targeted to delete a menu or pos of the playlist,
# it does this by using if and elif's, while having the user input a number between 1 and 2 to decide how the user wants to delete their song of choice. If the user chooses 1, it calls the del_search function and begins to run that portion of the code.
# If the user chooses the second option, it will then choose to search by position, where the program will again ask the user to input another number, this time for the pos of the song.
# Upon the user entering the pos, it will then call the del_pos function
def deletemenu(start):
    c = int(input("Which type of delete function did you want?\n1.By Search? \n Or\n2.By Position?\n"))
    if c == 1:
        del_search(start)
    elif c == 2:
        pos = int(input("\n Please enter the pos of the song: "))
        del_pos(start, pos - 1)

# This main function lives up to its name, calling in the global top variable, setting choice to zero to start, setting the start variable equal to Node in a list format. Printing a welcome statement,
# printing a disclaimer of how to make a space character within this program. Calling forward the create function and setting song to a string, then asking for a input of the playlists name from the user
def main():
    global top
    choice = 0
    song = ""
    start = Node("")
    print("**WELCOME TO THE MUSIC PLAYLIST PLAYER PROGRAM**")
    print("\n**Please use '_' when using a space character within this music playlist program**")
    start.song = input("Please enter your playlists name:  ")
    start.next = None
    hold = start
    create()

    # This long set of code is for the options that print so the user can use the playlist after creating a playlist name, after showing the choices to the user,
    # comes the if and elif train for the different options menus that are associated with a number from 1-11 within the program
    while choice != 11:
        print("\n1. Add A New Song To The Playlist\n2. Delete A Song From the Playlist\n3. Display The Current Playlist\n4. Total Songs Found Within A Playlist\n5. Search For a Song Within The Playlist\n6. Play A Song Within The Playlist\n7. View The Recently Played Songs List\n8. View The Last Played Within The Playlist\n9. Sort The Playlists Songs\n10. Add From A File\n11. Exit The Music Playlist")
        choice = int(input("\nPlease enter your choice: "))
        if choice == 1:
            add_node(start)
        elif choice == 2:
            deletemenu(start)
        elif choice == 3:
            printlist(start)
        elif choice == 4:
            count_nodes(hold)
        elif choice == 5:
            search1(start)
        elif choice == 6:
            play(start)
        elif choice == 7:
            recent()
        elif choice == 8:
            topelement()
        elif choice == 9:
            start.next = sort(start.next)
            printlist(start)
        elif choice == 10:
            addplaylist(start)
        elif choice == 11:
            exit(0)

# Driver to begin to run the program
if __name__ == "__main__":
    main()
