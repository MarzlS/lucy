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
var i18n = require('./i18n');

// obtain our credentials from config.js
var credentials = config.credentials;

// obtain user-specific config
var WORKSPACEID = config.workspaceId;

// these are the hardware capabilities that this recipe needs
var hardware = ['microphone', 'speaker', 'led', 'servo', 'camera'];
if (config.hasCamera == false) {
    hardware = ['microphone', 'speaker', 'led', 'servo'];
}

// set up the bot configuration
var tjConfig = config.tjConfig;

// instantiate our TJBot
var tj = new TJBot(hardware, tjConfig, credentials);

// full list of colors that the bot recognizes, e.g. ['red', 'green', 'blue']
var tjColors = tj.shineColors();

// hash map to easily test if TJ understands a color, e.g. {'red': 1, 'blue': 1, ...}
var colors = {};
tjColors.forEach(function(color) {
    colors[color] = 1;
});

console.log(i18n.console.welcome.replace(/%name%/gi, tj.configuration.robot.name));
console.log(i18n.console.info1.replace(/%name%/gi, tj.configuration.robot.name));
console.log(i18n.console.info2.replace(/%name%/gi, tj.configuration.robot.name));

console.log(i18n.console.listening);

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
               response.description = i18n.responses.nocamera;
            }

            if (intent == 'insult') {
                //give an angry answer if we have been insulted  
                tj.shine('red');
                response.description = "<prosody pitch='-200Hz' rate='-10%'>" + response.description + "</prosody>"
            }
 
            tj.speak(response.description);

            if (intent == 'change_light' && color != '') {
                var tjColor = i18n.color[color];
                if (tjColor) {
                    tj.shine(tjColor);
                } else {
                    console.log("Color not in translation: " + color);
                }
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
		    	tj.speak(i18n.responses.whatisee + whatisee);
		    else
			tj.speak(i18n.responses.noidea);

		    if (colorScore > 0)
		    	tj.shine(color);

		    tj.resumeListening();
	   	    console.log(i18n.console.listening);

		});
            }

   	    if (resumeWhenDone) {
  	        tj.resumeListening();
	        console.log(i18n.console.listening);
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

// check to see if user is talking to bot
function isTalkingToBot(msg) {
    var test = msg.toLowerCase();
    for (var i in config.nameVariants) {
        var value = config.nameVariants[i];
        if (test.indexOf(value.toLowerCase()) >= 0)
            return true;
    };
    return false;
};

