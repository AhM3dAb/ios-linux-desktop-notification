const detect = require('detect-gender');

// promises
detect('amir').then(function (gender) {
  console.log(gender);
});
