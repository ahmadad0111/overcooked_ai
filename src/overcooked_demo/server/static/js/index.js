// Persistent network connection that will be used to transmit real-time data
var socket = io();

/* * * * * * * * * * * * * * * * 
 * Button click event handlers *
 * * * * * * * * * * * * * * * */

$(function() {
    $('#create').click(function () {
        params = arrToJSON($('form').serializeArray());
        params.layouts = [params.layout]
        data = {
            "params" : params,
            "game_name" : "overcooked",
            "create_if_not_found" : false
        };
        socket.emit("create", data);
        $('#waiting').show();
        $('#join').hide();
        $('#join').attr("disabled", true);
        $('#create').hide();
        $('#create').attr("disabled", true)
        $('#create-next').hide();
        $('#create-next').attr("disabled", true)
        $("#instructions").hide();
        $('#tutorial').hide();
    });
});

$(function() {
    $('#create-next').click(function () {
        params = arrToJSON($('form').serializeArray());
        params.layouts = [params.layout]
        data = {
            "params" : params,
            "game_name" : "overcooked",
            "create_if_not_found" : false
        };
        socket.emit("create-next", data);
        $('#waiting').show();
        $('#join').hide();
        $('#join').attr("disabled", true);
        $('#create').hide();
        $('#create').attr("disabled", true)
        $('#create-next').hide();
        $('#create-next').attr("disabled", true)
        $("#instructions").hide();
        $('#tutorial').hide();
    });
});

$(function(){
    $('[data-toggle="tooltip"]').tooltip({
      delay: { "show": 100, "hide": 100 } /* Adjust delay times here */
    });
});

$(function() {
    $('#join').click(function() {
        socket.emit("join", {});
        $('#join').attr("disabled", true);
        $('#create').attr("disabled", true);
    });
});

$(function() {
    $('#leave').click(function() {
        socket.emit('leave', {});
        $('#leave').attr("disabled", true);
    });
});

$(function() {
    $('#layout').change(function() {
        var layout = document.getElementById("layout").value;
        var agentMapping = window.config_data["layout_agent_mapping"];
        try {
            document.getElementById("playerOne").value = agentMapping[layout];
            // document.getElementById("playerOne").text = agentMapping[layout];
            $('#current-layout').html(layout)

        }
        catch(err) {document.getElementById("playerOne").value = window.config_data["layout_agent_mapping"][window.config_data["default_layout"]];console.log(err);}
    });
});

window.onload = function() {
    fetch('http://localhost:5000/get_config')
    .then(response => response.json())
    .then(json => {
        console.log(json);
        window.config_data = json.config_data;
    });
}


/* * * * * * * * * * * * * 
 * Qualtrics handlers    *
 * * * * * * * * * * * * */
// JavaScript logic to control Qualtrics iframe modal
function showQualtricsSurvey(url, next=null) {
    const modal = document.getElementById('qualtrics-modal');
    const iframe = document.getElementById('qualtrics-frame');
    iframe.src = url;  // dynamically set URL based on participant/layout
    modal.style.display = 'block';
    if(next){
        socket.emit('show_pregame_survey', {})
    }
}

function closeQualtricsSurvey() {
    const modal = document.getElementById('qualtrics-modal');
    const iframe = document.getElementById('qualtrics-frame');
    iframe.src = "";  // clear iframe to reset survey
    modal.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const closeBtn = document.getElementById('close-qualtrics');
    if (closeBtn) {
      closeBtn.addEventListener('click', closeQualtricsSurvey);
    }
  });
  

/* * * * * * * * * * * * * 
 * Socket event handlers *
 * * * * * * * * * * * * */

window.intervalID = -1;
window.spectating = true;

socket.on('waiting', function(data) {
    // Show game lobby
    $('#error-exit').hide();
    $('#waiting').hide();
    $('#game-over').hide();
    $('#instructions').hide();
    $('#tutorial').hide();
    $("#overcooked").empty();
    $('#lobby').show();
    $('#join').hide();
    $('#join').attr("disabled", true)
    $('#create').hide();
    $('#create').attr("disabled", true)
    $('#leave').show();
    $('#leave').attr("disabled", false);
    if (!data.in_game) {
        // Begin pinging to join if not currently in a game
        if (window.intervalID === -1) {
            window.intervalID = setInterval(function() {
                socket.emit('join', {});
            }, 1000);
        }
    }
});

socket.on('creation_failed', function(data) {
    // Tell user what went wrong
    let err = data['error']
    $("#overcooked").empty();
    $('#lobby').hide();
    $("#instructions").show();
    $('#tutorial').show();
    $('#waiting').hide();
    $('#join').show();
    $('#join').attr("disabled", true);
    $('#create').show();
    $('#create').attr("disabled", false);
    $('#create-next').show();
    $('#create-next').attr("disabled", false);
    $('#overcooked').append(`<h4>Sorry, game creation code failed with error: ${JSON.stringify(err)}</>`);
});

