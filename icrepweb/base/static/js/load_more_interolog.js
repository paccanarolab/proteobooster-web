var CURR_FILTER = 'interolog';

var COMPLEX_SUCCESS = function(data, stat, xhr){
    addComplexes('#complexes-container', data);
    complex_offset += data.length;
    removeButtonIfNotRelevant('complexes', data);
};
var COMPLEX_ERROR = function(xhr, stat, err){};
var INTEROLOG_SUCCESS = function(data, stat, xhr){
    addInterologs('#interologs-container', data, true);
    interolog_offset += data.length;
    removeButtonIfNotRelevant('interologs', data);
};
var INTEROLOG_ERROR = function(xhr, stat, err){};
var PROTEIN_SUCCESS = function(data, stat, xhr){};
var PROTEIN_ERROR = function(xhr, stat, err){};
var EXP_INTERACTION_SUCCESS = function(data, stat, xhr){
    addExperimentalInteractions('#interactions-container', data, null, true, true);
    exp_interaction_offset += data.length;
    removeButtonIfNotRelevant('interactinos', data);
};
var EXP_INTERACTION_ERROR = function(xhr, stat, err){};
var GO_TERM_SUCCESS = function(data, stat, xhr){};
var GO_TERM_ERROR = function(xhr, stat, err){};
var EVIDENCE_SUCCESS = function(data, stat, xhr){
    addEvidence('#evidence-container', data);
    evidence_offset += data.length;
    removeButtonIfNotRelevant('evidence', data);
};
var EVIDENCE_ERROR = function(xhr, stat, err){};


$(document).ready(function(){
    complex_offset = $('.complex').length - 1;
    interolog_offset = $('.interolog').length - 1;
    protein_offset = $('.protein').length - 1;
    exp_interaction_offset = $('.interaction').length - 1;
    go_term_offset = $('.go-term').length - 1;
    evidence_offset = $('.evidence').length - 1;
});

