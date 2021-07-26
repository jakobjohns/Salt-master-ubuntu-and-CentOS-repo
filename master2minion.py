#!/usr/bin/env python3

import os

# main is used just for choice selection 
def main():

    minionCheckIfUP()

def minionCheckIfUP():
     # Quick check to see if a minion returns true with a ping
    operatingsys = input("What is the name of the distribution you would like to create a repo in? (CentOS, Ubuntu, CentOS-Docker, Ubuntu-Docker): ")
    salt_ping = "salt '*' test.ping"
    os.system(salt_ping)
    choice = input("What is the name of the machine? (Spell it exactly, choices listed above, true means the machine is up and running, do not include colon.):  ")
    if (operatingsys.upper() == "CENTOS"):
        centos(choice)
    elif (operatingsys.upper() == "UBUNTU"):
        ubuntu(choice)
    elif (operatingsys.upper() == "CENTOS-DOCKER"):
        centos_docker(choice)
    elif (operatingsys.upper() == "UBUNTU-DOCKER"):
        ubuntu_docker(choice)
    else:
        print("Invalid option...")
        exit()

def centos(choice):
    print("Starting CentOS repo creation...")
    
    file_location = input("What is the path of the file you would like to pull from: ")
    # Pull down recent updates and store it in the created dir
    userRepo = input("What repo would you like to pull from?: ")
    while (userRepo != '-1'):
        repocmd = "salt " + choice + " cmd.run 'reposync --repoid=" + userRepo + " --download_path=" + file_location + "'"
        os.system(repocmd)
        print("Finished downloading packages from " + userRepo + " at " + file_location + "'")
        user_choice = input("Would you like to do another? (type Y or N): " )
        if (user_choice.upper == 'Y'):
            continue
        else:
            userRepo = '-1'
            break

    createrepocmd = "salt " + choice + " cmd.run 'createrepo " + file_location + "'"
    os.system(createrepocmd)
    print("Created repo metadata")
    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created at: " + file_location)
      
def ubuntu(choice):
    print("Starting Ubuntu repo creation...")
    
    # Get location for storing the repo
    file_location = input("What is the path of the file you would like to pull from: ")
    
    # Find the mirror.list file and change the base_path
    make_bak = "salt " + choice + " cmd.run 'mv /etc/apt/mirror.list /etc/apt/mirror.list.bak'"
    set_base_path = "salt " + choice + " cmd.run 'echo 'set base_path " + file_location + "'" + " >> /etc/apt/mirror.list'"

    os.system(make_bak)
    os.system(set_base_path)

    # Pull down recent updates and store it in the created dir
    cmd1 = "salt " + choice + " cmd.run 'apt-mirror' "
    os.system(cmd1)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created. \n")

def centos_docker(choice):
    print("Starting CentOS repo creation...")
    
    # Get location for storing the repo
    file_location = input("What is the path of the file you would like to pull from: ")
    
    # Pull down recent updates and store it in the created dir
    repocmd = "salt " + choice + " cmd.run 'repotrack --repoid=docker-ce --download_path=" + file_location + "'"
    os.system(repocmd)
    print("Finished downloading packages from docker-ce at " + file_location + "'")

    createrepocmd = "salt " + choice + " cmd.run 'createrepo " + file_location + "'"
    os.system(createrepocmd)
    print("Created repo metadata")
    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created at: " + file_location)

def ubuntu_docker(choice):
    print("Starting Ubuntu repo creation...")
    
    file_location = input("What is the path of the file you would like to pull from: ")
    
    # Find the mirror.list file and change the base_path
    make_bak = "salt " + choice + " cmd.run 'mv /etc/apt/mirror.list /etc/apt/mirror.list.bak'"
    set_base_path = "salt " + choice + " cmd.run 'echo 'set base_path " + file_location + "'" + " >> /etc/apt/mirror.list'"
    docker_repo_echo = "salt " + choice + " cmd.run 'echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable' >> /etc/apt/mirror.list'"
    os.system(make_bak)
    os.system(set_base_path)
    os.system(docker_repo_echo)

    # Pull down recent updates and store it in the created dir
    cmd1 = "salt " + choice + " cmd.run 'apt-mirror'"
    os.system(cmd1)

    # Display to the user that everything should be good to go (I hope)
    print("Local repo has been created. \n")

# As always, call the main function
if __name__ == '__main__':
    main()