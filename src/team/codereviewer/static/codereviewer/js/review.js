var csrftoken="";
var linesWithComment=[];
function populateCode(file_id){
    var jqXHR = $.get("/codereviewer/get-codes/"+file_id)
      .done(function(data){
        linesWithComment = (data.commented_lines);
        var list = $('#code-block');
        list.html('');
        var html='<pre>';
        for (var i = 0; i < data.codes.length; i++) {
              var new_line = (data.codes[i]);
              // console.log(new_line);
              html+=('<code class="java hljs" id="code-'+i+'">'+new_line+'</code>');
              html+="<span class='cmt-block-span' id='cmt-span-"+i+"'><table><tbody><tr><th><label for='id_commentcontent'>Comments... </label></th><td><input type='text' name='commentcontent' required id='id_commentcontent_"+i+"'><button id='"+i+"' type='submit' class='btn btn-success cmt-btn' style='padding: 4px 4px;font-size: 12px;'>Comment</button></td></tr>\
                    </tbody></table><hr><div id='cmt-list-"+i+"'></div></span>";

          }
          html+=('</pre>');
          list.append(html);
      })
      .fail(function(jqXHR, textStatus, errorThrown){
        console.log(errorThrown);
      });
      $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
        console.log("here");
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
    clickOnLine(file_id,line_num);

});

function clickOnLine(file_id,line_num){
  var list = $('#cmt-list-'+line_num);
  list.html('');
  $.get("/codereviewer/get-comments/"+file_id+"/"+line_num)
    .done(function(data){
      for (var i=0;i<data.comments.length;i++){
        var line_num = data.comments[i].line_num;
        var s = (data.comments[i].html);
        s+="<table><tbody><tr><th><label for='id_replycontent'>  reply... </label></th><td><input type='text' name='replycontent' required id='id_replycontent_reply-"+data.comments[i].id+"'>";
        s+="<button id='"+line_num+"-reply-"+data.comments[i].id+"' type='submit' class='btn btn-success reply-btn' style='padding: 4px 4px;font-size: 12px;'>Send</button></td></tr></tbody></table></div><hr>";
        for(var j=0;j<data.comments[i].replies.length;j++){
          s+=data.comments[i].replies[j].html;
        }
        list.append(s);
        // add reply
      }
    });
}
//click to expand all cmt-span block
$(document).on("click", ".badge-dark", function(event){
  event.preventDefault();
  text = this.text;
  if(text=="Show All Comments"){
    this.text="Close All";
    var file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
    for(var i=0;i<linesWithComment.length;i++){
      var line_num=linesWithComment[i];
      $("#cmt-span-"+line_num).slideDown(400);
      clickOnLine(file_id,line_num);
    }
  }else{
    this.text="Show All Comments";
    for(var i=0;i<linesWithComment.length;i++){
      var line_num=linesWithComment[i];
      $("#cmt-span-"+line_num).slideUp(400);}
  }


});

$(document).ready(function() {
  var file_id=window.location.href.substr(window.location.href.lastIndexOf('/')+1);
 //  $.getScript("/codereviewer/js/highlight.pack.js", function() {
 //   alert("Script loaded but not necessarily executed.");
 //
 // });

  console.log(file_id);
  populateCode(file_id);

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
          linesWithComment.add(line_num);
          clickOnLine(file_id,line_num);
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
