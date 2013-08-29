(function($){
  $(function() {
       var getColumns = function(){
          var new_columns = [
              {'property':'id', 'label': 'Table ID', 'sortable': true},
              {'property':'subject_id', 'label': 'Subject ID', 'sortable': false},
              {'property':'event', 'label': 'Event', 'sortable': false},
          ]

          var variables = FACTS.getVariables();
          
          for (var i=0;i<variables.length;i++){
              var column = variables[i];
              if (column.in_use = 'True'){
                  new_column = {property: column.id, label: column.name, sortable: true};
                  new_columns.push(new_column);
              }
          }
          new_columns.push({'property':'controls', 'label': '', 'sortable': false});
          return new_columns;
      };

      var filterTemplate = Handlebars.getTemplate('facts-new-filter');
      Handlebars.registerPartial("filter", filterTemplate);

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
                  item.event = item.event.name;
                  itemURL = '/facts/' + item.id + '/edit/';
                  item.controls = compiledTemplate({model: 'facts', 
                                                   id: item.id,
                                                   item_name: item.id,
                                                   description: item.description,
                                                   url: itemURL,
                                                   IS_ADMIN: IS_ADMIN
                  });
              });
          }
      }),
      stretchHeight: false
      });

      $('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter = [];

      $(document).on('click', '.remove-item', function(){
          var $me = $(this);
          var id = $(this).attr('id').substring(2);
          var name = $(this).attr('item_name');
          var model = $(this).attr('model');
          if (confirm("Are you sure you want to delete all " + model + " with id=" + name + "?")) {
              $.ajax({
                  url: '/api/' + model + '/' + id,
                  type: 'DELETE',
                  dataType: 'json',
                  data: '',
                  success: function(response) {
                      $('#FactsGrid').datagrid('reload');
                      //$me.closest('tr').remove();
                      $('#flash-messages').append("<div class='alert alert-success'>Successfully deleted " + model + " " + name + ". <a class='close' data-dismiss='alert'>&#215;</a> </div>");
                  },
                  failure: function(response) {
                      $('#flash-messages').append("<div calss='alert alert-failure'>Error encountered when trying to delete " + model + " " + name + ". Please inform the site administrator. <a class='close' data-dismiss='alert'>&#215;</a> </div>");
                  }
              });
          }
          return false;
      });

      $(document).on('click', '#dg-add-filter', function(){
          var compiledTemplate = Handlebars.getTemplate('facts-nested-filter');
          var columns_no_controls = columns.slice(0,-1);
          var newFilter = compiledTemplate({columns: columns_no_controls, ops: operations, level: "filter0"});
          if ($('#dg-add-filter').attr('value') === 'Show filters'){
              $('#dg-add-filter').attr('value','Hide filters');
              if (!$('.nested-filter-and-level').length) {
                  $('#filter-submit').siblings('br').before(newFilter);
              }
              $('#fact-filter-form').slideDown()
          }
          else {
              $('#dg-add-filter').attr('value','Show filters');
              $('#fact-filter-form').slideToggle()
          }

      });

      var getNewLevel = function(classStr){
          var newLevel = '';
          if (classStr.indexOf('filter0') !== -1){
              newLevel = "filter1";
          } else {
              newLevel = "filter0";
          }
          return newLevel;
      }

      $(document).on('change', '.and-or-select', function(){
          currentVal = $(this).val();
          if ($(this).parent('div.and-or').siblings('.nested-filters').children('fieldset').length <= 1) {
              var compiledTemplate = Handlebars.getTemplate('facts-nested-filter');
              var columns_no_controls = columns.slice(0,-1);
              currentClass = $(this).parent('div.and-or').siblings('.nested-filters').attr('class');
              var newLevel = getNewLevel(currentClass);

              var newFilter = compiledTemplate({columns: columns_no_controls, ops: operations, level: newLevel});
              var newClass = 'nested-filters ' + newLevel;
              $(this).parent('div.and-or').siblings('.nested-filters').attr('class', newClass);
              $fieldset = $(this).parent('div.and-or').parent('fieldset');
              $fieldset.wrap("<fieldset class='nested-filter-and-level'><div class='" + currentClass + "'></div></fieldset>");
              $fieldset.parent('.nested-filters').before("<div class='and-or'><select class='and-or-select'><option value='and'>AND</option><option value='or'>OR</option></select></div>");
              $fieldset.parent('.nested-filters').siblings('div.and-or').children('select').val(currentVal);
              $fieldset.after(newFilter);
              $fieldset.siblings('.nested-filter-and-level:last').after("<button class='btn add-filter-btn'><i class='icon-plus'></i></button>");
              $(this).val('');
          }
      });

      $(document).on('click', 'button.btn.add-filter-btn', function(e){
          e.preventDefault();
          var compiledTemplate = Handlebars.getTemplate('facts-nested-filter');
          var columns_no_controls = columns.slice(0,-1);
          var currentClass = $(this).siblings('fieldset:first').children('div.nested-filters').attr('class');
          if (currentClass.indexOf('filter0') !== -1){
              currentLevel = "filter0";
          } else {
              currentLevel = "filter1";
          }

          var newFilter = compiledTemplate({columns: columns_no_controls, ops: operations, level: currentLevel});
          $(this).before(newFilter)
          return false;
      });

      $(document).on('change', 'select.op-select', function(){
          if ($('option:selected', this).val() != ''){
              $(this).siblings('.val-input').removeAttr('disabled');
          }
          else {
              $(this).siblings('.val-input').attr('disabled', 'disabled');
          }
      });

      var buildFilters = function(currentFilter){
          filters = {};
          value = $(currentFilter).children('div.and-or').children('select').val();
          if (value === 'and'){
              buildFilters($(currentFilter).children('.nested-filters'));
              var andLevel = $(currentFilter).children('.nested-filters').children('fieldset.nested-filter-and-level');
              nestedFilters = $.map(andLevel, function(val, i) {return buildFilters(val);});
              return {'and': nestedFilters};

          } else if (value === 'or'){
              return {'or':[buildFilters($(currentFilter).children('.nested-filters'))]}

          } else {
              filter = $(currentFilter).children('.nested-filters').children('fieldset.nested-filter');
              if (($(filter).find('select.field-select option:selected').val() != '') &&
                  ($(filter).find('select.op-select option:selected').val() != '') &&
                      ($(filter).find('.val-input').val() != '')){
                  newFilter = {name: $(filter).find('select.field-select option:selected').val(),
                      op: $(filter).find('select.op-select option:selected').val(),
                      val: $(filter).find('.val-input').val()
                  };
                  return newFilter;
              }
          }
      };


      var clearEmptyFilters = function(filter) {
          if ($(filter).children('div.nested-filters').children('fieldset.nested-filter-and-level').length){
              $.each($(filter).children('div.nested-filters').children('fieldset.nested-filter-and-level'), function(index, value){
                  clearEmptyFilters(value);
              });
          }

          if ((! $(filter).children('div.nested-filters').children('fieldset.nested-filter').length) && (! $(filter).children('div.nested-filters').children('fieldset.nested-filter-and-level').length)){
              $(filter).remove();
          }
      };

      $(document).on('click','.remove-filter',function(){
          $(this).closest('fieldset.nested-filter-and-level').remove();
          clearEmptyFilters($('form > fieldset'));
      });

      $(document).on('click','#filter-submit', function(e){
          e.preventDefault();
          filters = buildFilters($('form > fieldset'));
          if (!_.isEqual($('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter,filters)) {
              $('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter = filters;
              $('#FactsGrid').datagrid('reload');
          }
          return false;
      });

      $(document).on('click','#filter-reset', function(e){
          e.preventDefault();
          $('form > fieldset').remove();
          var compiledTemplate = Handlebars.getTemplate('facts-nested-filter');
          var columns_no_controls = columns.slice(0,-1);
          var newFilter = compiledTemplate({columns: columns_no_controls, ops: operations, level: "filter0"});
          $('#filter-submit').siblings('br').before(newFilter);
          $('#FactsGrid').datagrid().data().datagrid.options.dataOptions.filter = {};
          $('#FactsGrid').datagrid('reload');
          return false;
      });

      $(document).on('click','#dg-fv-DownloadFacts',function(){
          datagridOptions = $('#FactsGrid').datagrid().data().datagrid.options.dataOptions;
          q = {};

          q.filters = datagridOptions.filter;
          if (datagridOptions.sortProperty){
              q.order_by = [{field: datagridOptions.sortProperty.toString(), direction: datagridOptions.sortDirection}];
          }

          data = {results_per_page: 10000};
          data.q = JSON.stringify(q);
          $.fileDownload('/facts/download/',{data:data});
      });
  });
})(jQuery)
