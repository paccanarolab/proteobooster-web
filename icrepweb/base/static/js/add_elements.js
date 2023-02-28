
var addExperimentalInteractions = function(containerSelector, data, parentAccession, includeOrgName = false, includeQuality=false){
    var elementClass = 'interaction interaction';
    if(includeQuality && includeOrgName)
        elementClass += '-4columns';
    else if(includeQuality || includeOrgName)
        elementClass += '-3columns';
    else
        elementClass += '-2columns';
    $.each(data, function(i, item){
        $(containerSelector).append(
            `<a href="${getUrl('interaction', {first:item.first, second:item.second})}"
                class="${elementClass}">
                ${includeOrgName? `<div class="interaction-organism_name">${item.organism_name}</div>`:''}
                ${includeQuality? `<div class="interaction-quality">${item.quality}</div>`:''}
                <div class="interaction-interactor">${item.first} - ${item.first_description}</div>
                <div class="interaction-interactor">${item.second} - ${item.second_description}</div>
             </a>
            `);
    });
};

var addInterologs = function(containerSelector, data, includeOrgName = false){
    var elementClass = 'interolog interolog';
    if(includeOrgName)
        elementClass += '-4columns';
    else
        elementClass += '-3columns';
    $.each(data, function(i, item){
        $(containerSelector).append(
            `
            <a href="${getUrl('interolog', {first: item.first, second: item.second})}"
               class="${elementClass}">
                ${includeOrgName? `<div class="interolog-name">${item.organism_name}</div>`:''}
                <div class="interolog-quality">${item.quality}</div>
                <div class="interolog-interactor">${item.first} - ${item.first_description}</div>
                <div class="interolog-interactor">${item.second} - ${item.second_description}</div>
            </a>
            `);
    });
};

var addEvidence = function(containerSelector, data){
    $.each(data, function(i, item){
        $(containerSelector).append(
            `<a href='http://www.ncbi.nlm.nih.gov/pubmed/${item.pubmed_id}'
                class="evidence">
                <div class="evidence-pubmed_id">${item.pubmed_id}</div>
                <div class="evidence-interaction_type">${item.interaction_type}</div>
                <div class="evidence-detection_method">${item.detection_method}</div>
             </a>
            `);
    });
};

var addComplexes = function(containerSelector, data, includeScore = false){
    $.each(data, function(i, item){
        $(containerSelector).append(
            `<a href="${getUrl('complex', item.id)}"
                class="complex">
                ${includeScore? `<div class="predicted-complex-pvalue">${item.pvalue}</div>`:''}
                <div class="complex-size">${item.size}</div>
                <div class="complex-proteins">${item.proteins.slice(0,10).join(' ')}</div>
             </a>
            `);
    });
};

var addProteinItems = function(containerSelector, data){
    $.each(data, function(i, item){
        $(containerSelector).append(
            `<a href="${getUrl('protein', item.accession)}"
                class="protein_item protein_item-3columns">
                <div class="protein_item-accession">${item.accession}</div>
                <div class="protein_item-entry_name">${item.entry_name}</div>
                <div class="protein_item-description">${item.description}</div>
            </a>
            `);
    });
};

var addProteins = function(containerSelector, data){
    $.each(data, function(i, item){
        $(containerSelector).append(
            `<a href="${getUrl('protein', item.accession)}"
                class="protein">${item.accession}</a>
            `);
    });
};

var addGOTerms = function(containerSelector, data){
    $.each(data, function(i, item){
        $(containerSelector).append(
            `
            <a href="${getUrl('go_term', item.id)}">
                <div class="go_term-go_id">${item.go_id}</div>
                <div class="go_term-function">${item.function}</div>
            </a>
            `
        );
    });
};


var removeButtonIfNotRelevant = function(element, data){
    var id = '#load-more-' + element;
    if(data.length < LOAD_MORE_LIMIT){
        $(id).remove();
    }
}


$(document).ready(function(){
});
