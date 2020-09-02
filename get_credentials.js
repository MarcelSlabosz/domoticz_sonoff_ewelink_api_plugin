const ewelink = require('ewelink-api');
const credentials = require('./credentials');

(async () => {

    const connection = new ewelink(credentials);

    console.log("Obtaining credentials...");
    const auth = await connection.getCredentials();
    if (auth.hasOwnProperty('error') && auth.hasOwnProperty('msg')){
        console.error('Some error occurred: ' + auth.msg + " : " + auth.error)
        return
    }
    console.log('Application token: ', auth.at);
    console.log('Application key: ', auth.user.apikey);
    console.log('Region: ', auth.region);

})();