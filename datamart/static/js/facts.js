(function($){

  $(function() {
    $('#FactsGrid').datagrid({ dataSource: new FactsDataSource({
        columns: [{}],
        formatter: function (items) {
            var compiledTemplate = Handlebars.getTemplate('model-table-controls');
            $.each(items, function (index, item) {
                item.controls = compiledTemplate({model: 'dimension', id: item.id, item_name: item.unit_name, description: item.description});
            });
        }
    }),
    stretchHeight: false
    });

    $(document).on('click', '.remove-item', function(){
        var $me = $(this);
        var id = $(this).attr('id').substring(2);
        var unitName = $(this).attr('item_name');
        var model = $(this).attr('model');
        if (confirm("Are you sure you want to delete " + model + " " + unitName + "?")) {
            $.ajax({
                url: '/api/' + model + '/' + id,
                type: 'DELETE',
                dataType: 'json',
                data: '',
                success: function(response) {
                    $('#FactsGrid').datagrid('reload');
                    //$me.closest('tr').remove();
                    $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted " + model + " " + unitName + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
                },
                failure: function(response) {
                    $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete " + model + " " + unitName + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
                }
            });
        }
        return false;
    });
  });
})(jQuery)

