
var express = require('express');
var bodyParser = require("body-parser");
var app = express();


app.set('port', (process.env.PORT || 5000));

app.use(express.static(__dirname + '/public'));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// views is directory for all template files
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');


var tracker = {};

app.get('/', function(request, response) {
  response.send(tracker);
});

function exists_in_list(name, list) {
	for (var i = 0; i < list.length; i++) {
		if (list[i] == name) {
			return true;
		}
	}
	return false;
}

// curl -H "Content-Type: application/json" -X POST -d '{"filename":"test.txt","ip":"130.64.155.2:3000"}'  localhost:5000/join
app.post('/join', function (request, response) {
  var data = request.body;
  if (data.filename in tracker) {
  	if (!exists_in_list(data.ip, tracker[data.filename])) {
  		tracker[data.filename].push(data.ip)
  	}
  } 
  else {
  	tracker[data.filename] = []
  	tracker[data.filename].push(data.ip)
  }
  response.send(tracker);
})

app.listen(app.get('port'), function() {
  console.log('Node app is running on port', app.get('port'));
});
