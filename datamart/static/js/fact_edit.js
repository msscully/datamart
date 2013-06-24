var FACTS = {}; // FACTS Namespace

(function($){
    // Returns all elements in a that aren't in b
    // http://stackoverflow.com/a/980412
    $.disjoin = function(a, b) {
            return $.grep(a, function($e) { return $.inArray($e, b) == -1; });
    };

    FACTS.getVariables = function(){
        var url = '/api/variable';
        var variables = {};
        $.ajax(url, {
            dataType: 'json',
            async: false,
            data: {"results_per_page": '500',
                "q": JSON.stringify({filters:[{name:"in_use",op:"eq",val:"true"}]}),
                "page": 1 },
                jsonp: false,
                contentType: "application/json",
                type: 'GET',
                success: function(response) {
                    variables = response.objects;
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    alert('An error has occurred when fetching variables.  Please alert the system administrator.\n' + errorThrown)
                }
        });
        return variables;
    };

    FACTS.getUnusedVariables = function(){
        var variables = FACTS.getVariables();
        var availableVariableIDs = $.map(variables, function(n){
            return n.id.toString();
        });
        var currentlyUsedVariableIDs = $.map($('.hidden-variable-id'), function(n){
            return $(n).attr('value');
        });
        var unusedVariableIDs = $.disjoin(availableVariableIDs, currentlyUsedVariableIDs);
        return $.map(variables, function(n){
            if ($.inArray(n.id.toString(),unusedVariableIDs) !== -1){
                return n;
            } else {
                return null;
            }
        });
    };

    $(function() {
        $(document).on('click','#AddVarToFact',function(){
            var compiledTemplate = Handlebars.getTemplate('edit-fact-new-variable');
            var variables = FACTS.getUnusedVariables();
            var inputs = $('table .controls > input')
            var varNums = $.map(inputs, function(n) {
                var varIDString = $(n).attr('id');
                return Math.floor(/-(\d+)-/.exec(varIDString)[1]);
            });
            maxID = Math.max.apply(Math, varNums);
            var index = maxID + 1;
            if (variables && variables.length > 0 ){
                $('#FactVariablesTable tr:last').after(compiledTemplate({variables: variables, index: index}));
                $('#FactVariablesTable tr:last select').chosen({allow_single_deselect: true});
            }else {
                $('#NoUnusedVarsModal').modal();
            }

        });

        $(document).on('change', '.variable-select', function() {
            var $newVarRow = $($(this).closest('tr'));
            var $dimension = $($newVarRow.children('td.dimension'));
            var $datatype = $($newVarRow.children('td.data-type'));
            var $controls = $($newVarRow.find('.controls'));
            var $input = $($controls.children('input'));
            var $varIDHiddenInput = $($controls.find('div > input'));
            if ($(this).children('option:selected').attr('value') !== '' ){
                var variableID = $(this).children('option:selected').attr('value');
                var variables = FACTS.getVariables();
                var currentVariable = $.map(variables, function(n) {
                    if (n.id == variableID){
                        return n;
                    } else {
                        return null;
                    }
                })[0];

                var dimensionName = currentVariable.dimension.name;
                var dimensionID = currentVariable.dimension.id;
                var dataType = currentVariable.dimension.data_type;
                $dimension.html("<a href='/dimensions/" + dimensionID + "/'>" + dimensionName + "</a>");
                $dimension.removeClass('muted');
                $datatype.text(dataType);
                $datatype.removeClass('muted');
                $input.removeAttr('disabled');
                $varIDHiddenInput.attr('value',variableID);
            } else {
                $dimension.text('Dimension');
                $dimension.addClass('muted');
                $datatype.text('Data Type');
                $datatype.addClass('muted');
                $input.attr('disabled', 'disabled');
                $varIDHiddenInput.attr('value','');
            }
        });

        $(document).on('click', 'input[type=submit]', function() {
            $.each($('td .controls > div > input'), function(index, value) {
                if( $(value).attr('value') === '' ){
                    // Remove id and name so it won't be processed on backend
                    // Doing it this way rather than removing the <tr> so the
                    // user doesn't see anything.
                    $(value).removeAttr('id');
                    $(value).removeAttr('name');
                    var $pairedInput = $($(value).closest('td').find('.controls > input'));
                    $pairedInput.removeAttr('id');
                    $pairedInput.removeAttr('name');
                }
            });

        });
    });
})(jQuery)
