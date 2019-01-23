function download_tsv() {
    var minSL = $("#min_seq_len").val();
    var maxSL = $("#max_seq_len").val();
    var filterP = $("#checkPaired").is(":checked");
    var minA = $("#min_A_value").val();
    var minT = $("#min_T_value").val();
    var minG = $("#min_G_value").val();
    var minC = $("#min_C_value").val();
    var maxA = $("#max_A_value").val();
    var maxT = $("#max_T_value").val();
    var maxG = $("#max_G_value").val();
    var maxC = $("#max_C_value").val();
    var pairedRP = $("#paired_read_percentage").val();
    window.location.href = "http://127.0.0.1:5000/api/export_tsv?minSL=" + minSL + "&maxSL=" + maxSL + "&filterP=" + filterP + "&minA=" + minA +
        "&minT=" + minT + "&minG=" + minG + "&minC=" + minC + "&maxA=" + maxA + "&maxT=" + maxT + "&maxG=" + maxG + "&maxC=" + maxC + "&pairedRP=" + pairedRP;

}

// TODO: implement this method for the number input fields
//function checkInp(input_list) {
//    input_list.forEach(function (s) {
//        if (isNaN(x)) {
//            alert("Must input numbers");
//            return false;
//        }
//    })
//    return true;
//}

function clear_errors() {
    $(".image_error").html("");

}

function disable_buttons() {
    $(function(){
        $( ".action_button" ).prop("disabled", true);
    });
}

function enable_buttons() {
    $(function(){
        $( ".action_button" ).prop("disabled", false);
    });
}

function make_seq_image() {
    clear_errors();
    disable_buttons();
    var min_seq_len = $( "#min_seq_len" ).val();
    var max_seq_len = $( "#max_seq_len" ).val();

    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/api/sequence",
        data: {"min_seq_len": min_seq_len, "max_seq_len": max_seq_len},
        statusCode: {
            400: function () {
                $("#sequence_error").html("No known records are loaded, please make sure you uploaded your files in this session");
            },
            404: function () {
                $("#sequence_error").html("Not found, please report this error to the developers");
            },
            500: function () {
                $("#sequence_error").html("Internal server error, please contact the developers");
            }
        },
        success: function (response) {
            $("#sequenceImage").css("height", "370px");
            visualizeSequenceLength(JSON.parse(response));
        }
    });
}

function make_paired_image() {
    clear_errors();
    disable_buttons();
    var filter_paired = $( "#checkPaired").is(":checked");
  
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/api/paired",
        data: {"FilterPaired": filter_paired},
        statusCode: {
            400: function () {
                $("#paired_error").html("No known records are loaded, please make sure you uploaded your files in this session");
            },
            404: function () {
                $("#paired_error").html("Not found, please report this error to the developers");
            },
            500: function () {
                $("#paired_error").html("Internal server error, please contact the developers");
            }
        },
        success: function(response){
            $( "#pairsImage" ).css("height","370px");
            visualizePairedReads(JSON.parse(response));
        }
    });
}

function make_nucleotide_image() {
    clear_errors();
    disable_buttons();
    var min_A_value = $( "#min_A_value" ).val();
    var min_T_value = $( "#min_T_value" ).val();
    var min_G_value = $( "#min_G_value" ).val();
    var min_C_value = $( "#min_C_value" ).val();
    var max_A_value = $( "#max_A_value" ).val();
    var max_T_value = $( "#max_T_value" ).val();
    var max_G_value = $( "#max_G_value" ).val();
    var max_C_value = $( "#max_C_value" ).val();
    var bin_size = $( "#nucleotide_bin_size" ).val();

    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/api/nucleotide",
        data: {
            "minAValue": min_A_value, "minTValue": min_T_value, "minGValue": min_G_value, "minCValue": min_C_value,
            "maxAValue": max_A_value, "maxTValue": max_T_value, "maxGValue": max_G_value, "maxCValue": max_C_value,
            "BinSize": bin_size
        },
        statusCode: {
            400: function () {
                $("#nucleotide_error").html("No known records are loaded, please make sure you uploaded your files in this session");
            },
            404: function () {
                $("#nucleotide_error").html("Not found, please report this error to the developers");
            },
            500: function () {
                $("#nucleotide_error").html("Internal server error, please contact the developers");
            }
        },
        success: function (response) {
            $("#fwNucleotideImage").css("height", "370px");
            $("#rvcNucleotideImage").css("height", "370px");
            var combined = JSON.parse(response);
            var fw_json = combined.fw_json;
            var rvc_json = combined.rvc_json;
            visualizeNucleotidePercentages(fw_json, "fwNucleotideImage", "Forward Clustered Nucleotide Percentage");
            visualizeNucleotidePercentages(rvc_json, "rvcNucleotideImage", "Reverse Clustered Nucleotide Percentage");
        }
    });
}

