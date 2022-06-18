function send_email(user_email, verification_code) {
    var title = "来自思密达的验证邮件"
    var content = '<p><strong>尊敬的用户，您好！</strong></p>' +
        '<br>' +
        '<p>感谢您对思密答的支持。</p>' +
        '<p>您的验证码是: ' + '<strong> <font size=5 color="blue">' + verification_code + '</font></strong> </p>' +
        '<p>注：此链接有效期为30分钟，过期未验证将失效。如非本人操作，请忽略此邮件，' +
        '由此给您带来的不便请谅解。</p>' +
        '<p>如有疑问，请登录思密答。</p>' +
        '<hr style="height:1px;border:none;border-top:1px dashed #0066CC;" />' +
        '<p>此邮件由思密答系统发出，系统不接受回信，请勿直接回复。</p>'

    try {
        Email.send("simida_account@163.com",
            user_email,
            title,
            content,
            "smtp.163.com",
            "simida_account@163.com",
            "liuxuesheng456")
        alert("邮件已发送，请输入验证码")
    }
    catch (err) {
        alert("发送失败，请重试!")
    }
}

function set_timer(time, url) {
    var default_time = 5
    var default_url = '/'
    var passed_time = 0
    var redirect, display_time

    if (typeof time === 'number') {
        default_time = time
    }
    if (typeof url === 'string') {
        default_url = url
    }

    redirect = function () {
        location.href = default_url
    }


    display_time = function () {
        document.all.timer.innerHTML = (default_time - passed_time) + "秒后返回首页"
        passed_time++
    }

    setInterval(display_time, 1000)
    setTimeout(redirect, default_time * 1000)
}