
sketch = false;
sketchPos = {
    x: null,
    y: null
};
marks = [];
image_data = [];
dataURL = '';
original_width = '';
freehand = true;
function setup_overlay() {
    $('myCanvas').height($('body').height());
    $('#myCanvas').mousedown(function(e) {
        if (freehand) {
            var mouseX = e.pageX;
            var mouseY = e.pageY;
            sketch = true;
            sketchPos.x = e.pageX;
            sketchPos.y = e.pageY;
            drawPixels(mouseX, mouseY);   
        }
    });
    $('#myCanvas').mousemove(function(e) {
        if(sketch) {
            var mouseX = e.pageX - this.offsetLeft;
            var mouseY = e.pageY - this.offsetTop;
            drawPixels(mouseX, mouseY);
        }
    });
    $('#myCanvas').mouseup(function(e) {
        if(freehand) {
            sketch = false;
        }
    });
    $('#myCanvas').click(function(e) {
        if(!freehand) {
            var mouseX = e.pageX - this.offsetLeft;
            var mouseY = e.pageY - this.offsetTop;
            drawCircle(mouseX, mouseY);
            $('#myModal').modal('show');
            $('#pin_close').click(function(e) {
                $('#pin_desc').val('');
                $('#myModal').modal('hide');
            });
            $('#pin_save').click(function(e) {
                descr = $('#pin_desc').val();
                marks.push([[mouseX, mouseY], descr]);
                $('#myModal').modal('hide');
                //$('#pin_desc').val('');
            });
        }   
    });
    $('#freehand').click(function(e) {
        freehand = true;
    });
    $('#marker').click(function(e) {
        freehand = false;
    });
    $('#myModal').modal({
        keyboard: false
    });
    $('#myModal').modal('hide');
    $("#save").click(function(e) {
        scrape_pixels();
        input = {canvas_data: image_data,
            marks_data: marks,
            base_html: $('html').html(),
            base_url: window.location.origin + window.location.pathname,
            image_data: dataURL,
            original_width: original_width
        }
        $.ajax({ 
            url: 'https://scrib-tresback.rhcloud.com/4fb5b83b51692b56c9000000',
            data: JSON.stringify(input),
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'application/json'
        });
    });
}

function scrape_pixels() {
    var cheight = $('#myCanvas').height();
    var cwidth = $('#myCanvas').width();
    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    dataURL = canvas.toDataURL("image/png");
    original_width = cwidth;
    /*
    for(x=0; x < cwidth; x++) {
        for(y=0; y < cheight; y++) {
            var pixel = context.getImageData(x, y, 1, 1);
            if (pixel.data[0]!=0 || pixel.data[1]!=0 || pixel.data[2]!=0 || pixel.data[3]!=0) {
                image_data.push([[x, y], pixel.data[0], pixel.data[1], pixel.data[2], pixel.data[3]]);
            }           
        }
    }
    */
}

function drawPixels(xPos, yPos) {
    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    context.beginPath();
    context.moveTo(sketchPos.x, sketchPos.y);
    context.lineTo(xPos, yPos);
    context.lineWidth = 5;
    context.lineCap = "round";
    context.stroke();
    sketchPos.x = xPos;
    sketchPos.y = yPos;
}
function drawCircle(xPos, yPos) {
//http://falcon80.com/HTMLCanvas/BasicShapes/Circle.html
    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    context.moveTo(xPos, yPos);
    context.strokeStyle = 'red';
    var radius = 5;
    var start = 0 * Math.PI / 180;
    var end = 360 * Math.PI /180;
    context.arc(xPos, yPos, radius, start, end, false);
    context.fill();
}
