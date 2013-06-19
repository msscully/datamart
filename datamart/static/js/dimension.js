(function($){

  $('.remove-item').click(function(){
      removeItem($(this));
  });

  var removeItem = function($item){
    var id = $item.attr('id').substring(2);
    var name = $('#n_'+id).text();
    var model = $.trim($('title').text().match(/-(.*)/)[1]).slice(0,-1);
    if (confirm("Are you sure you want to delete " + model + " '" + name + "'?")) {
      $.ajax({
        url: '/api/' + model.toLowerCase() + '/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) {
          $('#r_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted " + model + " '" + name + "'. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete " + model + " '" + name + "'. Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  };

})(jQuery);
