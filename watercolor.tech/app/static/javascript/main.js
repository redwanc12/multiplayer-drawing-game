var userList = document.getElementById("userList");
var chatbox = document.getElementById("chat");
const canvas = document.getElementById("canvas");
const canvasDiv = document.getElementById("canvasDiv");
const ctx = canvas.getContext('2d');
const timeLeftText = document.getElementById('timeLeft');
var startBtn = document.getElementById("startBtn");
var username = "";
var currDrawer;
var currWord;
var timeLeft = 30;
var timer;
var socket;
var flag = false, prevX = 0, prevY = 0;

$(document).ready(function(){
    ctx.strokeStyle = "black";
    ctx.lineWidth = 10;
    ctx.globalAlpha = 0.8;
    // ctx.lineJoin = 'round';
    // ctx.lineCap = 'round';
    canvas.style.webkitFilter = "blur(1px)";

    canvas.addEventListener("mousemove", function (e) {
        findxy('move', e);
    }, false);
    canvas.addEventListener("mousedown", function (e) {
        findxy('down', e)
    }, false);
    canvas.addEventListener("mouseup", function (e) {
        findxy('up', e)
    }, false);
    canvas.addEventListener("mouseout", function (e) {
        findxy('out', e)
    }, false);

    startBtn.onclick = function startGuess(){
        if(currDrawer == username){
            var word = prompt("What will you be drawing?");
            const banned_words = ["", "name", "room", "userID", "color"]
            if(word != null && !(word in banned_words)){
                socket.emit('startGame', word);
            }
            return;
        }
        else{
            alert('only hosts can start game');
        }
    }

    socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function() {
        socket.emit('joined', {});
        socket.emit('getInfo');
    });
    socket.on('message', function(data) {

        if(data.special){
            const user_message = `<span style="color: ${data.color}">${data.name} ${data.msg} </span> <br>`;
            chatbox.innerHTML += user_message;
        }
        else{
            const user_message = `<span style="color: ${data.color}">${data.name}:</span>`;
            chatbox.innerHTML += user_message;
            chatbox.innerText += data.msg;
            chatbox.innerHTML += "<br>";
        }
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    socket.on('getInfo', (data) => {
        userList.innerHTML = "";
        const users = data["Users"]
        for(each in users){
            var li = document.createElement("li");
            var name_span = document.createElement('span');
            name_span.className = "statusBoxUsername";
            name_span.innerHTML = `${users[each][0]} <br>`;
            li.appendChild(name_span);

            var points_span = document.createElement('span');
            points_span.className = "statusBoxPoints";
            points_span.innerHTML = `${users[each][1]} PTS`;
            li.appendChild(points_span);
            userList.appendChild(li);
        }
        currDrawer = data['current_drawer'];
        document.getElementById('drawer').innerHTML = currDrawer;

        //TODO: pass username to JS when you create user. This is ghetto.
        if(username == ""){
            username = data["username"];
        }

    });
    socket.on('drawCanvas', (data) => {
        draw(data['x'], data['y']);
    });
    socket.on('updateColor', (data) => {
        ctx.strokeStyle = data;
    });
    socket.on('updatePrev', (data) =>{
        prevX = data['x'];
        prevY = data['y'];
    });
    socket.on('updateBrushSize', (data) =>{
        ctx.lineWidth = data;
    });
    socket.on('clearCanvas', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
    socket.on('startGame', (word)=> {
        timer = setInterval(startTiner, 1000);
        startBtn.style.display = 'none';
        currWord = word;
    })
    socket.on('nextRound', () => {
        if(currDrawer == username){
            guess();
        }
    });
    socket.on('resetTimer', () => {
        timeLeft = 30;
        clearInterval(timer);
    });
    socket.on('endGame', (winner) =>{
        alert(`game ended! ${winner} has won.`);
    })
    $('#text').keypress(function(e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            const data = {
                'msg':text,
                'timeLeft':timeLeft
            };
            socket.emit('text', data);
        }
    });
    function startTiner() {
        if(timeLeft <= 0){
            if (currDrawer == username) {
                socket.emit('nextRound');
            }
            return;
        }
        else{
            timeLeft-=1;
            timeLeftText.innerHTML = timeLeft;
        }
    }
    function draw(newX, newY) {
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(newX, newY);
        ctx.stroke();
        ctx.closePath();
        prevX = newX;
        prevY = newY;
    }
        
    function findxy(res, e) {
        if(currDrawer != username){
            return;
        }
        if (res == 'down') {  
            data = {'x': e.clientX - canvas.offsetLeft - canvasDiv.offsetLeft, 'y':e.clientY - canvas.offsetTop - canvasDiv.offsetTop};
            socket.emit("updatePrev", data); 
            flag = true;
        }
        if (res == 'up' || res == "out") {
            flag = false;
        }
        if (res == 'move') {
            if (flag) {
                data = {'x': e.clientX - canvas.offsetLeft - canvasDiv.offsetLeft, 'y':e.clientY - canvas.offsetTop - canvasDiv.offsetTop};
                socket.emit("drawCanvas", data);
            }
        }
    }
    function guess(){
        var word = prompt("What will you be drawing?");
        const banned_words = ["", "name", "room", "userID", "color"]
        if(word != null && !(word in banned_words)){
            socket.emit('startGame', word);
        }
    }
});