#!/usr/bin/env python3

import os
import subprocess

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
    minionUp = ('True')
    minion_check = subprocess.check_output(['salt', '*', 'test.ping'])
    # Check to see if "true" statement is there then continue
    if minionUp in minion_check:
        print("Minion(s) is up!")
        print("--------------------------")
        if getUserOption == '1':
        # This is to see what OS is running
            lines = subprocess.Popen(['salt' '-G' 'os:CentOS' 'test.version'], stdout=subprocess.PIPE).communicate()[0]
            osLine = print(lines.splitlines()[0]) + ('\n')
            print("CentOS minion is up!")
            centos(osLine)
        elif getUserOption == '2':
        # Assuming that it does not match the CentOS then we call the correct one
            lines = subprocess.Popen(['salt' '-G' 'os:Ubuntu' 'test.version'], stdout=subprocess.PIPE).communicate()[0]
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
    # Start performing commands with salt per repo
    # Creating a directory called repo{#} to store a repo 
    index = ''
    while True:
        try:
            repoDir = os.system("salt " + osLine, " cmd.run 'mkdir /repo'" + index)
            break
        except OSError:
            if index:
                index = '('+str(int(index[1:-1])+1)+')' # Append 1 to number in brackets
            else:
                index = '(1)'
            pass # Go and try create file again
    # Pull down recent updates and store it in the created dir
    os.system("salt " + osLine, " cmd.run 'reposync --gpgcheck=1 --repoid=base --repoid=extras --repoid=updates \
        --repoid=centosplus --download_path=/repo'" + index)
    os.system("salt " + osLine, " cmd.run 'createrepo /repo'" + index)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created and is listed below: \n")
    os.system("salt " + osLine, " cmd.run 'ls -l /repo" + index)

    # Check to see if getUserOption was used
    if getUserOption == '3':
        ubuntu()

def ubuntu(osLine):
    index = ''
    # While loop allows us to tack on a random number to get a proper directory creation
    while True:
        try:
            repoDir = os.system("salt " + osLine, " cmd.run 'mkdir /repo'" + index)
            break
        except OSError:
            if index:
                index = '('+str(int(index[1:-1])+1)+')' # Append 1 to number in brackets
            else:
                index = '(1)'
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
    os.system("salt " + osLine, " cmd.run 'apt-mirror /repo'" + index)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created and is listed below: \n")
    os.system("salt " + osLine, " cmd.run 'ls -l /repo" + index)

# As always, call the main function
if __name__ == '__main__':
    main()