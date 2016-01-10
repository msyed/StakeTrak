
$(document).ready(function(){

	if (document.location.hash == "#search") {
		$('#search-form').toggle();
    $('#options-container').toggle();
	}

  $('#search-db').on('click', function(){
  	document.location.hash = "search";
    $('#search-form').toggle();
    $('#options-container').toggle();
  });

  $('#go-back').on('click', function(){
  	document.location.hash = "";
    $('#options-container').toggle();
    $('#search-form').toggle();
  });
})
