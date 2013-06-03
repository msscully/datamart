(function($){

  $(function() {
      var getColumns = function(){
          var url = '/api/variable';
          var new_columns = [
              {'property':'id', 'label': 'Table ID', 'sortable': true},
              {'property':'reviewed', 'label': 'Reviewed', 'sortable': true},
          ]

          $.ajax(url, {

              dataType: 'json',
              async: false,
              data: {"results_per_page": '500',
                  "page": 1 },
                  jsonp: false,
                  contentType: "application/json",
                  type: 'GET',
                  success: function(response) {
                      var data = response.objects;
                      var count = response.num_results;

                      for (var i=0;i<data.length;i++){
                          var column = data[i];
                          if (column.in_use = 'True'){
                              new_column = {property: column.id, label: column.display_name, sortable: true};
                              new_columns.push(new_column);
                          }
                      }
                  }
          });
          new_columns.push({'property':'controls', 'label': '', 'sortable': false});
          return new_columns;
      };
      var columns = getColumns();
      var operations = [
          {name: '=='},
          {name: '!='},
          {name: '>'},
          {name: '>='},
          {name: '<'},
          {name: '<='},
          {name: 'like'},
          {name: 'ilike'},
          {name: 'is null'},
          {name: 'is not null'},
          {name: 'in'},
          {name: 'not in'},
          {name: 'any'}
      ];

      $('#FactsGrid').datagrid({ dataSource: new FactsDataSource({
          columns: columns,
          formatter: function (items) {
              var compiledTemplate = Handlebars.getTemplate('model-table-controls');
              $.each(items, function (index, item) {
                  item.controls = compiledTemplate({model: 'facts', id: item.id, item_name: item.id, description: item.description});
              });
          }
      }),
      stretchHeight: false
      });

      $('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter = [];

      $(document).on('click', '.remove-item', function(){
          var $me = $(this);
          var id = $(this).attr('id').substring(2);
          var unitName = $(this).attr('item_name');
          var model = $(this).attr('model');
          if (confirm("Are you sure you want to delete all " + model + " with id=" + unitName + "?")) {
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

      $(document).on('click', '#dg-add-filter', function(){
          var compiledTemplate = Handlebars.getTemplate('facts-new-filter');
          var columns_no_controls = columns.slice(0,-1);
          var newFilter = compiledTemplate({columns: columns_no_controls, ops: operations});

          $('#facts-grid-filter').append($("<div class='fact-filter'></div>").html(newFilter));
      });

      $(document).on('change', 'select.op-select', function(){
          if ($('option:selected', this).val() != ''){
              $(this).siblings('.val-input').removeAttr('disabled');
          }
          else {
              $(this).siblings('.val-input').attr('disabled', 'disabled');
          }
      });

      $(document).on('change', '#facts-grid-filter', function(){
          filters = [];
          $(this).find('.fact-filter').each(function(){
              if (($(this).find('select.field-select option:selected').val() != '') &&
                      ($(this).find('select.op-select option:selected').val() != '') &&
                          ($(this).find('.val-input').val() != '')){
                  newFilter = {name: $(this).find('select.field-select option:selected').val(),
                      op: $(this).find('select.op-select option:selected').val(),
                      val: $(this).find('.val-input').val()
                  };
                  filters.push(newFilter);
              }
          });

          if (!_.isEqual($('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter,filters)) {
              $('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter = filters;
              $('#FactsGrid').datagrid('reload');
          }

      });

      $(document).on('click','.remove-filter',function(){
          $(this).closest('div.fact-filter').remove();
          $('#facts-grid-filter').change();
      });

  });
})(jQuery)
