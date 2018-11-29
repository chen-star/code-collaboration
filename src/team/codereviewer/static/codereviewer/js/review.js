var csrftoken="";
var last_update_time;
var linesWithComment=new Set();
var openLines=new Set();
var file_id;
function show(id) {
  document.getElementById(id).style.visibility = "visible";
}
function hide(id) {
  document.getElementById(id).style.visibility = "hidden";
}
function populateCode(file_id){
    var jqXHR = $.get("/codereviewer/get-codes/"+file_id)
      .done(function(data){
        linesWithComment = (data.commented_lines);
        var list = $('#code-block');
        list.html('');
        var html='<pre>';
        for (var i = 0; i < data.codes.length; i++) {
              var new_line = (data.codes[i]);
              html+=('<code class="hljs" id="code-'+i+'"><a onMouseOver="show(\'guide-'+i+'\')" onMouseOut="hide(\'guide-'+i+'\')">'+new_line+'<span id="guide-'+i+'" style="visibility:hidden;font-style: italic;"> # click to comment</span></code></a>');
              html+="<span class='cmt-block-span' id='cmt-span-"+i+"'><table><tbody><tr><th><label for='id_commentcontent'>Comments... </label></th><td><input type='text' name='commentcontent' required id='id_commentcontent_"+i+"'><a id='"+i+"' type='submit' class='cmt-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Comment</a>\
              <div id='popUp-"+i+"' style='display: none;'>   You have successfully sent the comment! </div>\
              </td></tr></tbody></table><div id='cmt-list-"+i+"'></div></span>";

          }
          html+=('</pre>');
          list.append(html);
      })
      .fail(function(jqXHR, textStatus, errorThrown){
        var list = $('#code-block');
        list.append("<h4>We're sorry. There is something wrong when opening the files.</h4>");
        list.append("<h5>"+errorThrown+"</h5>");
      });

}
//click to expand cmt-span block
$(document).on("click", ".hljs", function(event){
  var file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
  var line_num=this.id.substr(5);
    $header = $(this);
    //getting the next element
    $content = $header.next();

    //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
    $content.slideToggle(400);
    if(openLines.has(line_num)){
      openLines.delete(line_num);
    }else{
      openLines.add(line_num);
    }
    console.log(openLines);
    clickOnLine(file_id,line_num);

});

function clickOnLine(file_id,line_num){
  var list = $('#cmt-list-'+line_num);
  list.html('');
  $.get("/codereviewer/get-comments/"+file_id+"/"+line_num)
    .done(function(data){
      user = (data.current_user);
      for (var i=0;i<data.comments.length;i++){
        var line_num = data.comments[i].line_num;
        var s = "<hr>"+(data.comments[i].html);
        s+="<table><tbody><tr><th><label for='id_replycontent'>  reply... </label></th><td><input type='text' name='replycontent' required id='id_replycontent_reply-"+data.comments[i].id+"'>";
        if(user==data.comments[i].commenter){
          s+="<a id='"+line_num+"-delete-"+data.comments[i].id+"' type='submit' class='delete-cmt-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Delete</a>";
          s+="<a id='"+line_num+"-reply-"+data.comments[i].id+"' type='submit' class='reply-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Reply</a></td></tr></tbody></table></div>";
        }else{
          s+="<a id='"+line_num+"-reply-"+data.comments[i].id+"' type='submit' class='reply-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Reply</a></td></tr></tbody></table></div>";
        }
        for(var j=0;j<data.comments[i].replies.length;j++){
          s+=data.comments[i].replies[j].html;
        }
        list.append(s);
      }
    });
}
//click to expand all cmt-span block
$(document).on("click", ".badge-dark", function(event){
  event.preventDefault();
  text = this.text;
  if(text=="Show All Comments"){
    // open
    this.text="Close All";
    var file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
    for(var i=0;i<linesWithComment.length;i++){
      var line_num=linesWithComment[i];
      openLines.add(line_num);
      $("#cmt-span-"+line_num).slideDown(400);
      clickOnLine(file_id,line_num);
    }
    console.log(openLines);
  }else{
    // close
    this.text="Show All Comments";
    for(var i=0;i<linesWithComment.length;i++){
      var line_num=linesWithComment[i];
      $("#cmt-span-"+line_num).slideUp(400);
      openLines.delete(line_num);
    }
    // TODO close other lines
      for(var i=0;i<openLines.length;i++){
        var line_num=openLines[i];
        $("#cmt-span-"+line_num).slideUp(400);
      }
      // openLines=new Set();

  }


});

