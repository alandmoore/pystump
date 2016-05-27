//Javascript functions for PyStump
//Assumes jQuery, jQuery-UI


/////////////////////////////////////
// Utilities and jQuery extensions //
/////////////////////////////////////


//Case-insensitve :contains operator for jQuery selectors

$.extend($.expr[':'], {
    'containsi': function(elem, i, match, array)
    {
        return ((elem.textContent || elem.innerText || '') + (elem.title || '')).toLowerCase()
            .indexOf((match[3] || "").toLowerCase()) >= 0;
    }
});

//Animate.css wrapper function (adapted from animate.css README)

$.fn.extend({
    animateCss: function (animationName, animation_duration) {
        var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
        if (animation_duration){
            var dv = animation_duration + 'ms';
            var duration_props = {
                '-webkit-animation-duration': dv,
                '-moz-animation-duration': dv,
                '-o-animation-duration': dv,
                'animation-duration': dv
            };
            $(this).css(duration_props);
        }
        $(this).addClass('animated ' + animationName).one(animationEnd, function() {
            $(this).removeClass('animated ' + animationName);
            $(this).trigger("animatecss.finished");
        });
    }
});

// This function takes an element and stretches it to fit the page, expanding text to maximum size.

function fit_el_to_page(el) {
    var target_height =  window.innerHeight - $("NAV").outerHeight() - $("#meta").outerHeight();
    var numbreaks = $(el).find("br").size() +1;
    var target_width = window.innerWidth;
    var line_size = target_height / numbreaks;
    var font_size = line_size;
    //$(el).css("line-height", line_size+"px");
    $(el).css("white-space", "nowrap");
    $(el).css("font-size", font_size+"px");
    //The basic concept here is to shrink the text by 10% until the scrollwidth is less than the target width, and scrollheight likewise.
    //This would indicate a lack of scrollbars.
    while (($(el)[0].scrollWidth > target_width || $(el)[0].scrollHeight > target_height) && font_size > 12){
        font_size *= .9;
        $(el).css("font-size", font_size+"px");
        //console.log($(el).attr("id"), "W: ", $(el)[0].scrollWidth, target_width,"; H:",  $(el)[0].scrollHeight, target_height, '; F: ', font_size );
    }
    $(el).width("100%");
    $(el).height("100%");
}

// shortcut to disable or enable form elements
$.fn.extend({
    set_enabled: function(enable){
        if (enable){
            $(this).removeAttr("disabled");
        }else{
            $(this).attr("disabled", "disabled");
        }
    }
});

////////////////
// Components //
////////////////

var FormDialog = function(url, init_function, submit_function){
    // A popup dialog containing a form.

    var $fd = {};

    $fd.url = document.basepath.replace(/\/$/, '') + url;

    $fd.dialog_options = {
        width: "90%",
        modal: true
    };
    $fd.$dialog = $("#_dialog_");
    $fd.$dialog.hide();

    $fd.showform  = function(url_suffix){
        var url = url_suffix ? $fd.url + url_suffix : $fd.url;

        $.get(url, function(data){
            $fd.dialog_options.title = $(data).attr("title");
            $fd.$dialog.html(data).dialog($fd.dialog_options);
            $fd.form = $fd.$dialog.find("FORM");

            //common form initialization

            //Datetime inputs.
            var date_display_fmt = "m/d/yy";
            var time_display_fmt = "h:mm tt";

            $fd.form.find(":input.datepicker").each(
                function(i, el){
                    var $input = $(el);
                    var widget = $input.data("widget") + "picker";
                    var altfield_id = $input.data("altfield");
                    var dateval = $input.val()? new Date($input.val()) : null;

                    $input[widget]({
                        altField: "#" + altfield_id,
                        altFormat: "yy-mm-dd",
                        altTimeFormat: "HH:mm:ssz",
                        altSeparator: "T",
                        altFieldTimeOnly: false,
                        timeFormat: time_display_fmt,
                        dateFormat: date_display_fmt,
                        constrainInput: true,
                        showSecond: false,
                        showTimezone: false
                        //parse: 'loose'
                    });

                    $input[widget]('setDate', dateval);

                    //datetimepicker doesn't automatically clear the altField when its field is cleared.

                    $input.on("change", function(){
                        if ($input.val().trim() === ''){
                            $("#" + altfield_id).val('');
                        }
                    });
                });

            // Textareas to CKEDITOR
            $("TEXTAREA.ckedit").ckeditor();

            //custom init function

            if (init_function){
                init_function($fd.form);
            }

            //submit function

            if (submit_function){
                $fd.form.on("submit", function(e){
                    submit_function(e, $fd.form);
                });
            }
        });
    };//end show_form()

    return $fd;
};


