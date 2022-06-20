var register_form = document.getElementById("register-form")
var login_form = document.getElementById("login-form")
var forms = document.getElementsByClassName("forms")[0]

function changeForm() {

    if (register_form.style.display == 'none') {
        forms.style.left = "-50vw"
        setTimeout(() => {
            forms.style.display = "none"
            forms.style.left = "100vw"
            forms.style.clipPath = "polygon(10% 0, 100% 0, 100% 100%, 0 100%)"

            login_form.style.display = "none"
            register_form.style.display = "flex"
            setTimeout(() => {
                forms.style.display = "flex"
                setTimeout(() => {
                    forms.style.left = "50vw"
                }, 75)
            }, 75)
        }, 150)
    }
    else {
        forms.style.left = "100vw"
        setTimeout(() => {
            forms.style.display = "none"
            forms.style.left = "-50vw"
            forms.style.clipPath = "polygon(0 0, 100% 0, 90% 100%, 0% 100%)"

            register_form.style.display = "none"
            login_form.style.display = "flex"
            setTimeout(() => {
                forms.style.display = "flex"
                setTimeout(() => {
                    forms.style.left = "0vw"
                }, 75)
            }, 75)
        }, 150)
    }

}
