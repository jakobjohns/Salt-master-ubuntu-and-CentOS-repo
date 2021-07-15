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

    mount()

def mount():

    print("\t\t\tLVM Automation Program")
    print("\t\t**************All of these will be created in your OS of choice****************")
    mycheck=True
    mayexit=True
    
    while (mayexit):
        os.system("tput setaf 3")
        print("\n")
        print("")
        print("\t1. To create a new partition using fdisk -l")
        print("\t2. To mount a partition")
        print("\t3. Exit & Continue to repo creation")
        print("")
        mycheck = True
        os.system("tput setaf 7")
        print("\n")
        
        a=int(input("Select any option from the above menu: "))
        while(mycheck == True):
            if (a == 1):
                parti = input("Enter the device name for which you want to create the partition (If you don't know it for the specific OS do not worry just leave blank): ")
                input("Press enter to continue...")
                break
            elif (a == 2):
                fs_type = input("Please enter the type of filesystem: (ext4, xfs")
                mount_point = input("What is the path of the mount point? (Your repo will be created here) ")
                fullmountpoint = "sudo mount -t " + fs_type + " " + parti + " " + mount_point
                break
            elif (a == 3):
                mayexit = False
                minionCheckIfUP(fullmountpoint, fs_type, parti, mount_point)
                break

def minionCheckIfUP(fullmountpoint, fs_type, parti, mount_point):
     # Quick check to see if a minion returns true with a ping
    operatingsys = input("What is the name of the operating system you would like to create a repo in? (CentOS, Ubuntu, CentOS-Docker, Ubuntu-Docker): ")
    salt_ping = "salt '*' test.ping"
    os.system(salt_ping)
    choice = input("What is the name of the machine? (Choices listed above.):  ")
    if (operatingsys.upper == "CENTOS"):
        centos(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point)
    elif (operatingsys.upper == "UBUNTU"):
        ubuntu(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point)
    elif (operatingsys.upper == "CENTOS-DOCKER"):
        centos_docker(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point)
    elif (operatingsys.upper == "UBUNTU-DOCKER"):
        ubuntu_docker(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point)
    else:
        print("Invalid option...")
        exit()

def centos(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point):
    print("Starting CentOS repo creation and mount...")
    # Start performing commands with salt and mounting
    os.system("fdisk -l")
    find_out = input("Would you like to create a partition for a device? (Y/N): ")
    if (find_out.upper == "Y"):
        parti = input("What device would you like to create a partition in?: ")
    
    make_dir = "salt " + choice + " cmd.run 'mkdir " + mount_point + "'"
    os.system(make_dir)
    try:
        os.system(fullmountpoint)
    except:
        print("Unexpected error occurred...")
    
    print("Successfully created directory")
    
    # Pull down recent updates and store it in the created dir
    userRepo = input("What repo would you like to pull from?: ")
    while (userRepo != '-1'):
        repocmd = "salt " + choice + " cmd.run 'reposync --repoid=" + userRepo + " --download_path=" + mount_point + "'"
        os.system(repocmd)
        print("Finished downloading packages from " + userRepo + " at " + mount_point + "'")
        user_choice = input("Would you like to do another? (type Y or N): " )
        if (user_choice.upper == 'Y'):
            continue
        else:
            userRepo = '-1'
            break

    createrepocmd = "salt " + choice + " cmd.run 'createrepo " + mount_point + "'"
    os.system(createrepocmd)
    print("Created repo metadata")
    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created at: " + mount_point)
      
def ubuntu(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point):
    print("Starting Ubuntu repo creation and mount...")
    # Start performing commands with salt and mounting
    os.system("fdisk -l")
    find_out = input("Would you like to create a partition for a device? (Y/N): ")
    if (find_out.upper == "Y"):
        parti = input("What device would you like to create a partition in?: ")
    make_dir = "salt " + choice + " cmd.run 'mkdir " + mount_point + "'"
    os.system(make_dir)
    try:
        os.system(fullmountpoint)
    except:
        print("Unexpected error occurred...")
    
    print("Successfully created directory")
    
    # Find the mirror.list file and change the base_path
    a_file = open("/etc/apt/mirror.list", "r")
    list_of_lines = a_file.readlines()
    list_of_lines[2] = "set base_path " + mount_point + "\n"
    # This reopens the copied file and writes what we need for it
    a_file = open("/etc/apt/mirror.list", "w")
    a_file.writelines(list_of_lines)
    a_file.close()

    # Pull down recent updates and store it in the created dir
    cmd1 = "salt " + choice + " cmd.run 'apt-mirror " + mount_point + "'"
    os.system(cmd1)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created. \n")

def centos_docker(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point):
    print("Starting CentOS repo creation and mount...")
    # Start performing commands with salt and mounting
    os.system("fdisk -l")
    find_out = input("Would you like to create a partition for a device? (Y/N): ")
    if (find_out.upper == "Y"):
        parti = input("What device would you like to create a partition in?: ")
    make_dir = "salt " + choice + " cmd.run 'mkdir " + mount_point + "'"
    os.system(make_dir)
    try:
        os.system(fullmountpoint)
    except:
        print("Unexpected error occurred...")
    
    print("Successfully created directory")
    
    # Pull down recent updates and store it in the created dir
    repocmd = "salt " + choice + " cmd.run 'repotrack --repoid=docker-ce --download_path=" + mount_point + "'"
    os.system(repocmd)
    print("Finished downloading packages from docker-ce at " + mount_point + "'")

    createrepocmd = "salt " + choice + " cmd.run 'createrepo " + mount_point + "'"
    os.system(createrepocmd)
    print("Created repo metadata")
    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created at: " + mount_point)

def ubuntu_docker(operatingsys, choice, fullmountpoint, fs_type, parti, mount_point):
    print("Starting Ubuntu repo creation and mount...")
    # Start performing commands with salt and mounting
    os.system("fdisk -l")
    find_out = input("Would you like to create a partition for a device? (Y/N): ")
    if (find_out.upper == "Y"):
        parti = input("What device would you like to create a partition in?: ")
    make_dir = "salt " + choice + " cmd.run 'mkdir " + mount_point + "'"
    os.system(make_dir)
    try:
        os.system(fullmountpoint)
    except:
        print("Unexpected error occurred...")
    
    print("Successfully created directory")
    
    # Find the mirror.list file and change the base_path
    os.system("mv /etc/apt/mirror.list /etc/apt/mirror.list.bak")
    a_file = open("/etc/apt/mirror.list", "r")
    list_of_lines = a_file.readlines()
    list_of_lines[2] = "set base_path " + mount_point + "\n"
    # This reopens the copied file and writes what we need for it
    a_file = open("/etc/apt/mirror.list", "w")
    a_file.writelines(list_of_lines)
    a_file.close()
    os.system("echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable' >> /etc/apt/mirror.list")

    # Pull down recent updates and store it in the created dir
    cmd1 = "salt " + choice + " cmd.run 'apt-mirror'"
    os.system(cmd1)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created. \n")
# As always, call the main function
if __name__ == '__main__':
    main()