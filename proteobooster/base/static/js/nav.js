$(document).ready(function(){

    $(document).tooltip({
        content: function () {
            return $(this).prop('title');
        },
        show: null, 
        close: function (event, ui) {
            ui.tooltip.hover(

            function () {
                $(this).stop(true).fadeTo(400, 1);
            },

            function () {
                $(this).fadeOut("400", function () {
                    $(this).remove();
                })
            });
        }
    });

    // mobile menu animation
    $('#nav-control').click(function(){
    });

    // hover animations of the menu items
    $('.nav-item').mouseover(function(){
        $(this).children('.nav-item .nav-icon').css('filter','none');
    });    
    $('.nav-item').mouseleave(function(){
        $(this).children('.nav-item:not(.selected-nav-item) .nav-icon').css('filter','grayscale(100%)');
    });
});
