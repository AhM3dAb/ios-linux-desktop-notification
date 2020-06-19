// Modules to control application life and create native browser window
const {app, BrowserWindow, Menu, Tray} = require('electron');
var ps = require('ps-node');
const ipc = require('electron').ipcMain;
const path = require('path');

let tray = null;
let mainWindow = null;
let pids = [];
function createWindow () {
  // Create the browser window.
   mainWindow = new BrowserWindow({
    width: 300,
    height: 620,
    resizable: false,
    transparent: true,
    frame: false,
    webPreferences: {
    nodeIntegration: true,
    preload: path.join(__dirname, 'preload.js')
    }
  })

  // and load the index.html of the app.
  mainWindow.loadFile('index.html')
  mainWindow.setMenuBarVisibility(true)
  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', () => {
  setTimeout(createWindow, 400);
  tray = new Tray("/home/ahmed/Desktop/iphonenotification/icons/setting.jpg");
  const menu = Menu.buildFromTemplate([
    {
      label: 'Quit',
      click() {
        pids.forEach(function(pid) {
          // A simple pid lookup
          ps.kill( pid, function( err ) {
              if (err) {
                  throw new Error( err );
              }
              else {
                  console.log( 'Process %s has been killed!', pid );
              }
          });
        });
        app.quit();
      }
    },
    {
      label: 'Minimize',
      click() { mainWindow.hide(); }
    },
    {
      label: 'Restore',
      click() { mainWindow.restore(); }
    }
  ]);

  tray.setToolTip('Clipmaster');
  tray.setContextMenu(menu);
});

//app.whenReady().then(createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})
ipc.on('pid-message', function(event, arg) {
  console.log('Main:', arg);
  pids.push(arg);
});
// App close handler
app.on('before-quit', function() {
  pids.forEach(function(pid) {
    // A simple pid lookup
    ps.kill( pid, function( err ) {
        if (err) {
            throw new Error( err );
        }
        else {
            console.log( 'Process %s has been killed!', pid );
        }
    });
  });
});
// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
