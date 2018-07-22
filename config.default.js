/*
* User-specific configuration
* IMPORTANT NOTES:
*  Please ensure you do not interchange your username and password.
*  Your username is the longer value: 36 digits, including hyphens
*  Your password is the smaller value: 12 characters
*/

// replace with the workspace identifier of your Watson Assistant workspace
exports.workspaceId = ''; 

// Set this to false if your TJBot does not have a camera.
exports.hasCamera = true;

// Create the credentials object for export
exports.credentials = {};

// Watson Assistant Service Credentials
// https://www.ibm.com/watson/services/conversation/
exports.credentials.conversation = {
	username: '',
	password: ''
};

// Watson Speech to Text Service Credentials
// https://www.ibm.com/watson/services/speech-to-text/
exports.credentials.speech_to_text = {
	username: '',
	password: ''
};


// Watson Text to Speech Service Credentials
// https://www.ibm.com/watson/services/text-to-speech/
exports.credentials.text_to_speech = {
	username: '',
	password: ''
};


// Watson Visual Recognition Service Credentials
// https://www.ibm.com/watson/services/visual-recognition/
exports.credentials.visual_recognition = {
	api_key: '',
	iam_apikey: ''
};