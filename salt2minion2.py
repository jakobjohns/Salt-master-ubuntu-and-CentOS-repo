#!/usr/bin/env python3

import os
import subprocess
from progress.bar import Bar

'''
    This script assumes a couple of things that are key for successful repository creation
    1. Even though it pings an initial, it still presumes the user has checked for the minion machines to be up and running with the keys
       already accepted which eliminates any configuration from the script as well

    2. This is meant to be run on the SALT-MASTER machine, not the minion

    3. It figures that whatever machine you are running the minions on has enough space
       if this is not the case, OS error exception handling could create unexpected consequences
'''

# main is used just for choice selection 
def main():
    # calls for both types of repos
    print("Choose an option (# only): \n")
    print("1 - CentOS \n")
    print("2 - Ubuntu \n")
    print("3 - Both \n")

    # variable for input
    getUserOption = input()
    minionCheckIfUP(getUserOption)

def minionCheckIfUP(getUserOption):
     # Quick check to see if a minion returns true with a ping
    minionUp = (b'True')
    minion_check = subprocess.check_output(['salt', '*', 'test.ping'])
    disallowed_characters = ":"
    # Check to see if "true" statement is there then continue
    if minionUp in minion_check:
        print("Minion(s) is up!")
        print("--------------------------")
        if getUserOption == '1':
        # This is to see what OS is running
            lines = subprocess.Popen(['salt', '-G', 'os:CentOS', 'test.version'], stdout=subprocess.PIPE)
            proc = lines.communicate()[0]
            test = proc.decode('utf-8') 
            osLine = test.splitlines()[0]
            print(osLine)
            # For loop to eliminate the annoying characters it returns
            for character in disallowed_characters:
                osLine = osLine.replace(character, "")
            # Call CentOS function after letting user know it is up
            print("CentOS minion is up!")
            centos(osLine, getUserOption)
        elif getUserOption == '2':
        # Assuming that it does not match the CentOS then we call the correct one
            lines = subprocess.Popen(['salt', '-G', 'os:Ubuntu', 'test.version'], stdout=subprocess.PIPE).communicate()[0]
            osLine = print(lines.splitlines()[0]) + ('\n')
            print("Ubuntu OS is up!")
            ubuntu(osLine)
        elif getUserOption == '3':
            # Check for CentOS
            try:
                lines = subprocess.Popen(['salt' '-G' 'os:CentOS' 'test.version'], stdout=subprocess.PIPE).communicate()[0]
                osLine = print(lines.splitlines()[0]) + ('\n')
                print("CentOS minion is up!")
                # Check for ubuntu
                lines = subprocess.Popen(['salt' '-G' 'os:Ubuntu' 'test.version'], stdout=subprocess.PIPE).communicate()[0]
                osLine = print(lines.splitlines()[0]) + ('\n')
                print("Ubuntu OS is up!")
                # Call CentOS first
                centos(osLine, getUserOption)
            # I have no idea what could happen here
            except OSError:
                print("One of the minions are not responding to CentOS or Ubuntu")
        else:
            print("Improper option!")
    # if we get nothing then just assume it's not up and kill the process       
    else:
        print("Minion(s) is down!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        exit
    
def centos(osLine, getUserOption):
    print("Starting CentOS repo creation...")
    # Start performing commands with salt per repo
    # Creating a directory called repo{#} to store a repo 
    index = int()
    testLoop = False
    cmd = "salt " + str(osLine) + " cmd.run 'mkdir /repo'" + str(index)
    while not testLoop:
        try:
            dirCreate = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
            dirCreate.wait()
            testLoop = True
            print("Successfully created directory")
        except:
            index = index + 1
            pass # Go and try create file again
    
    # Pull down recent updates and store it in the created dir
    userRepo = input("What repo would you like to pull from? (type -1 if done): ")
    while (userRepo != '-1'):
        repocmd = "salt " + str(osLine) + " cmd.run 'reposync --repoid=" + userRepo + " --download_path=/repo'"+ str(index)
        repodir = subprocess.Popen(repocmd, stderr=subprocess.PIPE, shell=True)
        repodir.wait(print("Downloading packages from " + userRepo + ", this may take a while..."))
        print("Finished downloading packages from " + userRepo + " at /repo" + str(index))
        choice = input("Would you like to do another? (type Y or N): " )
        if (choice.upper == 'Y'):
            continue
        else:
            break

    createrepocmd = "salt " + str(osLine) + " cmd.run 'creatrepo /repo'" + str(index)
    create_Repo = subprocess.Popen(createrepocmd, stderr=subprocess.PIPE, shell=True)
    create_Repo.wait(print("Creating repo metadata..."))
    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created and is listed below: \n")
    list_files = "salt " + str(osLine) + " cmd.run 'ls -l /repo'" + str(index)
    listWait = subprocess.Popen(subprocess.Popen(list_files, stderr=subprocess.PIPE, shell=True))
    listWait.wait()
    # Check to see if getUserOption was used
    if (getUserOption == '3'):
        print("Starting Ubuntu repo creation...")
        ubuntu()
    else:
        print("Terminating program")
        print("----------------------------")
        exit()
      
def ubuntu(osLine):
    index = ''
    # While loop allows us to tack on a random number to get a proper directory creation
    cmd = "salt " + str(osLine) + " cmd.run 'mkdir /repo'" + str(index)
    while True:
        try:
            index = index + 1
            dirCreate = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
            dirCreate.wait()
            break
        except:
            pass # Go and try create file again
    # Find the mirror.list file and change the base_path
    a_file = open("/etc/apt/mirror.list", "r")
    list_of_lines = a_file.readlines()
    list_of_lines[2] = "set base_path   /repo" + index ,"\n"
    # This reopens the copied file and writes what we need for it
    a_file = open("/etc/apt/mirror.list", "w")
    a_file.writelines(list_of_lines)
    a_file.close()

    # Pull down recent updates and store it in the created dir
    cmd1 = "salt " + osLine, " cmd.run 'apt-mirror /repo'" + str(index)
    subprocess.Popen(cmd1, stderr=subprocess.PIPE, shell=True)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created and is listed below: \n")
    cmd3 = "salt " + osLine, " cmd.run 'ls -l /repo" + str(index)
    subprocess.Popen(cmd3, stderr=subprocess.PIPE, shell=True)

# As always, call the main function
if __name__ == '__main__':
    main()