// update time
function updateTime(){
  date = new Date();
  last_update_time = date.getTime();
}
// update opened lines
function getUpdates(){
  console.log(openLines.length);
  for(var i=0;i<openLines.length;i++){
    var line_num=openLines[i];
    console.log(line_num+", "+last_update_time);
    $.get("/codereviewer/get-changes/"+file_id+"/"+line_num+"/"+last_update_time)
      .done(function(data) {
        var list = $('#cmt-list-'+line_num);
        user = (data.current_user);
        for (var i=0;i<data.comments.length;i++){
          var line_num = data.comments[i].line_num;
          var s = (data.comments[i].html);
          s+="<table><tbody><tr><th><label for='id_replycontent'>  reply... </label></th><td><input type='text' name='replycontent' required id='id_replycontent_reply-"+data.comments[i].id+"'>";
          if(user==data.comments[i].commenter){
            s+="<a id='"+line_num+"-delete-"+data.comments[i].id+"' type='submit' class='delete-cmt-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Delete</a>";
            s+="<a id='"+line_num+"-reply-"+data.comments[i].id+"' type='submit' class='reply-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Reply</a></td></tr></tbody></table></div><hr>";
          }else{
            s+="<a id='"+line_num+"-reply-"+data.comments[i].id+"' type='submit' class='reply-btn' style='-webkit-appearance: initial;color:darkgrey;'>  Reply</a></td></tr></tbody></table></div><hr>";
          }
          for(var j=0;j<data.comments[i].replies.length;j++){
            s+=data.comments[i].replies[j].html;
          }
          list.append(s);
          // add reply
        }
      });
  }

     updateTime();
}

$(document).ready(function() {

 file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);

 var linesWithComment=new Set();
 var openLines=new Set();
  console.log(file_id);
  populateCode(file_id);
  $.getScript('https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.13.1/highlight.min.js')
    .done(function(data, textStatus, jqxhr){
      $('pre code').each(function(i, block) {
  hljs.highlightBlock(block);
});
  })
  .fail(function( jqxhr, settings, exception ) {
    console.log(exception);
});

  updateTime();
  window.setInterval(getUpdates, 5000);
  // CSRF set-up copied from Django docs
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
csrftoken = getCookie('csrftoken');
// alert(csrftoken);
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
  }
});

});
// click send comment button
$(document).on("click", ".cmt-btn", function(event){
  // alert(csrftoken);
  event.preventDefault();
  file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
  selector = "#id_commentcontent_"+this.id;
  line_num=this.id;
  if($(selector).val()===null ||$(selector).val()===""){
    alert("Please enter comment!");
  }else{
    $.post("/codereviewer/add-comment", {
      'commentcontent':$(selector).val(),
      'file_id':file_id,
      "line_num":line_num
    })
      .done(function(data) {
          console.log("sent cmt");
          var cmt_list = $("#cmt-list-"+this.id);
          // populateList();
          $(selector).val('');
          linesWithComment.push(line_num);
          clickOnLine(file_id,line_num);
          $( "#popUp-"+line_num ).show();
          console.log("here!!");
          setTimeout(function() {
            $( "#popUp-"+line_num ).hide();
          }, 2000);
      });
  }

});
// click send reply button
$(document).on("click", ".reply-btn", function(event){
  // alert(csrftoken);
  event.preventDefault();
  file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);

  line_num=this.id.substring(0,this.id.indexOf('-'));
  comment_id=this.id.substring(this.id.indexOf('-')+1);
  selector = "#id_replycontent_"+comment_id;
  if($(selector).val()===null ||$(selector).val()===""){
    alert("Please enter comment!");
  }else{
    $.post("/codereviewer/add-reply", {
      'replycontent':$(selector).val(),
      'comment_id':comment_id
    })
      .done(function(data) {
          console.log("sent reply");
          // update comment reply list;
          $(selector).val('');
          clickOnLine(file_id,line_num);
      });
  }

});

// click delete comment reply button
$(document).on("click", ".delete-cmt-btn", function(event){
  // alert(csrftoken);
  event.preventDefault();
  file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
  line_num=this.id.substring(0,this.id.indexOf('-'));
  comment_id=this.id.substring(this.id.lastIndexOf('-')+1);
  $.post("/codereviewer/delete-comment", {
    'comment_id':comment_id
  })
    .done(function(data) {
        console.log("delete reply");
        clickOnLine(file_id,line_num);
    });
});
