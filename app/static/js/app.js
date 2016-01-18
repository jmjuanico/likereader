$(document).ready(function () {
    window.setTimeout(function() {
        $(".alert").fadeTo(1000, 0).slideUp(1000, function(){
            $(this).remove();
        });
    }, 5000);

});

/***********************************************************************
freeze panes
************************************************************************/

$(document).scroll(function(e){
    var scrollTop = $(document).scrollTop();
    if(scrollTop > 0){
        console.log(scrollTop);
        $('.navbar').removeClass('navbar-static-top').addClass('navbar-fixed-top');
    } else {
        $('.navbar').removeClass('navbar-fixed-top').addClass('navbar-static-top');
    }
});

/***********************************************************************
translates the posts if language vs post is not the same
************************************************************************/

function translate(sourceLang, destLang, sourceId, destId, loadingId) {
    $(destId).hide();
    $(loadingId).show();
    $.post('/translate', {
        text: $(sourceId).text(),
        sourceLang: sourceLang,
        destLang: destLang
    }).done(function(translated) {
        $(destId).text(translated['text'])
        $(loadingId).hide();
        $(destId).show();
    }).fail(function() {
        $(destId).text("{{ _('Error: Could not contact server.') }}");
        $(loadingId).hide();
        $(destId).show();
    });
}

/***********************************************************************
shows up reply box when reply button is clicked
************************************************************************/

function replycomment(commentid){
    if ($(commentid).css('display') == 'none' ){
        $(commentid).show();
    } else {
        $(commentid).hide();
    }
}

/***********************************************************************
used for openid
************************************************************************/

function set_openid(openid, pr)
{
    u = openid.search('<username>');
    if (u != -1) {
        // openid requires username
        user = prompt('Enter your ' + pr + ' username:');
        openid = openid.substr(0, u) + user;
    }
    form = document.forms['login'];
    form.elements['openid'].value = openid;
}

$(".nav li").on("click", function() {
    $(".nav li").removeClass("active");
    $(this).addClass("active");
});

/***********************************************
facebook sharing sdk
************************************************/

window.fbAsyncInit = function() {
    FB.init({
    appId      : '1666096990295024',
    xfbml      : true,
    version    : 'v2.5'
    });
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


