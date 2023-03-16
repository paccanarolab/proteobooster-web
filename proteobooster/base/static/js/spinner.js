
var loadingAnimation = function(spinnerId, spinnerMessage){
	$(spinnerId).show();
	$(spinnerId).find('.spinnerMessage').html(spinnerMessage);
}

$(document).ready(function() {
	$('#spinnerWrapper').hide();
	$('#spinnerWrapperInterolog').hide();
});
