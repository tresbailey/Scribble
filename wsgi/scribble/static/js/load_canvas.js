function loadScript(url, callback){{
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    script.onreadystatechange = callback;
    script.onload = callback;
    head.appendChild(script);
}}

var runJQueryScripts = function() {{    
$.ajax({{ 
    url: BASEURL + '/{0}/{1}/canvas',
    type: 'GET',            
    cache: false,            
    success: function( htmll ) {{                
var canvas = $("#scribble_overlay").children('div').children('canvas');
var context = canvas[0].getContext('2d');
var imageObj = new Image();
imageObj.onload = function() {{
    context.drawImage(this, 0, 0);
}};
imageObj.src = htmll;                
    }}    
}});
}}
loadScript('//code.jquery.com/jquery-1.7.2.min.js', runJQueryScripts);
