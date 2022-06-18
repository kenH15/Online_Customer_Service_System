var socket
var date = new Date()
var time = "0" + ":" + "0"
var staffName = []
var staffImage = []
$(function () {
    $('.emotion').qq_face({
        id: 'facebox',
        assign: 'InputMessage',
        path: 'static/images/arclist/'
    })
})

function replace_em(str) {
    str = str.replace(/\</g, '&lt;')
    str = str.replace(/\>/g, '&gt;')
    str = str.replace(/\n/g, '<br/>')
    str = str.replace(/\[em_([0-9]*)\]/g, '<img src="static/images/arclist/$1.gif" border="0" />')
    return str
}

function init(code) {
    var host = "ws://127.0.0.1:" + code + '/'
    try {
        socket = new WebSocket(host)
        socket.onopen = function (msg) {
            log("Begin Connection!")
        }
        socket.onmessage = function (msg) {
            log(msg.data)
        }
        socket.onclose = function (msg) {
            log("Lose Connection!")
        }
    }
    catch (ex) {
        log(ex)
    }
    document.getElementById("InputMessage").focus()
}

function send() {
    var txt, msg
    txt = document.getElementById("InputMessage")
    msg = txt.value
    if (!msg) {
        alert("Message can not be empty")
        return
    }
    txt.value = ""
    txt.focus()
    try {
        socket.send(msg)
    } catch (ex) {
        log(ex)
    }
    log_user_message(msg)
}

window.onbeforeunload = function () {
    try {
        socket.send('quit')
        socket.close()
        socket = null
    }
    catch (ex) {
        log(ex)
    }
}

function log(msg) {
    var i = 0
    var new_msg = ""
    var staffName_str = ''
    var temp = 0

    if (msg[0] === '{') {
        while (1) {
            if (msg[i] === '}') {
                i++
                break
            }
            else {
                i++
            }
        }
        if (msg[i] === '{') {
            while (1) {
                if (msg[i] === '}') {
                    i++
                    break
                }
                else {
                    i++
                }
            }
        }
        while (1) {
            if (i === msg.length) {
                break
            }
            else {
                new_msg += msg[i]
                i++
            }
        }
    }
    else {
        new_msg = msg
    }
        if (msg.indexOf('连接成功/IP=') >= 0) {
        for (var i = 0; i < msg.length; i++) {
            if (msg[i] === '/') {
                if (temp == 2) {
                    staffName = staffName_str
                }
                if (temp == 5) {
                    break
                }
                temp++
            }
            if (msg[i] === '=') {
                staffName_str = ""
            }
            else {
                staffName_str += msg[i]
            }
        }

        staffImage = staffName_str
        new_msg = '连接成功! ' + staffName + '为您服务'
    }
    if (new_msg[0] === '*' && new_msg[1] === 's'
        && new_msg[2] === 'e' && new_msg[3] === 'l'
        && new_msg[4] === 'f' && new_msg[5] === '*') {
        var folder_name = ""
        var file_name = ""
        var state = 0
        var j = 0

        while (1) {
            if (j === msg.length) {
                break
            }
            else if (msg[j] === '*') {
                state++
            }
            else if (msg[j] === '/') {
                state++
            }
            else if (state === 2) {
                folder_name += msg[j]
            }
            else if (state === 3) {
                file_name += msg[j]
            }
            j++
        }

        user_Image(folder_name, file_name)
        return
    }
    else if (new_msg[0] === '*' && new_msg[1] === 'l'
        && new_msg[2] === 'o' && new_msg[3] === 'g'
        && new_msg[4] === '*') {
        var folder_name2 = ""
        var file_name2 = ""
        var state2 = 0
        var j2 = 0

        while (1) {
            if (j2 === msg.length) {
                break
            }
            else if (msg[j2] === '*') {
                state2++
            }
            else if (msg[j2] === '/') {
                state2++
            }
            else if (state2 === 2) {
                folder_name2 += msg[j2]
            }
            else if (state2 === 3) {
                file_name2 += msg[j2]
            }
            j2++
        }

        staff_image(folder_name2, file_name2)
        return
    }

    if (new_msg[0] !== '<') {
        new_msg = replace_em(new_msg)
    }

    date = new Date()
    var new_time = get_time(date.getHours()) + ":" + get_time(date.getMinutes())
    var htmlData = '<li class ="msg_box">'
    if (new_time != time) {
        time = new_time
        htmlData = htmlData
            + '<p class = "time"><span>' + time + '</span></p>'
    }
    if (msg !== '') {
        var htmlData = htmlData
            + '<div class="msg">'
            + '<p class="ip">'
            + staffName
            + '</p>'
            + '<img class = "avartar" width ="30" height = "30" src = ' + staffImage + '>'
            + '<div class="text">'
            + new_msg
            + '</div>'
            + '</div>'
            + '</li>'
        $(".chat_messagebox #chat").append(htmlData)
        $(".chat_messagebox").scrollTop($(".chat_messagebox")[0].scrollHeight + 20)
        $(".chat_messagebox").val('')
    }
}

