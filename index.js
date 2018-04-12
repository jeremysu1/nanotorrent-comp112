
var express = require('express');
var app = express();

app.set('port', (process.env.PORT || 5000));

app.use(express.static(__dirname + '/public'));

// views is directory for all template files
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');


var tracker = {};
tracker.declaration = ["127.0.0.1:9000", "192.68.103.2:8000"];
tracker.movie = ["130.64.155.2:3000"];

app.get('/', function(request, response) {
  response.send(tracker);
});

app.post('/join', function (request, response) {
  var client_ip = request.body;
  response.send(request);
})

app.listen(app.get('port'), function() {
  console.log('Node app is running on port', app.get('port'));
});
