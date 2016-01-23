//home.js
$(document).ready(function(){
	$("#btn-advantages").click(function() {
	    $('html, body').animate({
	        scrollTop: $("#advantages").offset().top
	    }, {
	    	done: function () { document.location.hash = "advantages" }
	    }, 1000);
	    return false;
	});

	$("#btn-hiw").click(function() {
	    $('html, body').animate({
	        scrollTop: $("#how-it-works").offset().top
	    }, {
	    	done: function () { document.location.hash = "how-it-works" }
	    }, 1000);
	    return false;
	});

	$("#btn-about").click(function() {
	    $('html, body').animate({
	        scrollTop: $("#about-us").offset().top
	    }, {
	    	done: function () { document.location.hash = "about-us" }
	    }, 1000);
	    return false;
	});
})
