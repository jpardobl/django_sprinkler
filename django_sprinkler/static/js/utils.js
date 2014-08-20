function doload_dom_script(url, id){
	var d = document;
	var s = d.createElement('script');
	s.src = url;
	s.type="text/javascript";
	s.id = id
	d.getElementsByTagName('head')[0].appendChild(s);
	delete d, s;
}

function doload_dom_css(url, id){
	var d = document
	var c = d.createElement('link')
	c.href = url
	c.rel = "stylesheet"
	c.type="text/css"
	c.id = id
	d.getElementsByTagName('head')[0].appendChild(c)
	delete d, c;
}


function load_dom_script_once(url, css){


	if( css == undefined){
		id = 'js_'+url.replace(/\//g,"").replace(/_/g,"").replace(/\./g, "")
		if(window.console)console.log("script "+id+"found: " + $("#"+id).length)
		if($("#"+id).length) return;
		if(window.console)console.log("Cargamos el script/css " + url)
		doload_dom_script(url, id);
		return
	}
	id = 'css_'+url.replace(/\//g,"").replace(/_/g,"").replace(/\./g, "")
	if($("#"+id).length) return;
	if(window.console)console.log("Cargamos el script/css " + url)
	doload_dom_css(url, id)
}

function init_progress(){
    var z = $("#left_col")
    $("#prog").remove()
    $("#avisos").remove()

    z.append("<div id='prog' class=\"progress\"><div id=\"progress\" class=\"progress-bar\" aria-valuenow=\"0\" aria-valuemin=\"0\" aria-valuemax=\"100\" style=\"width: 0%;\"></div></div>")
    delete z;
}

function progress(p){


    $("#progress").css( "width", p + "%")
}

function drop_progress(){

    setTimeout("$('#prog').fadeOut('slow')", 800)

}

function show_msg(msg, type){
    if(type == undefined) type = "danger"
    var z = $("#left_col")

    $("#avisos").remove()
    z.append("<div style='display:none' class='alert alert-"+type+"' id='avisos'><button type='button' class='close' aria-hidden='true'>&times;</button>" + msg + "</div>")
    $("#avisos").fadeToggle('slow')
    $('#avisos').bind('closed', function () {
            $("#avisos").remove()
        })
    delete z
}

function load_url(selector, url, data){
    init_progress();
    $.ajax({
        url: url,
        data: data,
        beforeSend: function(){progress(30)},
        success: function(data){progress(60);$(selector).html(data);progress(90)},
        complete: function(){$("[title!=undefined]").tooltip({"animation": "true"});progress(100)},
        error: function(ob){show_msg(ob.responseText)}
        });
   drop_progress();

}

function send_url(url, fun, data){
   init_progress();
   $.ajax({
    url: url,
    data: data,
    beforeSend: function(){progress(30)},
    success: fun,
    complete: function(){$("[title!=undefined]").tooltip({"animation": "true"});progress(100)},
    error: function(ob){show_msg(ob.responseText)}
   });

   drop_progress();
}
