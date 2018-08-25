/**
 * Copyright 2016-2018 IBM Corp. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var TJBot = require('tjbot');
var config = require('./config');

// obtain our credentials from config.js
var credentials = config.credentials;

// obtain user-specific config
var WORKSPACEID = config.workspaceId;

// these are the hardware capabilities that TJ needs for this recipe
var hardware = ['microphone', 'speaker', 'led', 'servo', 'camera'];
if (config.hasCamera == false) {
    hardware = ['microphone', 'speaker', 'led', 'servo'];
}

// set up TJBot's configuration
var tjConfig = {
    log: {
        level: 'verbose'
    },
    robot: {
        gender: 'female', // see TJBot.prototype.genders
        name: 'Lucy'
    },
    speak: {
        voice: 'en-US_AllisonVoice',
        speakerDeviceId: 'plughw:1,0'
    },
    see: {
        confidenceThreshold: {
            object: 0.5,
            text: 0.1
        },
        camera: {
            height: 720,
            width: 960,
            verticalFlip: true, // flips the image vertically, may need to set to 'true' if the camera is installed upside-down
            horizontalFlip: true // flips the image horizontally, should not need to be overridden
        }
    }
};

// instantiate our TJBot!
var tj = new TJBot(hardware, tjConfig, credentials);

// full list of colors that TJ recognizes, e.g. ['red', 'green', 'blue']
var tjColors = tj.shineColors();

// hash map to easily test if TJ understands a color, e.g. {'red': 1, 'green': $
var colors = {};
tjColors.forEach(function(color) {
    colors[color] = 1;
});

console.log("You can ask me to introduce myself or tell you a joke.");
console.log("Try saying, \"" + tj.configuration.robot.name + ", please introduce yourself\" or \"" + tj.configuration.robot.name + ", what can you do?\"");
console.log("You can also say, \"" + tj.configuration.robot.name + ", tell me a joke!\"");

console.log(">>> Start listening");

// listen for utterances with our attentionWord and send the result to
// the Assistant service

tj.listen(function(msg) {

   if (isTalkingToBot(msg)) {

	tj.pauseListening();
	var resumeWhenDone = true;

        // remove our name from the message
        var utterance = msg.toLowerCase().replace(tj.configuration.robot.name.toLowerCase(), "");
       
        // send to the assistant service
        tj.converse(WORKSPACEID, utterance, function(response) {
             // speak the result
            console.log("RESPONSE: %j", response);

            var intent = '';
            if (response.object.intents && response.object.intents[0])
                intent = response.object.intents[0].intent;
            console.log("INTENT: " + intent);

            var color = '';
            for(var i in response.object.entities) {
                var entity = response.object.entities[i];
                console.log("E: %j", entity);
                if (entity.entity == 'color') {
                    color = entity.value;
                }
            }

            if (intent == 'recognize' && config.hasCamera == false) {
               //no camera configured, we can not see anything
               response.description = "Sorry, but I think I am blind today.";
            }

            if (intent == 'insult') {
                //give an angry answer if we have been insulted  
                tj.shine('red');
                response.description = "<prosody pitch='-200Hz' rate='-10%'>" + response.description + "</prosody>"
            }
 
            tj.speak(response.description);

            if (intent == 'change_light' && color != '') {
                tj.shine(color);
            }
                  
            if (intent == 'goodbye') {
		tj.wave();
		tj.wave();
                setTimeout(goToBed, 4000);
            }

            if (intent == 'disco')
                setTimeout(discoParty, 2000);

            if (intent == 'hello') {
                tj.shine('blue');
		tj.wave();
		tj.wave();
            }

            if (intent == 'recognize' && config.hasCamera == true) {

                console.log("RECOGNIZE");

		resumeWhenDone = false;

		tj.see().then(function(result) {
                    //console.log("RECOGNIZE RESULT: %j", result);
		    var whatisee = '';
		    var score = 0;
		    var color = '';
		    var colorScore = 0;
                    for(var i in result) {
                         console.log("RECOGNIZE RESULT: %j", result[i]);
			 if (result[i].score > score && result[i].class.indexOf("color") < 0 && result[i].type_hierarchy) {
			     whatisee = result[i].class;
			     score = result[i].score;
			 }
			 if (result[i].class.indexOf("color") >= 0 && result[i].score > colorScore) {
			     color = result[i].class.replace("color", "").replace(" ","").trim();
     		             if (colors[color] == 1) {
			         colorScore = result[i].score;
                             }
			 }
		    }

                    console.log("SEE RESULT: " + whatisee);
                    //console.log("SEE COLOR: " + color);

		    if (whatisee)
		    	tj.speak("This is a " + whatisee);
		    else
			tj.speak("Sorry, I don't know what this is.");

		    if (colorScore > 0)
		    	tj.shine(color);

		    tj.resumeListening();
	   	    console.log(">>> Start listening");

		});
            }

   	    if (resumeWhenDone) {
  	        tj.resumeListening();
	        console.log(">>> Start listening");
	    }

        });
    }
});

function goToBed() {
    tj.shine('off');
    process.exit();
};

function discoParty() {
    for (i = 0; i < 30; i++) {
        setTimeout(function() {
            var randIdx = Math.floor(Math.random() * tjColors.length);
            var randColor = tjColors[randIdx];
            tj.shine(randColor);
        }, i * 250);
    }
};

// check to see if user is talking to Lucy
function isTalkingToBot(msg) {
    var containsName = msg.indexOf(tj.configuration.robot.name) >= 0
	|| msg.indexOf("you see") >= 0
	|| msg.indexOf("he knew") >= 0
	|| msg.indexOf("Lou") >= 0
	|| msg.indexOf("to you") >= 0
	|| msg.indexOf("does it") >= 0
	|| msg.indexOf("Rosie") >= 0
	|| msg.indexOf("you he") >= 0 
	|| msg.indexOf("who he") >= 0 
	|| msg.indexOf("no he") >= 0 
	|| msg.indexOf("movie") >= 0 
	|| msg.indexOf("Newfie") >= 0;
    return containsName;
};