socket.on('start_game', function(data) {
    // Hide game-over and lobby, show game title header
    if (window.intervalID !== -1) {
        clearInterval(window.intervalID);
        window.intervalID = -1;
    }
    graphics_config = {
        container_id : "overcooked",
        start_info : data.start_info
    };
    window.spectating = data.spectating;
    document.getElementById("experiment-order").innerHTML = "<b>Layout Order:</b> " + data.start_info["experiment_order_disp"];

    let currentLayout = data.start_info.current_layout.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    $('#current-layout').html(currentLayout);
        $('#xaiAgentType').val(data.start_info["xaiAgentType"]);
    $('#error-exit').hide();
    $("#overcooked").empty();
    $('#game-over').hide();
    $('#lobby').hide();
    $('#waiting').hide();
    $('#join').hide();
    $('#join').attr("disabled", true);
    $('#create').hide();
    $('#create').attr("disabled", true)
    $("#instructions").hide();
    $('#tutorial').hide();
    $('#leave').show();
    $('#leave').attr("disabled", false)
    $('#game-title').show();
    $('#experiment-order').show();
    $('#experiment-order').attr("disabled", false)
    
    if (!window.spectating) {
        enable_key_listener();
    }
    
    graphics_start(graphics_config);
});

socket.on('reset_game', function(data) {
    graphics_end();
    if (!window.spectating) {
        disable_key_listener();
    }
    
    $("#overcooked").empty();
    $("#reset-game").show();
    setTimeout(function() {
        $("reset-game").hide();
        graphics_config = {
            container_id : "overcooked",
            start_info : data.state
        };
        if (!window.spectating) {
            enable_key_listener();
        }
        graphics_start(graphics_config);
    }, data.timeout);
});

socket.on('state_pong', function(data) {
    // Draw state update
    drawState(data['state']);
});

socket.on('end_game', function(data) {
    // Hide game data and display game-over html
    graphics_end();
    if (!window.spectating) {
        disable_key_listener();
    }
    $('#game-title').hide();
    $('#game-over').show();
    $("#join").show();
    $('#join').attr("disabled", true);
    if (data.data && !data.data.game_flow_on) {
        $("#create").show();
        $('#create').attr("disabled", false)
    } else {
        $("#create-next").show();
        $('#create-next').attr("disabled", false)
    }
    if (data.data && data.data.is_ending) {
        $("#create").show();
        $('#create').attr("disabled", true)

        $("#create-next").hide();
        $('#create-next').attr("disabled", true)
        // socket.emit('leave', {});
        window.alert("Please enter UID for the next player!!")
    }
    $("#instructions").show();
    $('#tutorial').show();
    $("#leave").hide();
    $('#leave').attr("disabled", true)
    
    // Game ended unexpectedly
    if (data.status === 'inactive') {
        $('#error-exit').show();
    }
    console.log(data)
    if(data.data && data.data.session_ended){
        let surveyURL = `${data.data.survey_baseurl}?round_d=${data.data.round_id}&player_Id=${data.data.player_id}&uid=${data.data.uid}&session_Id=${data.data.session_id}&xai_agent=${data.data.xaiAgentType}&layout=${data.data.layout}`;
        showQualtricsSurvey(surveyURL)
    }
    if(data.data && data.data.game_ended){
        let surveyURL = `${data.data.survey_baseurl}?round_d=${data.data.round_id}&player_Id=${data.data.player_id}&uid=${data.data.uid}&session_Id=${data.data.session_id}&xai_agent=${data.data.xaiAgentType}&layout=${data.data.layout}`;
        showQualtricsSurvey(surveyURL)
    }
});
    //    print( {"round_Id": current_round, "player_Id": user_id, "uid": session["user_id"], "session_Id": current_session, "xai_agent": params["xaiAgentType"], "layout": GAME_FLOW['all_layouts'][current_session-1]})
    //     #TODO: add post-session questionnaire popup
    //     emit(
    //         "show_survey",
    //         {"round_id": current_round, "player_id": user_id, "uid": session["user_id"], "session_id": current_session, "xai_agent": params["xaiAgentType"], "layout": GAME_FLOW['all_layouts'][current_session-1]},
    //         broadcast=True
    //         )

  
$(document).ready(function () {
  const showModal = $('#instruction-modal').data('show-modal');
  console.log(showModal)
  if (showModal === true || showModal === 'true') {
    $('#instruction-modal').fadeIn();  // Show modal
  }

  $('#close-instructions').on('click', function () {
    $('#instruction-modal').fadeOut();
  });
  // Optional: if you use a button to trigger the instructions later
  $('#show-instructions').on('click', function () {
    $('#instruction-modal').fadeIn();
  });
});
  
/* * * * * * * * * * * * * * 
 * Game Key Event Listener *
 * * * * * * * * * * * * * */

function enable_key_listener() {
    $(document).on('keydown', function(e) {
        let action = 'STAY'
        switch (e.which) {
            case 37: // left
                action = 'LEFT';
                break;

            case 38: // up
                action = 'UP';
                break;

            case 39: // right
                action = 'RIGHT';
                break;

            case 40: // down
                action = 'DOWN';
                break;

            case 32: //space
                action = 'SPACE';
                break;

            default: // exit this handler for other keys
                return; 
        }
        e.preventDefault();
        socket.emit('action', { 'action' : action });
    });
};

function disable_key_listener() {
    $(document).off('keydown');
};


/* * * * * * * * * * *
 * Utility Functions *
 * * * * * * * * * * */

var arrToJSON = function(arr) {
    let retval = {}
    for (let i = 0; i < arr.length; i++) {
        elem = arr[i];
        key = elem['name'];
        value = elem['value'];
        retval[key] = value;
    }
    return retval;
};
