define([
       'jquery',
       'underscore',
       'backbone',
       'backgrid'
], function($, _, Backbone, Backgrid){

    var Dimension = Backbone.Model.extend({
        initialize: function () {
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.on("change", function (model, options) {
                if (options && options.save === false) return;
                model.save();
            });
        }
    });

    var Dimensions = Backbone.Collection.extend({
          model: Dimension,
          url: "api/dimension",
          
          parse: function(response) {
                  return response.objects;
          }

    });

    var dimensions = new Dimensions();

    var columns = [{
        name: "id", // The key of the model attribute
        label: "ID", // The name to display in the header
        editable: false, // By default every cell in a column is editable, but *ID* shouldn't be
        // Defines a cell type, and ID is displayed as an integer without the ',' separating 1000s.
        cell: Backgrid.IntegerCell.extend({
            orderSeparator: ''
        })
    }, {
        name: "unit_name",
        label: "Unit Name",
        // The cell type can be a reference of a Backgrid.Cell subclass, any Backgrid.Cell subclass instances like *id* above, or a string
        cell: "string" // This is converted to "StringCell" and a corresponding class in the Backgrid package namespace is looked up
    }, {
        name: "description",
        label: "Description",
        cell: "string"
    }];

    // Initialize a new Grid instance
    var grid = new Backgrid.Grid({
        columns: columns,
        collection: dimensions
    });

    // Render the grid and attach the root to your HTML document
    $("#DimensionsGrid").append(grid.render().$el);

    // Fetch some countries from the url
    dimensions.fetch({reset: true});

});
