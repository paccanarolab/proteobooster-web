
var loadingAnimation = function(spinnerId, spinnerMessage){
	console.log('hmmm');
	$(spinnerId).show();
	$(spinnerId).find('.spinnerMessage').html(spinnerMessage);
}

$(document).ready(function() {
	$('#spinnerWrapper').hide();
	$('#spinnerWrapperInterolog').hide();
});