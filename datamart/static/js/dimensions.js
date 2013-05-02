(function($){

  $(function() {
    $('#DimensionsGrid').datagrid({ dataSource: new DimensionsDataSource({

      // Column definitions for Datagrid
      columns: [{
        property: 'unit_name',
        label: 'Unit Name',
        sortable: false
      },{
        property: 'description',
        label: 'Description',
        sortable: false
      }],

    })
    });

  });
})(jQuery)

