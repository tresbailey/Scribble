
sketch = false;
sketchPos = {
    x: null,
    y: null
};

var sketch = false;
var sketchPos = {
    x: null,
    y: null
};
var marks = [];
var image_data = [];
var dataURL = '';
var original_width = '';
var freehand = true;
var canvas;
var stage;
var g;
var shape;
var isMouseDown;
var oldPosition;
var currentShape;
var ctx;
var selectedColor;
var oldMidX;
var oldMidY;
var oldX;
var oldY;
var firstLoad;
var canvasOffset;
var circleRadius=10;
function init() {

    firstLoad = true;
    canvas = document.getElementById('myCanvas');
    ctx = canvas.getContext("2d");
    stage = new createjs.Stage(canvas);
    oldPosition = new createjs.Point(stage.mouseX, stage.mouseY);
    stage.autoClear = true;
    stage.addEventListener("stagemousedown", handleMouseDown) ;
    stage.addEventListener("stagemouseup", handleMouseUp); 
    canvasOffset = $(canvas).offset();

    createjs.Touch.enable(stage);

    stage.update();
    createjs.Ticker.addListener(window);
}

function stop() {
    createjs.Ticker.removeListener(window);
}
function tick() {
    if (isMouseDown) {
        var pt = new createjs.Point(stage.mouseX, stage.mouseY);
        var midPoint = new createjs.Point(oldX + pt.x>>1, oldY+pt.y>>1);
        currentShape.graphics.moveTo(midPoint.x, midPoint.y);
        currentShape.graphics.curveTo(oldX, oldY, oldMidX, oldMidY);
        currentShape.draw(ctx);

        oldX = pt.x;
        oldY = pt.y;

        oldMidX = midPoint.x;
        oldMidY = midPoint.y;

        stage.update();
    }
}

function handleMouseDown() {
    if (freehand) {
        isMouseDown = true;
        firstLoad = false;
        var s = new createjs.Shape();
        oldX = stage.mouseX;
        oldY = stage.mouseY;
        oldMidX = stage.mouseX;
        oldMidY = stage.mouseY;
        var g = s.graphics;
        var thickness = 2;
        g.setStrokeStyle(thickness + 1, 'round', 'round');
        selectedColor = createjs.Graphics.getRGB(0, 0, 0);
        g.beginStroke(selectedColor);
        stage.addChild(s);
        currentShape = s;
    }
}

function handleMouseUp() {
    isMouseDown = false;
}
function setup_overlay() {
    init();
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
        keyboard: true,
    });
    $('#myModal').modal('hide');
    modal_left = $('#base_actions').scrollLeft();
    modal_width = $("#base_actions").offset().left;
    $("#base_actions").css("width", "auto");
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
            url: '{{ home }}/4fb5b83b51692b56c9000000',
            data: JSON.stringify(input),
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'application/json',
            success: function( data, textStatus) {
                if ( data.redirect) {
                 console.log(data.redirect);
                } else {
                    console.log(JSON.stringify(data));
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if ( jqXHR.status == 401 ) {
                    $.ajax({ url: '{{ home }}/static/login.html',
                    type: 'GET',
                    success: function(data, textStatus) {
                        $('.modal-body').html(data);
                    },
                    error: function(xhr, txtStat, errThrwn) {
                        console.log(txtStat);
                    }
                    });
                }
            }
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
}

function drawCircle(xPos, yPos) {
//http://falcon80.com/HTMLCanvas/BasicShapes/Circle.html
    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
	shape = new createjs.Shape();
	shape.graphics.beginFill('#ff0000').drawCircle(0,0,circleRadius);
	shape.graphics.beginFill('#ffffff').drawCircle(0,0,circleRadius*0.8);
	shape.graphics.beginFill('#ff0000').drawCircle(0,0,circleRadius*0.6);
	shape.graphics.beginFill('#ffffff').drawCircle(0,0,circleRadius*0.4);
	shape.graphics.beginFill('#ff0000').drawCircle(0,0,circleRadius*0.2);
	shape.x = xPos;
	shape.y = yPos;
    stage.addChild(shape);
    stage.update();
}
