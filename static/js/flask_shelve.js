
function flask_shelve(idx,element) {
    if ($(element).attr("fstype")=="multichoice") {
	var collection=$(element).attr("fscol");
	var fsid=$(element).attr("fsid");
	var choices=$(element).attr("fschoices").split("|");
	var choicebox=jQuery("<div/>", {"id":collection+"_"+fsid,"fscol":collection,"class":"fsgroup"});
	for (choice of choices) {
	    var newlabel=jQuery("<label/>", {"for": collection+"_"+fsid, style: "padding-right:20px"});
	    newlabel.text(choice);
	    
	    var newbutton=jQuery('<input/>', {type: "radio", fsid: fsid, fscol: collection, name: collection+"_"+fsid,"fschoice": choice, "fsmeta":$(element).attr("fsmeta")});
	    newbutton.on('change', function() {
		register_value($(this));
	    });

	    newbutton.appendTo(choicebox);
	    newlabel.appendTo(choicebox);
	}
	choicebox.appendTo($(element));
    }    
}    

function initialize_values(collection) {
    var request_url=APP_ROOT+"/list/"+collection;
    $.ajax({url: request_url, type: 'GET', dataType: 'json',
	    beforeSend: function() {$(".fsgroup").css("border","2px solid orange");},
	    success: function(data,status,request) {
		$("input[fscol='"+collection+"']").each(function(id, elem) {
		    var checked = (data[$(elem).attr("fsid")]["annotation"]==$(elem).attr("fschoice"));
		    $(elem).prop("checked",checked);
		    if (checked) {
			var collection_id=collection+"_"+$(elem).attr("fsid")
			$(".fsgroup[id="+collection_id+"]").css("border","2px solid green");
		    }
							})
	    }, //success
//	    fail: function(error) {console.log("FAIL",collection,id);$("#"+collection+"_"+id).css("border","2px solid red");},
	    error: function(request,status,error) {console.log("FAIL",collection);$("#"+collection+"_"+id).css("border","2px solid red");},
	    timeout:3000});
    
}

function register_value(element) {

    var collection=element.attr("fscol");
    var id=element.attr("fsid");
    var new_val=element.attr("fschoice");
    var request_url=APP_ROOT+"/set/"+collection+"/"+id;
    $.ajax({url: request_url, data:{"value":JSON.stringify({"annotation":new_val, "meta":element.attr("fsmeta")})}, type: 'GET', dataType: 'json',
	    beforeSend: function() {$("#"+collection+"_"+id).css("border","2px solid orange");},
	    success: function(error) {$("#"+collection+"_"+id).css("border","2px solid green");},
	    fail: function(error) {$("#"+collection+"_"+id).css("border","2px solid red");},
	    error: function(request,status,error) {console.log("FAIL",collection,id,error);$("#"+collection+"_"+id).css("border","2px solid red");},
	    timeout:3000});
}

//   $("#yourcontainer").append("<input type='radio' name='myRadio' />");
  // }


    
  //   $.ajax({
  //       url: $APP_ROOT+path,
  //       data: $(frm).serialize(),
  //       type: 'POST',
  //       beforeSend: function() { $(resdiv).html('');$(resdiv).hide(); $('#loading').show(); },
  //       complete: function() { $('#loading').hide(); $(resdiv).show(); },
  //       success: function(response){
  //           dsearch_ajax_response(response,resdiv);
  //       },
  //       error: function(error){
  //           $(resdiv).html('Backend server timeout.');
  //           console.log("error, maybe timeout");
  //           console.log(error);
  //       },
  //       fail: function(error){
  //           $(resdiv).html('Backend server timeout.');
  //           console.log("fail, maybe timeout");
  //           console.log(error);
  //       },
  //       timeout:600000

  //   });


