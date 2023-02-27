
//configuration variables

var LOAD_MORE_LIMIT = 40;

// these variables MUST BE SET in the particular template! 
// otherwise the binding will NOT be made
//
// This is very convoluted, but saves a ton of code repetition
//
// COMPLEX_SUCCESS
// COMPLEX_ERROR
// INTEROLOG_SUCCESS
// INTEROLOG_ERROR
// PROTEIN_SUCCESS
// PROTEIN_ERROR
// EXP_INTERACTION_SUCCESS
// EXP_INTERACTION_ERROR
// GO_TERM_SUCCESS
// GO_TERM_ERROR
//
// complex_offset
// interolog_offset
// protein_offset
// exp_interaction_offset
// go_term_offset
//
var complex_offset;
var interolog_offset;
var protein_offset;
var exp_interaction_offset;
var go_term_offset;

// these variables MUST be defined in the experimental interaction configuraition script
// EVIDENCE_SUCCESS
// EVIDENCE_ERROR
// evidence_offset

var evidence_offset;
var INCLUDE_TrEMBL; // TrEMBL is off by default

$(document).ready(function(){

    // bindings

    $(document).on('click', '#load-more-complexes', function(){
        loadMore(
            HOME_URL + '/api/lm/complex/',
            {
                filter:CURR_FILTER,
                offset:complex_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            COMPLEX_SUCCESS,
            COMPLEX_ERROR
        ); 
    });
    $(document).on('click', '#load-more-interactions', function(){
        loadMore(
            HOME_URL + '/api/lm/interaction/',
            {
                filter:CURR_FILTER,
                offset:exp_interaction_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            EXP_INTERACTION_SUCCESS,
            EXP_INTERACTION_ERROR
        ); 
    });
    $(document).on('click', '#load-more-interologs', function(){
        loadMore(
            HOME_URL + '/api/lm/interolog/',
            {
                filter:CURR_FILTER,
                offset:interolog_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            INTEROLOG_SUCCESS,
            INTEROLOG_ERROR
        ); 
    });
    $(document).on('click', '#load-more-proteins', function(){
        loadMore(
            HOME_URL + '/api/lm/protein/',
            {
                filter:CURR_FILTER,
                offset:protein_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            PROTEIN_SUCCESS,
            PROTEIN_ERROR
        ); 
    });
    $(document).on('click', '#load-more-goterms', function(){
        loadMore(
            HOME_URL + '/api/lm/goterm/',
            {
                filter:CURR_FILTER,
                offset:go_term_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            GO_TERM_SUCCESS,
            GO_TERM_ERROR
        ); 
    });
    // this is used only in the experimental interaction
    // page, which is why the variables are defined only there
    $(document).on('click', '#load-more-evidence', function(){
        loadMore(
            HOME_URL + '/api/lm/evidence/',
            {
                filter:CURR_FILTER,
                offset:evidence_offset,
                limit:LOAD_MORE_LIMIT,
                element_id:CURR_ELEMENT_ID,
                include_trembl:INCLUDE_TrEMBL
            },
            EVIDENCE_SUCCESS,
            EVIDENCE_ERROR
        ); 
    });
});


var loadMore = function(url,data,suc,err){
    $.ajax({
        url: url,
        data: data,
        type: 'get',
        success: suc,
        error: err
    });
};
