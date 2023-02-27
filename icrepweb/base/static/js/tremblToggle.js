var toggleTrembl = function(handle){
	var redirUrl = window.location.origin + window.location.pathname;
		
	if($('#trembl-checkbox').prop('checked')){
		//if there are more variables than just the include_trembl one
		if(window.location.search.length > '?include_trembl=false'.length){
			redirUrl += window.location.search.replace('&include_trembl=false', '');
		}else{
			redirUrl += window.location.search.replace('?include_trembl=false', '');
		}
	}else{
		// go to version that includes trembl
		// if there are any variables, add ours
		if(window.location.search.length > 0){
			redirUrl += window.location.search + '&include_trembl=false';
		}else{
			redirUrl += '?include_trembl=false';
		}
	}
	window.location = redirUrl;
};

$(document).ready(function(){
   $('#trembl-checkbox').on( "change", toggleTrembl );
});
