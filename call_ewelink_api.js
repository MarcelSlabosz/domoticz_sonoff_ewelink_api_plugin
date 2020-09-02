const ewelink = require('ewelink-api');

function parse_args(argument_list){
	if (argument_list.length != 7){
		throw "Invalid arguments lenght!";
	}
	return {
		at: argument_list[2],    
		apiKey: argument_list[3],
		region: argument_list[4],    
		device: argument_list[5],    
		action: argument_list[6],    
	}
}

(async () => {

  // console.debug(process.argv);

  let my_args = parse_args(process.argv);
  //console.debug(my_args);

  const connection = new ewelink({
    at: my_args['at'],
    apiKey: my_args['apiKey'],
    region: my_args['region']
  });

  /* device actions */
  switch(my_args['action']){
	 case 'on':
		const status_on = await connection.setDevicePowerState(my_args['device'], 'on');
  		console.log(my_args['device'], JSON.stringify(status_on));
		break;
	case 'off':
		const status_off = await connection.setDevicePowerState(my_args['device'], 'off');
  		console.log(my_args['device'], JSON.stringify(status_off));
		break;
	case 'status':
		const status_status = await connection.getDevicePowerState(my_args['device']);
  		console.log(my_args['device'], JSON.stringify(status_status));
		break;
	default:
		console.error('Operation: ', my_args['action'], ' not supported!');
  }

})();
