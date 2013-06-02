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
                  item.controls = compiledTemplate({model: 'facts', id: item.id, item_name: item.unit_name, description: item.description});
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

      $(document).on('click', '#dg-add-filter', function(){
          //var columnNames = _.pluck(columns, 'label');
          var compiledTemplate = Handlebars.getTemplate('facts-new-filter');
          var newFilter = compiledTemplate({columns: columns, ops: operations});
          //var newFilter = "<form class='fact-filter form-inline'> <fieldset>   <input class='input' type='text' name='field' placeholder='Field'> <select>"+columnSelect+"</select><input class='input' type='text' name='op' placeholder='Operation'> <input class='input' type='text' name='value' placeholder='Value'> </fieldset> </form>";

          $('#facts-grid-filter').append($("<div class='fact-filter'></div>").html(newFilter));
      });

      $(document).on('change', 'select.op-select', function(){
          console.log('op select changed');
          if ($('option:selected', this).val() != ''){
              $(this).siblings('.val-input').removeAttr('disabled');
          }
          else {
              $(this).siblings('.val-input').attr('disabled', 'disabled');
          }
      });

      $(document).on('change', '#facts-grid-filter', function(){
          console.log('filter changed');
          filters = [];
          $(this).find('.fact-filter').each(function(){
              newFilter = {field: $(this).find('select.field-select option:selected').val(),
                  op: $(this).find('select.op-select option:selected').val(),
                  val: $(this).find('.val-input').val()
              };
              filters.push(newFilter);
          });
          console.log(filters);

      });

      $(document).on('click','.remove-filter',function(){
          $(this).closest('div.fact-filter').remove();
          $('#facts-grid-filter').change();
      });

  });
})(jQuery)

