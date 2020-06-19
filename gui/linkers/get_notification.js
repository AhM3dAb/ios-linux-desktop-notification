function get_notification(){

const cp = require('child_process');
const ipcRenderer = require('electron').ipcRenderer
const child = cp.spawn('python3',["../engine/python/ios-linux.py"]);
ipcRenderer.send('pid-message', child.pid);
$('body').on('click', 'div.Notification__Container', function() {
  id = $(this).parent().prop('className').split(" ")[1].match(/\d+/g)[0];
  removeJson = JSON.stringify({"notificationID":id, "action":"remove"});
  removeItem(id);
  child.stdin.write(removeJson + "\n");
});
child.stdout.on('data', data => {
$(document).ready(function(){
  process.stdout.write(data);
  try{
    var obj =  JSON.parse(data);
    if(obj.event_id=="remove"){
      removeItem (parseInt(obj.notification_id));
      //child.stdin.write("remove:" + obj.notification_id + "\n");
    }
    else if(obj[1].data){
    var today = new Date();
    var h = today.getHours();
    var m = today.getMinutes();
    notif = {
      id: obj[0],
      name: obj[1].data[0].app_name,
      icon: '/tmp/'+obj[1].data[0].app_icon_name,
      time: h+':'+m,
      title: obj[1].data[0].title,
      content: obj[1].data[0].message
    };
    addNotification(Notification(notif));
  }
}
    catch(err) {
   console.log(err);
 }

});

});
}
