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

    FACTS.countBlankVarSelects = function(){
        var selects = $('td select.variable-select :selected')
        var blankCount = 0;
        $.each(selects, function(index, value) {
            if ($(value).attr('value') === ''){
                blankCount++;
            }
        });
        return blankCount;
    };

    $(function() {
        $(document).on('click','#AddVarToFact',function(){
            var compiledTemplate = Handlebars.getTemplate('edit-fact-new-variable');
            var variables = FACTS.getUnusedVariables();
            var inputs = $('table .controls > input')
            if (inputs.length > 0){
                var varNums = $.map(inputs, function(n) {
                    var varIDString = $(n).attr('id');
                    return Math.floor(/-(\d+)-/.exec(varIDString)[1]);
                });
            } else {
                varNums = [1];
            }
            var blankCount = FACTS.countBlankVarSelects();
            maxID = Math.max.apply(Math, varNums);
            var index = maxID + 1;
            // Don't allow adding variables if all variables have been used.
            if (variables && variables.length > 0 && variables.length > blankCount){
                $('#FactVariablesTable tr:last').after(compiledTemplate({variables: variables, index: index}));
                $('#FactVariablesTable tr:last select').chosen({allow_single_deselect: true});
            }else {
                $('#NoUnusedVarsModal').modal();
            }

        });

        $(document).on('change', '.variable-select', function() {
            var thisSelect = this;
            var $newVarRow = $($(thisSelect).closest('tr'));
            var $dimension = $($newVarRow.children('td.dimension'));
            var $datatype = $($newVarRow.children('td.data-type'));
            var $controls = $($newVarRow.find('.controls'));
            var $input = $($controls.children('input'));
            var $varIDHiddenInput = $($controls.find('div > input'));
            if ($(thisSelect).children('option:selected').attr('value') !== '' ){
                // New Variable selected.
                var variableID = $(thisSelect).children('option:selected').attr('value');
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

                // Remove the selected variable from other variable selects if
                // they exist.
                $('.variable-select option[value="' + variableID + '"]:not(:selected)').remove();
                $('.variable-select').trigger("liszt:updated");
            } else {
                // Variable selection cleared.
                $dimension.text('Dimension');
                $dimension.addClass('muted');
                $datatype.text('Data Type');
                $datatype.addClass('muted');
                $input.attr('disabled', 'disabled');
                $varIDHiddenInput.attr('value','');

                // Add the previously selected variable to other variable
                // selects if they exist.
                var variableSelects = $('.variable-select');
                if (variableSelects.length > 1){
                    thisOptions = $.map($(thisSelect).children('option'), function(value) {
                        return $(value).attr('value');
                    });
                    otherOptions = [];
                    $.each(variableSelects, function(index, varSelect) {
                        if(! $(varSelect).is($(thisSelect))){
                            var varSelectOptions = $.map($(varSelect).children('option'), function(value) {
                                return $(value).attr('value');
                            });
                            $.extend(otherOptions, varSelectOptions);
                        }
                    });
                    var idToAdd = $.disjoin(thisOptions, otherOptions);
                    var idToAddHtml = $(thisSelect).children('option[value="' + parseInt(idToAdd) + '"]').clone();
                    $.each(variableSelects, function(index, varSelect) {
                        if(! $(varSelect).is($(thisSelect))){
                            $(varSelect).append(idToAddHtml);
                        }
                    });
                    $('.variable-select').trigger("liszt:updated");
                }
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

        $(document).on('click', '.remove-fact', function() {
            // Remove row and renumber the input ids and names so they'll be
            // processed correctly on the backend.
            var $row = $($(this).closest('tr'));
            var $table = $($row.closest('table'));
            $row.remove();
            controls = $table.find('td .controls')
            $.each(controls, function(i,control) {
                var valueInput = $(control).children('input')
                var oldValueID = $(valueInput).attr('id');
                var newValueID = oldValueID.replace(/-\d+-/,'-'+i+'-');
                var oldValueName = $(valueInput).attr('name');
                var newValueName = oldValueName.replace(/-\d+-/,'-'+i+'-');
                $(valueInput).attr('id',newValueID);
                $(valueInput).attr('name',newValueName);
                var hiddenInput = $(control).find('div > input');
                var newHiddenID = $(hiddenInput).attr('id').replace(/-\d+-/,'-'+i+'-');
                var newHiddenName = $(hiddenInput).attr('name').replace(/-\d+-/,'-'+i+'-');
                $(hiddenInput).attr('id',newHiddenID);
                $(hiddenInput).attr('name',newHiddenName);
            });
        });
    });
})(jQuery)