var AnnouncementList = function(el, search_el){
    $al = $(el);
    $al.searchbox = $(search_el);

    if ($al.length === 0){
        return null;
    }

    $al.items = $al.find(".announcement_item");
    $al.edit_buttons = $al.find("BUTTON.edit");
    $al.preview_buttons = $al.find("BUTTON.preview");

    $al.searchbox.focus();

    $al.searchbox.keyup(function(){
        var term = $al.searchbox.val();
        if (term.length > 0){
            $al.items.hide();
            $al.items.filter(":containsi(" + term + ")").show();
        }else{
            $al.items.show();
        }
    });

    $al.edit_buttons.on("click", function(e){
        e.preventDefault();
        var id = $(this).closest("li").data("id");
        document.edit_form.showform("/" + id);
        return false;
    });

    $al.preview_buttons.on("click", function(e){
        e.preventDefault();
        var id = $(this).closest("li").data("id");
        window.open(document.basepath.replace(/\/$/, '') + "/preview/" + id);
        return false;
    });

    return $al;
};


var AnnouncementDisplay = function(el, source_url){
    var $ad = $(el);
    if ($ad.length === 0){
        $("#back_slide").set_enabled(false);
        $("#advance_slide").set_enabled(false);
        return null;
    }else{
        $("#back_slide").set_enabled(true);
        $("#advance_slide").set_enabled(true);
    }

    $ad.init = function(){
        $ad.slides = $ad.find(".announcement_display");
        $ad.slides.each(function(i, el){
            fit_el_to_page(el);
        });
        $ad.old_slide = $ad.slides.last();
        $ad.slides.hide();
        $ad.old_slide.show();
        $ad.slide = $ad.slides.first();
        if ($ad.slide.length > 0){
            $ad.show_slide();
        }
    };

    $ad.refresh_slides = function(){
        $.get(
            document.basepath.replace(/\/$/, '') + "/slides",
            function(data){
                $ad.html(data);
                $ad.init();
            }).fail(function(){
                setTimeout($ad.refresh_slides, 10000);
            });
    };

    $ad.show_slide = function(){
        var duration = parseInt($ad.slide.data("duration"), 10) * 1000;
        var transition = $ad.slide.data("transition");
        var transition_time = parseInt(Transition_Time, 10) || 500; // milliseconds

        //set title
        $("#title").html($ad.slide.data("title"));
        //set meta info
        meta_text = (Show_Updated ? ("Updated " + $ad.slide.data("updated") + ' ') : ' ') +
            (Show_Author ? ("By " + $ad.slide.data("author")) : '');
        $("#meta").html(meta_text);

        //hide the slides and show the new one.
        //$ad.slides.hide();
        if ($ad.old_slide){
            $ad.old_slide.css({'z-index': 0});
        }
        $ad.slide.css({'z-index': 100, 'top': 0});
        if (transition && transition_backend === 'animatecss'){
            $ad.slide.show();
            $ad.slide.animateCss(transition, transition_time);
            $ad.slide.one('animatecss.finished', function(){
                $ad.old_slide.hide();
            });
        }else if (transition && transition_backend === 'jquery-ui'){
            $ad.slide.show({
                effect: transition,
                duration: transition_time,
                complete: function(){ $ad.old_slide.hide(); }
            });
        }else{
            $ad.slide.show();
            $ad.old_slide.hide();
        }

        //set the timer for moving to the next slide
        if ($ad.advance_timeout){
            clearTimeout($ad.advance_timeout);
        }
        $ad.advance_timeout = setTimeout($ad.advance_slide, duration);
    };

    $ad.advance_slide = function(){
        $ad.old_slide = $ad.slide;
        $ad.slide = $ad.slide.next();
        if ($ad.slide.length === 0){
            $ad.refresh_slides();
        }else{
            $ad.show_slide();
        }
    };
    $ad.back_slide = function(){
        $ad.slide = $ad.slide.prev();
        if ($ad.slide.length === 0){
            $ad.refresh_slides();
        }else{
            $ad.show_slide();
        }
    };

    $(document).on("click", '#advance_slide', $ad.advance_slide);
    $(document).on("click", "#back_slide", $ad.back_slide);

    $ad.init();

    return $ad;
};

