var CURR_FILTER = 'organism';

var COMPLEX_SUCCESS = function(data, stat, xhr){
    addComplexes('#complexes-container', data);
    complex_offset += data.length;
    removeButtonIfNotRelevant('complexes', data);
};
var COMPLEX_ERROR = function(xhr, stat, err){};
var INTEROLOG_SUCCESS = function(data, stat, xhr){
    addInterologs('#interologs-container', data);
    interolog_offset += data.length;
    removeButtonIfNotRelevant('interologs', data);
};
var INTEROLOG_ERROR = function(xhr, stat, err){};
var PROTEIN_SUCCESS = function(data, stat, xhr){
    addProteins('#proteins-container', data);
    protein_offset += data.length;
    removeButtonIfNotRelevant('proteins', data);
};
var PROTEIN_ERROR = function(xhr, stat, err){};
var PROTEIN_3_COLS_SUCCESS = function(data, stat, xhr){
    addProteinItems("#protein_info-container", data);
    protein_item_offset += data.length;
    removeButtonIfNotRelevant('protein-items', data);
}
var PROTEIN_3_COLS_ERROR = function(xhr, stat, err){};
var EXP_INTERACTION_SUCCESS = function(data, stat, xhr){
    addExperimentalInteractions('#interactions-container', data);
    exp_interaction_offset += data.length;
    removeButtonIfNotRelevant('interactions', data);
};
var EXP_INTERACTION_ERROR = function(xhr, stat, err){};
var GO_TERM_SUCCESS = function(data, stat, xhr){
    addGOTerms('#goterms-container', data);
    go_term_offset += data.length;
    removeButtonIfNotRelevant('goterms', data);
};
var GO_TERM_ERROR = function(xhr, stat, err){};

$(document).ready(function(){
    complex_offset = $('.complex').length - 1;
    interolog_offset = $('.interolog').length - 1;
    protein_offset = $('.protein').length - 1;
    protein_item_offset = $('.protein_item').length - 1;
    exp_interaction_offset = $('.interaction').length - 1;
    go_term_offset = $('.go-term').length - 1;
});

