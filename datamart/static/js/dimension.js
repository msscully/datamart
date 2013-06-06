(function($){
  $('.remove-dimension').click(function(){
    var id = $(this).attr('id').substring(3);
    var name = $('#dun_'+id).html();
    if (confirm("Are you sure you want to delete Dimension " + name + "?")) {
      $.ajax({
        url: '/api/dimension/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) { 
          $('#dr_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted Dimension " + name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete Dimension " + name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  });

  $('.remove-variable').click(function(){
    var id = $(this).attr('id').substring(3);
    var name = $('#vdn_'+id).html();
    if (confirm("Are you sure you want to delete Variable " + name + "?")) {
      $.ajax({
        url: '/api/variable/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) {
          $('#vr_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted Variable " + name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete Variable " + name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  });

  $('.remove-role').click(function(){
    var id = $(this).attr('id').substring(3);
    var name = $('#rn_'+id).text();
    if (confirm("Are you sure you want to delete Role " + name + "?")) {
      $.ajax({
        url: '/api/role/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) {
          $('#drr_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted Role " + name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete Role " + name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  });

  $('.remove-user').click(function(){
    var id = $(this).attr('id').substring(3);
    var name = $('#un_'+id).html();
    if (confirm("Are you sure you want to delete User " + name + "?")) {
      $.ajax({
        url: '/api/user/'+id,
        type: 'DELETE',
        dataType: 'json',
        data: '',
        success: function(response) {
          $('#ur_'+id).remove();
          $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted User " + name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        },
        failure: function(response) {
          $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete User " + name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
        }
      });
    }
    return false;
  });

})(jQuery);
