var FACTS = {}; // FACTS Namespace

(function($){
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

  $(function() {
      $(document).on('click','#AddVarToFact',function(){
          var compiledTemplate = Handlebars.getTemplate('edit-fact-new-variable');
          var variables = FACTS.getVariables()
          $('#FactVariablesTable tr:last').after(compiledTemplate({variables: variables, index: 0}));
          $('#FactVariablesTable tr:last select').chosen();
      });
  });
})(jQuery)
