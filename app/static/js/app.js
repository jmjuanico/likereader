/***********************************************************************
for the SIDEBAR
************************************************************************/
$(document).ready(function () {
$("#menu-toggle").click(function(e){e.preventDefault();$("#wrapper").toggleClass("toggled");});
});

$(document).ready(function () {
    window.setTimeout(function() {
        $(".alert").fadeTo(1000, 0).slideUp(1000, function(){
            $(this).remove();
        });
    }, 5000);

});

/***********************************************************************
google analytics; new comment
************************************************************************/

$(document).ready(function () {
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-72699813-1', 'auto');
  ga('send', 'pageview');

});

/***********************************************************************
freeze panes; replaced by navbar bootstrap functionality
************************************************************************/

/**

$(document).scroll(function(e){
    var scrollTop = $(document).scrollTop();
    if(scrollTop > 0){
        console.log(scrollTop);
        $('.navbar').removeClass('navbar-static-top').addClass('navbar-fixed-top');
    } else {
        $('.navbar').removeClass('navbar-fixed-top').addClass('navbar-static-top');
    }
});

**/

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
    if ($("#comment" + commentid).css('display') == 'none' ){
        $("#comment" +commentid).show();
        $("#commentbox" +commentid).expanding();
    } else {
        $("#comment" +commentid).hide();
    }
}

/************************************************************************
when not login and reply button is click
*************************************************************************/

function commentauth(commentid){
    if ($("#commentauthbox" + commentid).css('display') == 'none' ){
        $("#commentauthbox" +commentid).show();
        $("#commentauthbutton" +commentid).hide();
    } else {
        $("#commentauthbox" +commentid).hide();
        $("#commentauthbutton" +commentid).show();
    }
}

/************************************************************************
when not login and reply button is click
*************************************************************************/

function replyauth(commentid){
    if ($("#replyauthbox" + commentid).css('display') == 'none' ){
        $("#replyauthbox" +commentid).show();
        $("#replyauthbutton" +commentid).hide();
    } else {
        $("#replyauthbox" +commentid).hide();
        $("#replyauthbutton" +commentid).show();
    }
}

/************************************************************************
when not login and post button is click
*************************************************************************/

function postauth(){
    if ($("#postauthbox").css('display') == 'none' ){
        $("#postauthbox").show();
        $("#postauthbutton").hide();
    } else {
        $("#postauthbox").hide();
        $("#postauthbutton").show();
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

/***
$(".nav li").on("click", function() {
    $(".nav li").removeClass("active");
    $(this).addClass("active");
});

**/

/***********************************************
facebook sharing sdk
************************************************/

  window.fbAsyncInit = function() {
    FB.init({
      appId      : '756338107834310',
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




