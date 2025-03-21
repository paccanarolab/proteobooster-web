var autocompleteError = function(data, statu, xhr){
    alert('something has gone wrong, please click OK and try again.');
}

var organismsCache = {};

var proteinCache = {};

$(document).ready(function() {
    $('#organism-search').autocomplete({
        delay: 0,
        minLength: 1,
        source: function(request, response) {
            var term = request.term;
            if( term in organismsCache ){
                response(organismsCache[term]);
                return;
            }
            $.ajax({
                url: HOME_URL + '/api/organisms',
                datatype: 'json',
                data: {
                    term: request.term,
                },
                success: function(data) {
                    organismsCache[ term ] = data;
                    response(data);
                },
                error: autocompleteError
            });
        }
    });

    $('.protein-search').autocomplete({
        delay:0,
        minLength:1,
        source: function(request, response) {
            var term = request.term;
            if( term in proteinCache ){
                response(proteinCache[term]);
                return;
            }
            $.ajax({
                url: HOME_URL + '/api/proteins',
                datatype: 'json',
                type: 'GET',
                data: {
                    term: request.term,
                    include_trembl: INCLUDE_TrEMBL,
                },
                success: function(data) {
                    proteinCache[ term ] = data;
                    response(data);
                },
                error: autocompleteError
            });
        },
        select: function(event, ui){
            $("#protein-search-input").val(ui.item.display); 
            $("#protein-accession").val(ui.item.elem); 
            return false;
        }
    })
    .autocomplete("instance")._renderItem = function(ul, item) {
        return $("<li>")
            .append(`<div>${item.display}</div>`)
            .appendTo(ul);
    };

    $( "form" ).submit(function( event ) {
        loadingAnimation('#spinnerWrapper', 'loading organism: ' + $('#organism-search').val());
    });

    $( "#search-interaction" ).submit(function( event ) {
        event.preventDefault();
        var protein1 = $('#interaction-prot-1').val();
        var protein2 = $('#interaction-prot-2').val();
        newLocation = HOME_URL + '/interaction';
        newLocation += '/' + protein1;
        newLocation += '/' + protein2;
        loadingAnimation('#spinnerWrapper', 'searching for an interaction involving <strong>' + protein1 + '</strong> and <strong>' + protein2 + '</strong>');
        window.location = newLocation;
    });

    $( "#search-interolog" ).submit(function( event ) {
        event.preventDefault();
        var protein1 = $('#interolog-prot-1').val();
        var protein2 = $('#interolog-prot-2').val();
        newLocation = HOME_URL + '/interolog';
        newLocation += '/' + protein1;
        newLocation += '/' + protein2;
        loadingAnimation('#spinnerWrapperInterolog', 'searching for an interolog involving <strong>' + protein1 + '</strong> and <strong>' + protein2 + '</strong>');
        window.location = newLocation;
    });


});

