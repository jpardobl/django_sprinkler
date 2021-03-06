
function load_context(){
    send_url("{% url 'get_context' %}", function(data){show_context(data)})

}

function show_context(ctxt){
    $("#state").html(ctxt.state)
    $("#time").html(ctxt.time)
    if(ctxt.simulation)
        $("#simulation").html("Simulation: " + ctxt.simulation)
    else
        $("#simulation").remove()
    if(ctxt.jump > 0)
        $("#jump").html("Jump next " + ctxt.jump + " cicles")
    else
        $("#jump").html("")
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

            $("#toggle_manual_btn").css("cursor", "pointer")
            $(".program").css("cursor", "pointer")
            $("#cicle_btn").css("cursor", "pointer")
            $("#3min_cicle_btn").css("cursor", "pointer")
            $(".valve > a").css("cursor", "pointer")

            $("#toggle_manual_btn").removeClass("hidden")
            $("#cicle_btn").removeClass("hidden")
            $("#3min_cicle_btn").removeClass("hidden")
            break;
        case "automatic":
            $("#toggle_manual_btn").html("Automatic")
            $("#toggle_manual_btn").attr("title", "Change to Manual")
            $("#toggle_manual_btn").bind("click", function(){set_state('manual')})

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").prop("disable", true)

            $("#toggle_manual_btn").css("cursor", "pointer")
            $("#cicle_btn").css("cursor", "default")
            $("#3min_cicle_btn").css("cursor", "default")


            $("#toggle_manual_btn").removeClass("hidden")
            $("#cicle_btn").addClass("hidden")
            $("#3min_cicle_btn").addClass("hidden")

            break;
        case "3min_cicle":
            $("#toggle_manual_btn").prop("disable", true)

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").html("Stop 3min cicle")
            $("#3min_cicle_btn").bind("click", function(){set_state("manual")})
            $("#3min_cicle_btn").prop("disable", false)

            $("#toggle_manual_btn").css("cursor", "default")
            $(".program").css("cursor", "default")
            $("#cicle_btn").css("cursor", "default")
            $("#3min_cicle_btn").css("cursor", "pointer")
            $(".valve > a").css("cursor", "default")

            $("#toggle_manual_btn").addClass("hidden")
            $("#cicle_btn").addClass("hidden")
            $("#3min_cicle_btn").removeClass("hidden")


            break;
        case "cicle":
            $("#toggle_manual_btn").prop("disable", true)

            $("#cicle_btn").html("Stop cicle")
            $("#cicle_btn").bind("click", function(){set_state("manual")})
            $("#3min_cicle_btn").prop("disable", true)

            $("#toggle_manual_btn").css("cursor", "default")
            $(".program").css("cursor", "default")
            $("#cicle_btn").css("cursor", "pointer")
            $("#3min_cicle_btn").css("cursor", "default")
            $(".valve > a").css("cursor", "default")

            $("#toggle_manual_btn").addClass("hidden")
            $("#cicle_btn").removeClass("hidden")
            $("#3min_cicle_btn").addClass("hidden")


            break;
        case "running_program":
            $("#toggle_manual_btn").html("Manual")
            $("#toggle_manual_btn").attr("title", "Change to automatic")
            $("#toggle_manual_btn").bind("click", function(e){e.preventDefault();set_state('automatic')})

            $("#cicle_btn").prop("disable", true)
            $("#3min_cicle_btn").prop("disable", true)

            $("#toggle_manual_btn").css("cursor", "pointer")
            $("#cicle_btn").css("cursor", "default")
            $("#3min_cicle_btn").css("cursor", "default")


            $("#toggle_manual_btn").removeClass("hidden")
            $("#cicle_btn").addClass("hidden")
            $("#3min_cicle_btn").addClass("hidden")

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
            v.name = v.name.replace(/;/g, " <br>")
            $("#programs").append("<li class='list-group-item'><a i='"+ v.id+"' class='program label label-default' href='javascript:void(0)'>" + v.name+ "</a></li>")

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
            if(v[0].state)
                c = "success"
            var n = v[0].caption
            if(v[1] != null) n = v[0].caption + " - " + v[1] + "min"

            $("#valves").append("<li class='valve list-group-item'><a href='javascript:void(0)' i='"+ v[0].id+"' class='label label-"+c+"'>" + n + "</a></li>")
            delete n,c;
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