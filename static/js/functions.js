//Javascript functions for pystump
//This file is loaded on every page

$.extend($.expr[':'], {
    'containsi': function(elem, i, match, array)
    {
        return ((elem.textContent || elem.innerText || '') + (elem.title || '')).toLowerCase()
            .indexOf((match[3] || "").toLowerCase()) >= 0;
    }
});

var default_dialog_options = {
    width : "90%",
    modal : true
}

function show_popup_form(data){
    default_dialog_options.title = $(data).attr("title");
    $("#_dialog_").html(data).dialog(default_dialog_options);
    initialize_form($("#_dialog_").find('FORM'));
    $("TEXTAREA.ckedit").each(function(i, el){
        CKEDITOR.replace(el.id);
        // trigger a change on color inputs
        $("input[type=color]").each(function(i, el){
            $(el).trigger("change");
        });
    });
}

function initialize_form(form){
    var $form = $(form);

    //Date/Datetime/time inputs
    var date_display_fmt = "m/d/yy";
    var time_display_fmt = "h:mm tt";

    $form.find(":input[type=datetime], :input[type=date], :input[type=time]").each(function(i, el){
        var $input = $(el);
        var widget = $input.attr("type") + "picker";
        var altfield_id = $input.data("altfield");
        var dateval = $input.val()? new Date($input.val()) : null;

        $input[widget]({
            altField: "#" + altfield_id,
            altFormat: "yy-mm-dd",
            altTimeFormat: "HH:mm",
            altSeparator: "T",
            altFieldTimeOnly: false,
            timeFormat: time_display_fmt,
            dateFormat: date_display_fmt,
            constrainInput: true,
            parse: 'loose'
        });

        $input[widget]('setDate', dateval);

        //datetimepicker doesn't automatically clear the altField when its field is cleared.

        $input.on("change", function(){
            if ($input.val().trim() === ''){
                $("#" + altfield_id).val('');
            }
        });
    });


}

function fit_el_to_page(el) {
    var target_height =  window.innerHeight - $("NAV").outerHeight();
    var numbreaks = $(el +" > br").size() +1;
    var target_width = window.innerWidth * .95;
    var line_size = target_height / numbreaks;
    var font_size = line_size;
    //$(el).css("line-height", line_size+"px");
    $(el).css("white-space", "nowrap");
    $(el).css("font-size", font_size+"px");
    //console.log("Area WxH: ", $(el)[0].scrollWidth, $(el)[0].scrollHeight);
    //The basic concept here is to shrink the text by 10% until the scrollwidth is less than the target width, and scrollheight likewise.
    //This would indicate a lack of scrollbars.
    while (($(el)[0].scrollWidth > target_width || $(el)[0].scrollHeight > target_height) && font_size > 12){
        //	console.log(font_size);
        font_size *= .9;
        $(el).css("font-size", font_size+"px");

        //console.log("fontsize: ", font_size, "; Line height: ", line_size, "; Div target W,H: ", target_width, target_height, "; Div scroll W, H: ", $(el)[0].scrollWidth, $(el)[0].scrollHeight);
    }
    $(el).width($(el)[0].scrollWidth);
}

function show_current_page(){
    var cp = document.current_page;
    var duration = parseInt(cp.attr("data-duration"), 10);
    body = $("#content");
    body.css("background", cp.attr("data-bg"));
    body.css("color", cp.attr("data-fg"));
    cp.css("height", "100%");
    $("#title").html(cp.attr("data-title"));
    meta_text = (Show_Updated && ("Updated " + cp.attr("data-updated") + ' ') || ' ') + (Show_Author && ("By " + cp.attr("data-author")) || '');
    $("#meta").html(meta_text);
    cp.show();
    fit_el_to_page("#" + cp.attr("id"));
    setTimeout(function(){
        document.current_page = cp.next();
        if (document.current_page.length === 0){
            //reload the slides
            $.get(
                document.basepath.replace(/\/$/, '') + "/slides",
                function(data){
                    $("#announcements").html(data);
                    document.current_page = $("#announcements .announcement_display:first");
                    cp.hide();
                    show_current_page();
            });
        }else{
            cp.hide();
            show_current_page();
        }
    }, duration * 1000);
}

$(document).ready(function(){
    $("_dialog_").hide();
    $("#search").focus();
    $("#search").keyup(function(){
        var term = $(this).val();
        if (term.length > 0){
            $(".announcement_item").hide();
            $(".announcement_item:containsi("+term+")").show();
        }else{
            $(".announcement_item").show();
        }
    });

    //make the main page LI's clickable
    $("#announcement_list > LI").click(function(){
        var id = $(this).attr("data-id");
        $.get(document.basepath + "edit/"+id, function(data){
            show_popup_form(data);
        });
        return false;
    });

    //ANNOUNCEMENT EDITING
    //New entry button
    $(document).on("click", "#new_announcement A", function(){
        $.get(document.basepath + "edit", function(data){
            show_popup_form(data);
        });
    });

    $(document).on("ignore", "#announcement_form", function(e){
        //e.preventDefault();
        //make sure dates and datetimes are ISO format
        $("input[type=date],input[type=datetime]").each(function(i, el){
            var $input = $(el);
            var type = $input.attr('type');
            var value = $input[type + 'picker']('getDate');
            var formatted_value = (
                $.datepicker.formatDate($.datepicker.ISO_8601, value) +
                    ' ' +
                    $.datepicker.formatTime('HH:mm', value)
            );
            $input.val(formatted_value);
        });

        return e;
    });

    $(document).on('change', 'input[name=fg_color],input[name=bg_color]', function(e){
        //make the CKEDITOR reflect the changes.

        var editor_doc = CKEDITOR.instances.announcement_content_textarea.document.getBody()["$"];
        var $this = $(this);
        if ($this.attr("name") === "fg_color"){
            editor_doc.style["color"] = $this.val();
        }else{
            editor_doc.style["background-color"] = $this.val();
        }
    });

    //SETTINGS
    //Show the settings dialog
    $(document).on("click", "#link_settings", function(event){
        $.get(document.basepath + "/settings", function(data){
            show_popup_form(data);
        });
    });

    //submit settings
    $(document).on("submit", "#settings_form", function(e){
        e.preventDefault();
        var data = $(this).serialize();
        $.post(
            $(this).attr("action"),
            data,
            function(){
                $("#_dialog_").dialog("close");
            }
        )
        return false;
    });

    //INITIALIZE
    //Call the initialize form
    $(document).on("click", "#link_initialize", function(event){
        event.preventDefault();
        $.get(document.basepath + "/initialize", function(data){
            show_popup_form(data);
            $("#initialize_form INPUT[type=submit]").attr("disabled", 1);
            $(document).on("change", "#init_db", function(){
                if ($(this).is(":checked")){
                    $("#initialize_form INPUT[type=submit]").removeAttr("disabled");
                }else{
                    $("#initialize_form INPUT[type=submit]").attr("disabled", 1);
                }
            });
        });
    });
    //Handle submit
    $(document).on("submit", "#initialize_form", function(event){
        event.preventDefault();
        var location = window.location;
        var formdata = $(this).serialize();
        $.post($(this).attr("action"), formdata, function(){
            window.location = location;
            window.location.reload();
        })
        return false
    });

    //Displaying the announcements on the main page
    $("#announcements .announcement_display").hide();
    document.current_page = $("#announcements .announcement_display:first");
    if(document.current_page.length > 0){
        show_current_page();
    }
});
