$(document).ready(function() {
  $('#submit-upload').on('click', function() {
    console.log("click!");
    var jqxhr = $.post("/search?apikey=rollthru").done(function(data, status, errorthrown) {
      document.write(data);
    }).fail(function(data, status, errorthrown) {
      //alert( "error: " + status + " problem: " + errorthrown );
      document.write(data.responseText);
    })
    $('#loading-icon').toggle();
    $('#file-dropzone').toggle();

    var total = 0
    var sizeList = $('.dz-size');
    for (var i = 0; i < sizeList.length; i++) {
      sl = sizeList[i].innerHTML.split("</strong> ");
      var sizeValue = $('.dz-size strong')[i].innerHTML;
      var unit = sl[sl.length - 1].substring(0, 2);
      var typeStr = $('.dz-filename span')[i].innerHTML;
      var type = typeStr.split('.');
      var t = type[type.length - 1];

      var multiplier = 1
      console.log(t.toLowerCase());
      if (t.toLowerCase() == "pdf") {
        multiplier = 0.192;
      }
      if (t.toLowerCase() == "docx" || t.toLowerCase() == "doc") {
        multiplier = 0.394;
      }
      console.log(unit.toLowerCase());
      if (unit.toLowerCase() == "m" || unit.toLowerCase() == "mb") {
        multiplier = multiplier * 1024;
        console.log("megabytes!");
      }
      if (unit.toLowerCase() == "gb") {
        multiplier = multiplier * 1024 * 1024;
      }
      // 30 seconds per kilobyte
      var rate = 30;
      var seconds = parseFloat(sizeValue) * multiplier * rate;
      total = total + seconds
    }

    total = Math.floor(total)
    console.log("processing will take approximately " + total + " seconds.");

    var element = document.getElementById('example-clock-container');
    var seconds = new ProgressBar.Circle(element, {
        duration: 800,
        color: "#FCB03C",
        trailColor: "#ddd"
    });

    seconds.animate(0, function() {
        seconds.setText(0);
    });
    var lastSecond = 0;
    var loadingInterval = setInterval(function() {
      seconds.animate(lastSecond / total, function() {
        var percent = Math.floor((lastSecond*100)/total);
        seconds.setText(percent);
        lastSecond = lastSecond + 1;
        if (percent > 98) {
          clearInterval(loadingInterval);
        }
      });
    }, 1000);

  });

});