(function( $ ) {
  $.fn.niceFileField = function() {
    this.each(function(index, file_field) {
      file_field = $(file_field);
      var label = file_field.attr("data-label") || "Choose File";

      file_field.css({'position': 'absolute', 'z-index': '2', 'top': '0', 'left': '0', 'filter': 'alpha(opacity=0)', '-ms-filter': 'progid:DXImageTransform.Microsoft.Alpha(Opacity=0)', 'opacity': '0', 'background-color': 'transparent', 'color': 'transparent'})
      file_field.after("<div class=\"nice_file_field input-append\"><input class=\"input span4\" type=\"text\"><a class=\"btn\">" + label + "</a></div>");

      var nice_file_field = file_field.next(".nice_file_field");
      nice_file_field.find("a").click( function(){ file_field.click() } );
      file_field.change( function(){
          file_path = file_field.val();
          // Browser security inserts C:\fakepath\filename so remove it.
          if(file_path.match(/fakepath/)) {
              file_path = file_path.replace(/C:\\fakepath\\/i, '');
          }
         nice_file_field.find("input").val(file_path);
      });
    });
  };

  $(function(){
      $(".nice_file_field").niceFileField();
  });
})( jQuery );
