/*
 * Flickr DataSource for Fuel UX Datagrid
 * https://github.com/adamalex/fuelux-dgdemo
 *
 * Copyright (c) 2012 Adam Alexander
 * Demo source released to public domain.
 */


var FactsDataSource = function (options) {
    this._formatter = options.formatter;
    this._columns = options.columns;
};

FactsDataSource.prototype = {

    /**
     * Returns stored column metadata
     */
    columns: function () {
        return this._columns;
    },

    /**
     * Called when Datagrid needs data. Logic should check the options parameter
     * to determine what data to return, then return data by calling the callback.
     * @param {object} options Options selected in datagrid (ex: {pageIndex:0,pageSize:5,search:'searchterm'})
     * @param {function} callback To be called with the requested data.
     */
    data: function (options, callback) {

        var url = '/api/facts';
        var self = this;
        var q = {};
        
        if (options.search) {

            var searchTerm = '%' + options.search + '%';
            var filters = [{"name": "4", "op": "like", "val": searchTerm}];
            q.filters = filters;
            q.disjunction = true;

        }
        // Sorting
        if (options.sortProperty) {
            var order = [{field: options.sortProperty.toString(), direction: options.sortDirection}];
            q.order_by = order;
        }
        // Filtering
        if (options.filter) {
            q.filters = options.filter;
        }


        $.ajax(url, {

            dataType: 'json',
            data: {"q": JSON.stringify(q),
                   "results_per_page": options.pageSize,
                   "page": options.pageIndex + 1 },
            jsonp: false,
            contentType: "application/json",
            type: 'GET'

        }).done(function (response) {

            // Prepare data to return to Datagrid
            var data = response.objects;
            for(var i in data){
                for(var j in data[i].values){
                    data[i][j] = data[i].values[j];
                }
                delete data[i].values;
            }

            var count = response.num_results;
            var startIndex = (response.page - 1) * options.pageSize;
            var endIndex = startIndex + options.pageSize;
            var end = (endIndex > count) ? count : endIndex;
            var pages = response.total_pages;
            var page = response.page;
            var start = startIndex + 1;

            // Allow client code to format the data
            if (self._formatter) {self._formatter(data);}

            // Return data to Datagrid
            callback({ data: data, start: start, end: end, count: count, pages: pages, page: page });

        });

    }
};
