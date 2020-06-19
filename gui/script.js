var template, notificationsList = [],
    baseClass = 'Notification',
    listElement = document.getElementsByClassName(baseClass + 's__List')[0],
    addBtn = document.getElementsByClassName(baseClass + 's__addBtn')[0],
    removeBtn = document.getElementsByClassName(baseClass + 's__removeBtn')[0],
    notificationContainer = document.getElementsByClassName(baseClass + '__Container')[0],
    userName = 'Ahmed',
    id = 0,
    secondClick = false;
// notificationsList.push({
// 	name: 'Messenger',
// 	icon: 'https://cdn3.iconfinder.com/data/icons/social-network-30/512/social-04-512.png',
// 	time: 'Now',
// 	title: userName,
// 	content: 'Hey, are you okay? Just call me'
// })

template = (() => {
	let elm = document.getElementsByClassName('Notification')[0],
	    tmp = elm.cloneNode(true)
	tmp.classList.add(baseClass + '--Close')
	tmp.classList.add(baseClass + '--Optimize')

	elm.remove()

	listElement.innerHTML = ''

	return tmp
})()

function rnd (size) {
	return Number.parseInt((Math.random() * size))
}

function Notification (config = {}) {
	var element = template.cloneNode(true)
  element.classList.add('notification-id' + config.id)

	function handler (klass, attr, value, child) {
		var tmp = element.getElementsByClassName(baseClass + klass)[0]

		if (typeof child === 'number') {
			tmp = tmp.children[child]
		}

		if (attr === 'value') {
			return tmp.innerText = value
		}

		return tmp.setAttribute(attr, value)
	}

	handler('__Icon', 'src', config.icon, 0)
	handler('__Name', 'value', config.name)
	handler('__Time', 'value', config.time)
	handler('__Title', 'value', config.title)
	handler('__Content', 'value', config.content)

	return element
}

function addNotification (notification, callback) {
  $("."+removeBtn.className).show(500);
	listElement.insertAdjacentElement('afterBegin', notification)

	setTimeout(() => {
		notification.classList.remove(baseClass + '--Close')
		setTimeout(() => {
			notification.classList.remove(baseClass + '--Optimize')

			if (typeof callback === 'function') callback()

		}, 875)
	}, 25)
}

function removeNotification (notification, callback) {
	notification.classList.add(baseClass + '--Optimize')
	notification.classList.add(baseClass + '--Close')

	setTimeout(() => {
		notification.remove()

		if (typeof callback === 'function') callback()
	}, 875)

}

function removeLastItem () {
	let notification, tmp

	tmp = document.getElementsByClassName(baseClass)

	for (let i = 0; i < tmp.length; i++) {
		if (!tmp[i].classList.contains(baseClass + '--Close')) {
			notification = tmp[i]
			break
		}
	}

	removeNotification(notification, () => {
		if (!listElement.children.length) {
			listElement.innerHTML = ''
		}
    if(listElement.children.length==0) {
      $("."+removeBtn.className).hide(100);
    }
	})
}

function removeItem (id) {
  if(listElement.children.length==0) {
    return;
  }
	let notification, tmp

	tmp = document.getElementsByClassName(baseClass)

	for (let i = 0; i < tmp.length; i++) {
		if (tmp[i].classList.contains('notification-id' + id)) {
			notification = tmp[i]
			break
		}
	}

	removeNotification(notification, () => {
    for (let i = 0; i < listElement.children.length; i++) {
		if (listElement.children[i].className.split(" ")[1] == 'notification-id' + id) {
			listElement.innerHTML = ''
		}
  }
  if(listElement.children.length==0) {
    $("."+removeBtn.className).hide(100);
  }
	})
}

function removeAllItem () {
	let notification, tmp

	tmp = document.getElementsByClassName(baseClass)

	for (let i = 0; i < tmp.length; i++) {

      removeNotification(tmp[i], () => {
        if (!listElement.children.length) {
          listElement.innerHTML = ''
        }
        if(listElement.children.length==0) {
          $("."+removeBtn.className).hide(500);
        }
      })

	}


}




$('body').on('click', 'div.Notification__Container', function() {
  id = $(this).parent().prop('className').split(" ")[1].match(/\d+/g)[0];
  removeItem(id);
});

addBtn.addEventListener('click', () => {
	addNotification(Notification(notificationsList[rnd(notificationsList.length)]))
})

document.getElementsByClassName("screen")[0].addEventListener('click', () => {
    	if(removeBtn.innerText == "Clear"){
        removeBtn.innerText = "x";
      }
  })


removeBtn.addEventListener('click', function(event) {
  event.stopPropagation();
	if(removeBtn.innerText == "x"){
    $("."+removeBtn.className).css("width", "31px");
    removeBtn.innerText = "Clear";
  }
  else {

    $("."+removeBtn.className).hide(500);
    $("."+removeBtn.className).css("width", "20px");
    removeBtn.innerText = "x";
    removeAllItem();

  }
})

{
	let c = 1, end = 20, operation = 'add'

	setInterval(() => {
		return

		if (operation === 'add') {
			addNotification(Notification(notificationsList[rnd(notificationsList.length)]))
		} else if (operation === 'remove') {
			removeLastItem()
		}

		if (c === 0) {
			operation = 'add'
		} else if (c === end) {
			operation = 'remove'
		}

		if (operation === 'add') {
			c++
		} else if (operation === 'remove') {
			c--
		}
	}, 875 / 6)
}
