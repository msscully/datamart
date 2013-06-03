(function($){
  $(function(){
    $('#dm-fl-LabelWizard').on('finished', function(e, data) {
      $('#dm_fl_column_var').submit();
    });
    $('#btnWizardPrev').on('click', function() {
      $('#dm-fl-LabelWizard').wizard('previous');
    });
    $('#btnWizardNext').on('click', function() {
      $('#dm-fl-LabelWizard').wizard('next');
    });
    $('.btn-prev').on('click', function(){
      if($('#dm-fl-LabelWizard').wizard().data().wizard.currentStep == 1){
        $('#btnWizardPrev').attr('disabled','disabled');
      }
      else {
        $('#btnWizardPrev').removeAttr('disabled');
      }

      $('#btnWizardNext').val('Next');
    });
    $('.btn-next').on('click', function(){
      if($('#dm-fl-LabelWizard').wizard().data().wizard.currentStep == 1){
        $('#btnWizardPrev').attr('disabled','disabled');
      }
      else {
        $('#btnWizardPrev').removeAttr('disabled');
      }

      if ($("#dm-fl-FinalSubmit").text() === 'Submit'){
        $('#btnWizardNext').val('Submit');
      }
    });
  });
})(jQuery)
