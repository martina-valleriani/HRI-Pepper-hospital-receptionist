var ip=window.location.hostname;
if (ip=='')
    ip='127.0.0.1';
var port = 9100;

console.log("Trying connection...")
wsrobot_init(ip,port);

function hello() {
    console.log("runnig interaction...");
    codews.send("im.robot.say('hello')\n");
}