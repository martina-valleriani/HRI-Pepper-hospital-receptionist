# HRI-Pepper-hospital-receptionist
by Pietro Nardelli and Martina Valleriani


# Project Description
This project is developed for the course of "Human-Robot Interaction" held by professor Luca Iocchi at La Sapienza, University of Rome, Italy.

The focus is on the interaction between Pepper robot as receptionist and the patients of a hospital. The robot has the goal to receive and welcome patients by handling the appointments and admission services, besides by giving general information. The patients can interact with the robot by means of speech or using the Pepper's built-in tablet and have to show an identification QR code in order to book a medical examination or to be admitted to a visit. Thanks to this code, Pepper can manage and personalise the communication and the interaction with the user.
In order to develop this application, we make use of the NAOqi framework and MODIM software.

# Instructions to launch the application
1. Follow the instructions in the repository https://bitbucket.org/iocchi/hri_software/src/master/ choosing option with Docker.

2. Modify the Dockerfile in the docker folder (*$HOME/src/hri_software/docker*) adding the following line:

    `RUN pip install opencv-python==4.2.0.32`
    
   to install OpenCV.

3. Put all the repository inside your local *playground* folder (*$HOME/playground*), except the files inside the *GUI_materials* folder.
   Copy the files inside the *GUI_materials* folder and paste into your local *GUI* folder (*$HOME/src/Pepper/pepper_tools/modim/src/GUI*).

   Notice: You can manually modify the cvs file about the appointments (*HRI_DB_appointments.csv*) in order to check if someone has a medical visit for the current date.
   
4. Open a terminal and launch the following commands:

    `cd $HOME/src/hri_software/docker`
    
    `./build.bash`
    
    `./run.bash`
    
    `cd $HOME/src/Pepper/pepper_tools/modim/docker`
    
    `./run_nginx.bash`
    
5. Then use this command to enter in the robot:
    
    `docker exec -it pepperhri tmux`

6. Inside the robot, launch these commands:
    
    `cd /opt/Aldebaran/naoqi-sdk-2.5.5.5-linux64`
    
    `./naoqi`
    
    then press `Ctrl-b c` to create a new tmux window.

7. Inside the just opened tmux window, use the following commands:
    
    `export MODIM_HOME=$HOME/src/pepper_tools/modim`
    
    `cd $MODIM_HOME/src/GUI`
    
    `python2 ws_server.py -robot pepper`
 
8. Open the browser and go to http://localhost/HRI-Pepper-hospital-receptionist/workspace/index.html .
    
9. Open another terminal using `docker exec -it pepperhri tmux` and follow these instructions:
    
    `export MODIM_HOME=$HOME/src/pepper_tools/modim`
    
    `cd playground/HRI-Pepper-hospital-receptionist/workspace/scripts`
    
    and finally `python2 main.py` to start the application.

10. Open another terminal using `docker exec -it pepperhri tmux` and use this command:
    
    `python $HOME/src/pepper_tools/sonar/sonar_sim.py --sensor SonarFront --value 1.3`
    
    with a value lower than 2.0, so that Pepper can detect the presence of a person and the interaction can start.
