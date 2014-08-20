
function load_context(){
    send_url("{% url 'get_context' %}", function(data){show_context(data)})

}

function show_context(ctxt){
    $("#state").html(ctxt.state)
    $("#time").html(ctxt.time)
    load_programs(ctxt)
    load_valves(ctxt)
    toggle_buttons(ctxt)
}

function toggle_buttons(ctxt){


    $("#3min_cicle_btn").unbind()
    $("#toggle_manual_btn").unbind()
    $("#cicle_btn").unbind()

    $("#3min_cicle_btn").html("3min cicle")
    $("#cicle_btn").html("Cicle")

    $(".valve > a").unbind()
    $(".program > a").unbind()

    switch(ctxt.state){
        case "manual":
            $("#toggle_manual_btn").html("Manual")
            $("#toggle_manual_btn").attr("title", "Change to automatic")
            $("#toggle_manual_btn").bind("click", function(e){e.preventDefault();set_state('automatic')})

            $(".program").bind("click", function(){activate_program(this)})
            $(".valve > a").bind("click", function(){toggle_valve(this)})

            $("#3min_cicle_btn").prop("disable", false)
            $("#3min_cicle_btn").bind("click", function(){set_state('3min_cicle')})

            $("#cicle_btn").prop("disable", false)
            $("#cicle_btn").bind("click", function(){set_state('cicle')})
            break;
        case "automatic":
            $("#toggle_manual_btn").html("Automatic")
            $("#toggle_manual_btn").attr("title", "Change to Manual")
            $("#toggle_manual_btn").bind("click", function(){set_state('manual')})

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").prop("disable", true)

            break;
        case "3min_cicle":
            $("#toggle_manual_btn").prop("disable", true)

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").html("Stop 3min cicle")
            $("#3min_cicle_btn").bind("click", function(){set_state("manual")})
            $("#3min_cicle_btn").prop("disable", false)
            break;
        case "cicle":
            $("#toggle_manual_btn").prop("disable", true)

            $("#cicle_btn").html("Stop cicle")
            $("#cicle_btn").bind("click", function(){set_state("manual")})
            $("#3min_cicle_btn").prop("disable", true)

            break;
        case "running_program":
            $("#toggle_manual_btn").html("Manual")
            $("#toggle_manual_btn").attr("title", "Change to automatic")
            $("#toggle_manual_btn").bind("click", function(e){e.preventDefault();set_state('automatic')})

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").prop("disable", true)

            break;
    }

}

function load_programs(ctxt){

    var programs = $("#programs")
    if(programs.length == 0 )
        programs = document.createElement("ul")
    else
        programs.html("")

    $(programs).addClass("list-group")
    $.each(ctxt.programs,
        function(k, v){
            $("#programs").append("<li class='list-group-item'><a i='"+ v.id+"' class='program label label-default' href='javascript:void(0)'>" + v.name+ "</a></li>")
            //console.log(v)
        })
    delete programs;
    console.log(ctxt.active_program)
    $(".program[i='" + ctxt.active_program+"']").addClass("label-success")
    $(".program[i='" + ctxt.active_program+"']").removeClass("label-default")
}

function load_valves(ctxt){
    var valves = $("#valves")
    if(valves.length == 0 )
        valves = document.createElement("ul")
    else
        valves.html("")

    $(valves).addClass("list-group")
    $.each(ctxt.valves,
        function(k, v){
            var c = "default"
            if(v.state)
                c = "success"
            $("#valves").append("<li class='valve list-group-item'><a href='javascript:void(0)' i='"+ v.id+"' class='label label-"+c+"'>" + v.caption+ "</a></li>")
            //console.log(v)
        })
    delete valves;
}

function activate_program(e){
    var $t = $(e)
    send_url("{% url 'activate_program' %}" + $t.attr("i"), function(data){show_context(data)})
    delete $t;
}

function toggle_valve(e){
    var $t = $(e)
    send_url("{% url 'toggle_valve' %}" + $t.attr("i"), function(data){show_context(data)})
    delete $t;
}

function set_state(new_state){
    send_url("{% url 'set_state' %}" + new_state, function(data){show_context(data)})
}