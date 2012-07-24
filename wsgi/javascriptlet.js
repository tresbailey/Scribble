javascript:(function(){ 
function loadScript(url, callback)
{
var head = document.getElementsByTagName('head')[0];
var script = document.createElement('script');
script.type = 'text/javascript';
script.src = url;
script.onreadystatechange = callback;
script.onload = callback;
head.appendChild(script);
}
var runJQueryScripts = function() {
    $.ajax({ url: 'http://localhost:5000/scribble_overlay',
            type: 'GET',
            cache: false,
            success: function( htmll ) {
                var load = $(htmll);
                load.css({position: 'absolute',
                        top: '0px',
                        left: '0px',
                        'z-index': 99999,
                        'height': $('body').height(),
                        'width': $('body').width()
                });
                $('body').append(load);
                $.getScript('http://localhost:5000/static/js/page_setup.js', function(data, textstatus, jxhr) {
                    setup_overlay();
                });
            }
    });
};
loadScript('http://code.jquery.com/jquery-1.7.2.min.js', runJQueryScripts);
