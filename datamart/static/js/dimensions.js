(function($){

  $(function() {
    $('#DimensionsGrid').datagrid({ dataSource: new DimensionsDataSource({

      // Column definitions for Datagrid
      columns: [{
        property: 'unit_name',
        label: 'Unit Name',
        sortable: true
      },{
        property: 'description',
        label: 'Description',
        sortable: true
      }],

    })
    });

  });
})(jQuery)