function get_time(time) {
    time = time.toString()
    if (time.length === 1)
        return '0' + time
    return time
}


function log_user_message(msg) {
    msg = replace_em(msg)

    date = new Date()
    var new_time = get_time(date.getHours()) + ":" + get_time(date.getMinutes())
    var htmlData = '<li class ="msg_box">'
    if (new_time != time) {
        time = new_time
        htmlData = htmlData
            + '<p class = "time"><span>' + time + '</span></p>'
    }
    if (msg !== '') {
        htmlData = htmlData
            + '<div class="user_msg">'
            + '<img class = "avartar" width ="30" height = "30" src = "static/images/chat.png">'
            + '<div class="text">'
            + msg
            + '</div>'
            + '</div>'
            + '</li>'
        $(".chat_messagebox #chat").append(htmlData)
        $(".chat_messagebox").scrollTop($(".chat_messagebox")[0].scrollHeight + 20)
        $(".chat_messagebox").val('')
    }
}


function user_Image(folder_name, file_name) {
    date = new Date()
    var new_time = get_time(date.getHours()) + ":" + get_time(date.getMinutes())
    var htmlData = '<li class ="msg_box">'
        + '<p class = "time"><span>' + new_time + '</span></p>'
        + '<div class="user_msg">'
        + '<img class = "avartar" width ="30" height = "30" src = "static/images/chat.png">'
        + '<img src = ' + 'static/user_image/' + folder_name + '/' + file_name + ' height = "200">'
        + '</div>'
        + '</li>'
    $(".chat_messagebox #chat").append(htmlData)
    $(".chat_messagebox").scrollTop($(".chat_messagebox")[0].scrollHeight + 20)
    $(".chat_messagebox").val('')
}

function staff_image(folder_name, file_name) {
    date = new Date()
    var new_time = get_time(date.getHours()) + ":" + get_time(date.getMinutes())
    var htmlData = '<li class ="msg_box">'
        + '<p class = "time"><span>' + new_time + '</span></p>'
        + '<div class="msg">'
        + '<img class = "avartar" width ="30" height = "30" src = "static/images/chat.png">'
        + '<img src = ' + 'static/staff_image/' + folder_name + '/' + file_name + ' height = "200">'
        + '</div>'
        + '</li>'
    $(".chat_messagebox #chat").append(htmlData)
    $(".chat_messagebox").scrollTop($(".chat_messagebox")[0].scrollHeight + 20)
    $(".chat_messagebox").val('')
}

document.onkeydown = function (event) {
    var e = event || window.event || arguments.callee.caller.arguments[0]
    if (event.ctrlKey && (e && e.keyCode === 13)) {
        send()
    }
}

function send_question(msg) {
    if (!msg) {
        alert("Message can not be empty")
        return
    }
    try {
        socket.send(msg)
    } catch (ex) {
        log(ex)
    }
    log_user_message(msg)
}

function connect_staff() {
    try {
        socket.send('*connect_staff*')
    } catch (ex) {
        log(ex)
    }
}

function chat_close() {
    try {
        socket.send('quit')
        socket.close()
        socket = null
    }
    catch (ex) {
        log(ex)
    }
    window.close()
    var obj = parent.document.getElementById('ifm_chat')
    parent.document.body.removeChild(obj)
}

function evaluate_staff() {
    var htmldata = '<div class="black_overlay"></div>'
        + '<div class="starability-container">'
        + '<div class = "eval_title">客服评价</div>'
        + '<form>'
        + '<p>请对我们的服务进行评价，谢谢！</p>'
        + '<fieldset class="starability-slot">'
        + '<input type="radio" id="rate5-2" name="rating" value="5"/>'
        + '<label for="rate5-2" title="Amazing">5 stars</label>'
        + '<input type="radio" id="rate4-2" name="rating" value="4"/>'
        + '<label for="rate4-2" title="Very good">4 stars</label>'
        + '<input type="radio" id="rate3-2" name="rating" value="3"/>'
        + '<label for="rate3-2" title="Average">3 stars</label>'
        + '<input type="radio" id="rate2-2" name="rating" value="2"/>'
        + '<label for="rate2-2" title="Not good">2 stars</label>'
        + '<input type="radio" id="rate1-2" name="rating" value="1"/>'
        + '<label for="rate1-2" title="Terrible">1 star</label>'
        + '</fieldset>'
        + '</form>'
        + '<button class="btn btn-primary" id="evaluate_button" type="submit" onclick = "chat_close()">确认</button>'
        + '</div>'
    $("body").append(htmldata)
    $(".starability-container").css('top', '130')
    $(".starability-container").css('left', '145')
}

function new_send_image() {
    socket.send('*create image data*')
    window.open("image_send", "image_send", "width = 250px, height = 202px")
}
