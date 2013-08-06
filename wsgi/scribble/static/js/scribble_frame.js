
function load_scribble_frame() {
    var inner = $({html: %(html)});
    var el = $('body', %(frame).contents());
    el.html($('<div />', inner).text());
    var canvas = el.children("#scribble_overlay").children('div').children('canvas');
    var context = canvas[0].getContext('2d');
    var imageObj = new Image();
    imageObj.onload = function() {
        context.drawImage(this, 0, 0);
    };
    imageObj.src = $(%(image)).attr('src');
    var factor = 450 / %(width).html();
    %(frame).width(%(width).html() + 'px');
    frame_offset = %(frame).offset();
    %(frame).height('100%');
}
