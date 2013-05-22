(function($){
  $('.remove-dimension').click(function(){
    var id = $(this).attr('id').substring(3);
    var unit_name = $('#dun_'+id).html();
    if (confirm("Are you sure you want to delete Dimension " + unit_name + "?")) {
      $.ajax({
        url: '/api/dimension/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) { 
          $('#dr_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted Dimension " + unit_name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete Dimension " + unit_name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  });
})(jQuery);
