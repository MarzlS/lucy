
# Lucy Conversation
> Chat with Lucy!

This recipe is based on [IBM TJBot](https://github.com/ibmtjbot/tjbot) and uses the [Watson Assistant](https://www.ibm.com/watson/services/conversation/) and other Watson services to turn Lucy into a chatting robot.

Some possible things to tell her:

* "Lucy how are you?" - To get to know about her feelings.
* "Hello Lucy" - Lucy will say hello and waves her arm.
* "Lucy turn the light to red" - Switch the LED to the given color.
* "Lucy start disco party" - Rotate through all LED colors.
* "What time is it, Lucy?" - Lucy tells you the time.
* "Lucy what is this?" - Lucy takes a photo and tries to guess what she sees.
* "Lucy go to bed" - Ends the conversation


## Hardware
This recipe requires a TJBot with a microphone, a speaker, a LED, a servo arm and a camera.


## Build and Run

### Bootstrap
First, make sure you have configured your Raspberry Pi for Lucy by running the [bootstrap script](https://github.com/MarzlS/lucy/blob/master/bootstrap/bootstrap.sh).

### Testing and Troubleshooting
Testing and troublehooting instructions can be found here: [Troubleshooting.md](Troubleshooting.md)

### Dependencies and configuration

Next, go to the `lucy` folder and install the dependencies.

    $ cd lucy
    $ npm install

Import the `workspace-lucy.json` file into the Watson Assistant service and note the workspace ID.

Create instances of all the required Watson services and note the authentication credentials.

Make a copy the default configuration file and update it with the Watson service credentials and the conversation workspace ID.

    $ cp config.default.js config.js
    $ nano config.js
    <enter your service credentials and the conversation workspace ID in the specified places>

### Run!

    sudo node lucy.js

> Note the `sudo` command. Root user access is required to run TJBot recipes.

# Watson Services
- [Watson Assistant](https://www.ibm.com/watson/services/conversation/)
- [Watson Speech to Text](https://www.ibm.com/watson/services/speech-to-text/)
- [Watson Text to Speech](https://www.ibm.com/watson/services/text-to-speech/)
- [Watson Visual Recognition](https://www.ibm.com/watson/services/visual-recognition/)

# License
This project is licensed under Apache 2.0. Full license text is available in [LICENSE](LICENSE).

