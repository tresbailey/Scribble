var runJQueryScripts = function() {{    
$.ajax({{ 
    // Causes problems between environments
    url: 'http:///localhost/{0}/{1}/canvas',
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

$(document).ready(function() {{
    runJQueryScripts();
}});
