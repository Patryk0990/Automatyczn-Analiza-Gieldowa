var sidebar = document.getElementById("sidebar-collapse")
var sidebar_collapse = document.getElementById("sidebar-collapse-button")

function onResize() {
    // apply dynamic padding at the top/left of the body according to the fixed navbar height/width
    var width = (window.innerWidth > 0) ? window.innerWidth : screen.width
    if (width > 768) {
        document.getElementsByClassName("container-fluid")[1].style.marginLeft = document.getElementsByClassName("sidebar")[0].offsetWidth+'px'
        document.getElementsByClassName("container-fluid")[1].style.marginTop = 0
        document.getElementById("sidebar-collapse").style.paddingTop = 0
        if (sidebar.classList.contains("collapse")) {
            sidebar.classList.remove("collapse")
        }
        sidebar_collapse.style.display = "none"
    }
    else {
        document.getElementsByClassName("container-fluid")[1].style.marginLeft = 0
        document.getElementsByClassName("container-fluid")[1].style.marginTop = (sidebar_collapse.offsetHeight)+'px'
        document.getElementById("sidebar-collapse").style.paddingTop = (sidebar_collapse.offsetHeight)+'px'
        if (!sidebar.classList.contains("collapse")) {
            sidebar.classList.add("collapse")
        }
        sidebar_collapse.style.display = "flex"
    }

};

function getCookie(cname) {
    var cookies = document.cookie.split(';');
    for(var i = 0; i < cookies.length; i++) {
        var c = cookies[i].split("=")
        if (c[0] == cname) {
            return c[1]
        }
    }
    return "";
}

window.addEventListener('resize', onResize);
document.addEventListener("DOMContentLoaded", (event) => {
    onResize();
    onResize();
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});

var settings = {}
var old_settings = {}

var save_settings_button = document.getElementById("save_settings")
var update_stocks_button = document.getElementById("update_stocks")
var settings_message = document.getElementById("settings-message")

document.querySelectorAll('.settings-option').forEach(item => {
    item.addEventListener('click', event => {
        if (!item.classList.contains('active')) {
        
            let item_active = item.parentElement.querySelector(".active")

            if (!(item.parentElement.id in old_settings)) {
                old_settings[item.parentElement.id] = item_active.dataset.value
            }
            settings[item.parentElement.id] = item.dataset.value
            if (settings[item.parentElement.id] == old_settings[item.parentElement.id]) {
                delete settings[item.parentElement.id]
            }

            switch (item.parentElement.id) {
                case 'dark-mode':
                        document.body.classList.toggle(item.parentElement.id)
                    break;
                default:
                        document.body.classList.remove(item.parentElement.id + "-" + item_active.dataset.value)
                        if (item.parentElement.id in settings) {
                            document.body.classList.add(item.parentElement.id + "-" + settings[item.parentElement.id])
                        }
                        else {
                            document.body.classList.add(item.parentElement.id + "-" + old_settings[item.parentElement.id])
                        }
                    break;
            }

            item_active.classList.remove("active")
            item.classList.add("active")

        }

        if (Object.keys(settings).length > 0) {
            save_settings_button.style.display = "block"
            save_settings_button.parentElement.style.display = "flex"

            let link_parts = save_settings_button.getAttribute('href').split('?')
            let new_link = link_parts[0] + '?'
            let settings_keys = Object.keys(settings)
            new_link += '&' + settings_keys[0].replace('-', '_') + '=' + settings[settings_keys[0]]
            for(let i = 1; i < settings_keys.length; i++){
                new_link += '&' + settings_keys[i].replace('-', '_') + '=' + settings[settings_keys[i]]
            }
            save_settings_button.setAttribute('href', new_link)
        }
        else {
            save_settings_button.style.display = "none"
            save_settings_button.parentNode.style.display = "none"

            let link = save_settings_button.getAttribute('href').split('?')
            save_settings_button.setAttribute('href', link[0]+'?')
        }
    })
  })

function checkInputValue(e) {
    if(e.value != ""){
        if(parseInt(e.value) < parseInt(e.min)){
            e.value = e.min
        }
        if(parseInt(e.value) > parseInt(e.max)){
            e.value = e.max
        }
    }
}