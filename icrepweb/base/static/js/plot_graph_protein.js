$(document).ready(function(){

   getNetwork(getNetworkUrl); 

});


var getNetwork = function(request_url){
    console.log({protein_id:CURR_ELEMENT_ID});
    $.ajax({
        url:request_url,
        type:'get',
        data:{protein_id:CURR_ELEMENT_ID},
        success: function(data, status, xhr) {
            network = data;
            plotNetwork(data);
        }

    
    });
};


var plotNetwork = function(data){
    var cy = cytoscape({
        container:$('#cy'),
        elements:data,
        layout: {
            name:'cola',
            //infinite:false,
            //random:false,
            //animate:true,

        },
        userZoomingEnabled:false, //this is very annoying with our layout
        style: [
            {
                selector:'node',
                style: {
                    'width':20,
                    'height':20,
                    label:'data(id)',
                    'text-valign':'center',
                    'color':'#000',
                    'background-color':'Gold'
                    
                }
            }, 
            {
                selector:'edge',
                style:{
                    'line-color':'data(c)'
                }
            }]

    });

};


