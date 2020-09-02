const ewelink = require('ewelink-api');
const credentials = require('./credentials');

(async () => {
    const connection = new ewelink(credentials);

    console.log("Fetching your devices...");
    /* get all devices */
    const devices = await connection.getDevices();
    if (devices.hasOwnProperty('error') && devices.hasOwnProperty('msg')){
        console.error('Some error occurred: ' + devices.msg + " - " + devices.error)
        return
    }
    console.log("Your devices:");
    console.log("device id            | brand                | model                | created date                | mac                  |");
    console.log("---------------------|----------------------|----------------------|-----------------------------|----------------------|");
    devices.forEach(function (element) {
        console.log( element.deviceid.padEnd(20, ' ') + " | " + element.brandName.padEnd(20, ' ') + " | " + element.productModel.padEnd(20, ' ') + " | "  + element.createdAt.padEnd(27, ' ') + " | " + element.params.staMac.padEnd(20, ' ') + " | ");

    });

})();