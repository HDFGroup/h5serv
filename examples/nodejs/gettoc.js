var http = require('http');
var options = {
  host: 'data.hdfgroup.org',
  port: 7253,
  path: '/'
};
var callback = function(response) {
  var str = '';

  //another chunk of data has been recieved, so append it to `str`
  response.on('data', function (chunk) {
    str += chunk;
  });

  //the whole response has been recieved, so we just print it out here
  response.on('end', function () {
    var rsp = JSON.parse(str);
    console.log(JSON.stringify(rsp, null, 4));
  });
}

http.request(options, callback).end();
