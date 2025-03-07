$(window).scroll(function() {
    const scroll = $(window).scrollTop();
    if (scroll > 50) {
        $(".navbar").css("background-color", "#435a42");
    } else {
        $(".navbar").css("background-color", "transparent"); } });