function calculate_identity(){
    clear_errors();
    disable_buttons();
    $.ajax({
    type: "POST",
    url: "http://127.0.0.1:5000/api/calc_identity",
    statusCode: {
            400: function(){
                $("#identity_error").html("No known records are loaded, please make sure you uploaded your files in this session");
                $("#load_identity").hide();
            },
            404: function(){
                $("#identity_error").html("Not found, please report this error to the developers");
                $("#load_identity").hide();
            },
            500: function(){
                $("#identity_error").html("Internal server error, please contact the developers");
                $("#load_identity").hide();
            }
    },
    success: function(response){
        if (response == "True"){
        $("#identity_succes").html("Identity successful calculated");
        }
        else{
        $("#identity_succes").html("Identity already calculated");
        }
        $("#load_identity").hide();
    }
    });
}

function make_identity_image() {
    clear_errors();
    disable_buttons();
    var pairedReadPercentage = $("#paired_read_percentage").val()
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/api/identity",
        data: {"paired_read_percentage": pairedReadPercentage},
        statusCode: {
            400: function () {
                $("#identity_error").html("No known records are loaded, please make sure you uploaded your files in this session");
            },
            404: function () {
                $("#identity_error").html("Not found, please report this error to the developers");
            },
            500: function () {
                $("#identity_error").html("Internal server error, please contact the developers");
            }
        },
        success: function(response){
            $( "#identityImage" ).css("height","370px");
            forwardReverseCompare(JSON.parse(response));
        }
    });
}

function run_diamond() {
    var maxTargetSeqs = $("#max-target-seqs").val();
    var evalue = $("#evalue").val();
    var sensitive = $("#sensitive").is(":checked");
    var moreSensitive = $("#more-sensitive").is(":checked");
    var frameshift = $("#frameshift").val();
    var gapOpen = $("#gapopen").val();
    var gapExtend = $("#gapextend").val();
    var matrix = $("#matrix").val();
    var algorithm = $("#algorithm").val();
    var outfmt = $("#outfmt").val();
    var compress = $("#compress").val();
    var minScore = $("#min-score").val();
    var id = $("#id").val();
    var queryCover = $("#query-cover").val();
    var subjectCover = $("#subject-cover").val();
    var maxHSPS = $("#max-hsps").val();

    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/api/diamond",
        data: {
            "maxTargetSeqs": maxTargetSeqs, "evalue": evalue, "sensitive": sensitive, "moreSensitive": moreSensitive,
            "frameshift": frameshift, "gapOpen": gapOpen, "gapExtend": gapExtend, "matrix": matrix,
            "algorithm": algorithm, "outfmt": outfmt, "compress": compress, "minScore": minScore, "id": id,
            "queryCover": queryCover, "subjectCover": subjectCover, "maxHSPS": maxHSPS
        },
        statusCode: {
            400: function () {
                $("#diamond_error").html("No known records are loaded, please make sure you uploaded your files in this session");
                $("#load_identity").hide();
            },
            404: function () {
                $("#diamond_error").html("Not found, please report this error to the developers");
                $("#load_identity").hide();
            },
            500: function () {
                $("#diamond_error").html("Internal server error, please contact the developers");
                $("#load_identity").hide();
            }
        },
        success: function (response) {
            // TODO: Handle repsonse
            console.log(response);

        }
    });
}
