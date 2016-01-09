
$(document).ready(function(){

  $('#search-db').on('click', function(){
    $('#search-form').toggle();
    $('#options-container').toggle();
  });

  $('#go-back').on('click', function(){
    $('#options-container').toggle();
    $('#search-form').toggle();
  });
})
