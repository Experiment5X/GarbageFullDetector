express = require('express');
fs = require('fs');
bodyParser = require('body-parser');
const app = express();
const pug = require('pug');

app.use(express.static('/home/pi/Developer/GarbageSettingsService/public'));
app.use(bodyParser.urlencoded({ extended: true }));


function updateLatestImage() {
    var imageDirectory = '/home/pi/Developer/GarbageDetector/captured_images/';
    var files = fs.readdirSync(imageDirectory);

    if (files.length > 0) {
        var fileName = files[files.length - 1];
        console.log(fileName);
        var unixTimestampStr = parseInt(fileName.replace('.png', ''));
        console.log(unixTimestampStr);
        var imageTimestamp = new Date(unixTimestampStr * 1000);
        console.log(imageTimestamp);
        var imageTimestampFormatted = imageTimestamp.toLocaleString('en-US');
        console.log(imageTimestampFormatted);

        var newestImage = imageDirectory + fileName;
        fs.createReadStream(newestImage).pipe(fs.createWriteStream('/home/pi/Developer/GarbageSettingsService/public/images/garbage_can.png'));
        console.log('Copied newest image: ' + newestImage);

        return imageTimestampFormatted;
    } else {
        return null;
    }
}

/**
 * Read settings from the disk and send the pug file with them 
 * @param {*} response The response object from the request
 */
function sendSettings(response) {
    fs.readFile('/opt/GarbageDetector/settings.store.json', 'utf-8', function(error, fileContents) {
        if (error) {
            console.log('Error: ' + error);
            response.send(pug.renderFile('/home/pi/Developer/GarbageSettingsService/settings.pug'));
        } else {
            var settings = JSON.parse(fileContents);
            settings.timeToNotify = parseInt(settings.timeToNotify);

            settings.imageTimestamp = updateLatestImage();

            console.log('Read Settings: ');
            console.log(settings);
            response.send(pug.renderFile('/home/pi/Developer/GarbageSettingsService/settings.pug', settings));
        }
    });
}

app.get('/', function (request, response) {
    sendSettings(response);
});

app.post('/', function (request, response) {
    fs.readFile('/opt/GarbageDetector/settings.store.json', 'utf-8', function(error, fileContents) {
        if (error) {
            console.log('Error: ' + error);
            response.send(pug.renderFile('settings.pug'));
        } else {
            var old_settings = JSON.parse(fileContents);
            var settings = request.body;

            settings['isGarbageFull'] = old_settings['isGarbageFull'];
            var settingsStr = JSON.stringify(settings);

            fs.writeFile('/opt/GarbageDetector/settings.store.json', settingsStr, function(error) {
                if (error) {
                    console.log('Error writing settings: ');
                    console.log(settings);
                } else {
                }

                sendSettings(response);
            });
        }
    });

});

app.get('/updateGarbageImage', function (request, response) {
    response.send(updateLatestImage());
});

app.listen(8000, () => console.log('Listening on 8000...'));