/////////////////////////////
// Document initialization //
/////////////////////////////

$(document).ready(function(){

    //Settings form
    document.settings_form = FormDialog(
        "/settings",
        null,
        function(e, form){
            e.preventDefault();
            var data = $(form).serialize();
            $.post(
                $(form).attr("action"),
                data,
                function(){
                    $("#_dialog_").dialog("close");
                }
            );
        });

    //DB init form
    document.initialize_db_form = FormDialog(
        "/initialize",
        //init function
        function(form){
            var $submit_btn = form.find("input[type=submit]");
            $submit_btn.set_enabled(false);
            form.find("#init_db").on("change", function(){
                $submit_btn.set_enabled($(this).is(":checked"));
            });
        },
        //submit function
        function(e, form){
            e.preventDefault();
            var location = window.location;
            var formdata = form.serialize();
            $.post(
                form.attr("action"),
                formdata,
                function(){
                    window.location = location;
                    window.location.reload();
                }
            );
        });

    //Announcement editing

    document.edit_form  = FormDialog(
        "/edit",
        //init function
        function(form){
            form.on('change', 'input[name=fg_color],input[name=bg_color]', function(e){
                //make the CKEDITOR reflect the changes.
                var editor_doc = CKEDITOR.instances.announcement_content_textarea.document.getBody()["$"];
                var $this = $(this);
                if ($this.attr("name") === "fg_color"){
                    editor_doc.style["color"] = $this.val();
                }else{
                    editor_doc.style["background-color"] = $this.val();
                }
            });

            form.on('change', 'input[name=delete]', function(e){
                var $delcb = $(this);

                if ($delcb.is(':checked')){
                    form.find(':input:not([type=hidden],[name=delete],[type=submit])').each(function(i, el){
                        $(el).set_enabled(false);
                    });
                }else{
                    form.find(':input').each(function(i, el){
                        $(el).set_enabled(true);
                    });
                }
            });

            $.when(form.find(".ckedit").ckeditor().promise).then(
                function(){
                    form.find("input[type=color]").each(function(i, el){
                        $(el).trigger("change");
                    });
                });
        });

    //cleaning expired

    document.clean_expired_form = FormDialog(
        "/clean_expired",
        null,
        function(e, form){
            e.preventDefault();
            form.find('input[type=submit]').set_enabled(false);
            form.find('input[type=submit]').attr("value", 'Please wait...');
            $.post(form.attr("action"), null, function(){
                window.location.reload();
            });
        }
    );

    //Buttons!

    $("#new_announcement A").on("click", function(){document.edit_form.showform();});
    $("#link_settings A").on("click", function(){document.settings_form.showform();});
    $("#link_initialize A").on("click", function(){document.initialize_db_form.showform();});
    $("#link_clean_expired A").on("click", function(){document.clean_expired_form.showform();});

    //The announcment list

    document.announcement_list = AnnouncementList("#announcement_list", "#search");

    //announcement display

    document.announcement_display = AnnouncementDisplay("#announcements");

});//End document.ready()
